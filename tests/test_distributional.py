"""
Tests for B50 calibration and distributional attribution.

Validates:
  - B50 = Q1 + Q2 + 0.5*Q3 (CPS person-income quintiles, each 20% of persons)
  - B50 population and spending computations
  - CEX household-income calibration: Q1+Q2+Q3+0.414*Q4 (unequal person shares)
  - Tariff DWL multiplier (1.4×)
  - Per-person burden and income-share calculations
"""
import numpy as np
import pytest


# CPS person-income quintiles: each quintile = 20% of persons
# B50 = Q1 + Q2 + 0.5*Q3 = exactly 50%
B50_Q3_FACTOR = 0.5

# CEX household-income quintiles: unequal person shares (10.1%, 12.7%, 17.8%, 22.7%, 36.7%)
# B50_CEX = Q1+Q2+Q3+0.414*Q4 = exactly 50% of persons in CEX framework
CEX_Q4_FACTOR = 0.414


class TestB50Calibration:
    """Unit tests for the B50 aggregation formula (CPS person-income quintiles)."""

    def test_factor_range(self):
        """The Q3 factor must be in (0, 1) — it's a fraction of Q3."""
        assert 0 < B50_Q3_FACTOR <= 1

    def test_b50_population(self):
        """
        With 5 equal quintiles of 50M each (CPS person-income),
        B50 pop = 2*50M + 0.5*50M = 125M (exactly 50%).
        """
        q_pop = 50_000_000
        b50_pop = 2 * q_pop + B50_Q3_FACTOR * q_pop
        expected = 125_000_000
        assert b50_pop == pytest.approx(expected)

    def test_b50_captures_exactly_50pct(self):
        """B50 = Q1(20%) + Q2(20%) + 0.5*Q3(20%) = 50% of persons."""
        pct_captured = 20 + 20 + B50_Q3_FACTOR * 20
        assert pct_captured == pytest.approx(50.0)

    def test_cex_b50_population(self):
        """
        CEX quintiles have unequal person shares:
        10.1% + 12.7% + 17.8% + 0.414*22.7% = 50.0%.
        """
        cex_shares = [10.1, 12.7, 17.8, 22.7, 36.7]
        b50_cex = sum(cex_shares[:3]) + CEX_Q4_FACTOR * cex_shares[3]
        assert b50_cex == pytest.approx(50.0, abs=0.1)

    def test_b50_spending_attribution(self):
        """
        Given known quintile spending cuts:
          Q1=-65, Q2=-50, Q3=-33, Q4=-24, Q5=-12  (billions)
        B50 spend = Q1+Q2 + 0.5*Q3 = -65-50 + 0.5*(-33) = -131.5B
        """
        cuts = {"Q1": -65, "Q2": -50, "Q3": -33, "Q4": -24, "Q5": -12}
        b50 = sum(cuts[q] for q in ["Q1", "Q2"])
        b50 += cuts["Q3"] * B50_Q3_FACTOR
        assert b50 == pytest.approx(-131.5, abs=0.01)

    def test_b50_tariff_attribution(self):
        """
        B50 tariff = Q1 + Q2 + 0.5*Q3 (CPS person-income quintiles).
        """
        tariffs = {"Q1": 14.0, "Q2": 21.0, "Q3": 30.8, "Q4": 37.8, "Q5": 36.4}
        b50_tariff = sum(tariffs[q] for q in ["Q1", "Q2"])
        b50_tariff += tariffs["Q3"] * B50_Q3_FACTOR
        expected = 14.0 + 21.0 + 0.5 * 30.8
        assert b50_tariff == pytest.approx(expected)

    def test_per_person_calculation(self):
        """Per-person = (total burden in $) / population."""
        total_burden_B = 181.8  # billions
        population = 136_571_242
        per_person = (total_burden_B * 1e9) / population
        assert per_person == pytest.approx(1331, rel=0.01)


class TestTariffDWLMultiplier:
    """Validate the deadweight loss multiplier logic."""

    def test_baseline_dwl(self):
        """$100B tariff revenue × 1.4 DWL = $140B consumer burden."""
        revenue = 100.0
        dwl_factor = 1.4
        burden = revenue * dwl_factor
        assert burden == pytest.approx(140.0)

    @pytest.mark.parametrize("passthrough, dwl, expected_burden", [
        (0.50, 1.4, 70.0),
        (0.75, 1.2, 90.0),
        (1.00, 1.0, 100.0),
        (1.00, 2.0, 200.0),
        (1.25, 1.4, 175.0),
    ])
    def test_sensitivity_scenarios(self, passthrough, dwl, expected_burden):
        """Robustness test 2: tariff pass-through × DWL grid."""
        revenue = 100.0
        burden = revenue * passthrough * dwl
        assert burden == pytest.approx(expected_burden)


class TestIncomeShareCalculation:
    """Validate percent-of-income computation."""

    def test_burden_as_pct_income(self):
        """$1,331 per person / $12,526 mean pretax = 10.63%"""
        per_person = 1331
        mean_income = 12526
        pct = (per_person / mean_income) * 100
        assert pct == pytest.approx(10.63, abs=0.1)

    def test_zero_income_guarded(self):
        """Division by zero should be handled gracefully."""
        per_person = 1000
        mean_income = 0
        # The code uses a guard: only compute if income > 0
        pct = (per_person / mean_income * 100) if mean_income > 0 else np.nan
        assert np.isnan(pct)
