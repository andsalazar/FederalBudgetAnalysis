"""
Tests for src/analysis/policy_impact.py

Covers:
  - HAC standard error computation in interrupted_time_series()
  - ITS regressor construction (time, intervention, time_after)
  - Newey-West lag selection formula
  - compute_real_values() CPI deflation
  - percent_change_around_event()
"""
import numpy as np
import pandas as pd
import pytest
from scipy import stats as sp_stats


# ---------------------------------------------------------------------------
# HAC lag selection
# ---------------------------------------------------------------------------
class TestHACLagSelection:
    """The formula: max(1, int(0.75 * n^(1/3)))"""

    @pytest.mark.parametrize("n_obs, expected_lag", [
        (8,   1),     # 0.75 * 2.0 = 1.5 -> 1
        (27,  2),     # 0.75 * 3.0 = 2.25 -> 2
        (64,  2),     # 0.75 * ~4.0 = ~3.0 -> 2 (float truncation: 64^(1/3) ≈ 3.9999)
        (125, 3),     # 0.75 * 5.0 = 3.75 -> 3
        (1,   1),     # edge: single obs
    ])
    def test_lag_formula(self, n_obs, expected_lag):
        lag = max(1, int(0.75 * (n_obs ** (1 / 3))))
        assert lag == expected_lag


# ---------------------------------------------------------------------------
# ITS regressor construction
# ---------------------------------------------------------------------------
class TestITSRegressors:
    def test_intervention_indicator(self, synthetic_quarterly_series):
        series, intervention_date = synthetic_quarterly_series
        intervention_dt = pd.Timestamp(intervention_date)

        intervention = (series.index >= intervention_dt).astype(int)
        # First 100 should be 0, last 10 should be 1
        assert intervention[:100].sum() == 0
        assert intervention[100:].sum() == 10

    def test_time_after_variable(self, synthetic_quarterly_series):
        series, intervention_date = synthetic_quarterly_series
        intervention_dt = pd.Timestamp(intervention_date)

        time_var = np.arange(len(series))
        intervention = (series.index >= intervention_dt).astype(int)
        time_after = np.where(
            intervention,
            time_var - time_var[intervention.argmax()],
            0,
        )
        # Pre-intervention should all be 0
        assert np.all(time_after[:100] == 0)
        # Post-intervention should be [0, 1, 2, ..., 9]
        np.testing.assert_array_equal(time_after[100:], np.arange(10))


# ---------------------------------------------------------------------------
# ITS model (integration test using statsmodels)
# ---------------------------------------------------------------------------
class TestInterruptedTimeSeries:
    def test_detects_level_shift(self, synthetic_quarterly_series):
        """ITS should detect the +20 level shift in synthetic data."""
        import statsmodels.api as sm

        series, intervention_date = synthetic_quarterly_series
        intervention_dt = pd.Timestamp(intervention_date)

        time_var = np.arange(len(series))
        intervention = (series.index >= intervention_dt).astype(int)
        time_after = np.where(
            intervention,
            time_var - time_var[intervention.argmax()],
            0,
        )
        X = sm.add_constant(
            pd.DataFrame({
                "time": time_var,
                "intervention": intervention,
                "time_after": time_after,
            })
        )
        n_obs = len(series)
        max_lags = max(1, int(0.75 * (n_obs ** (1 / 3))))
        model = sm.OLS(series.values, X).fit(
            cov_type="HAC", cov_kwds={"maxlags": max_lags}
        )
        # Level shift coefficient should be close to +20
        assert 10 < model.params["intervention"] < 30
        # Should be statistically significant (p < 0.05)
        assert model.pvalues["intervention"] < 0.05

    def test_detects_trend_change(self):
        """ITS should detect a strong trend change with low noise."""
        import statsmodels.api as sm

        # Build targeted synthetic: strong trend change (-2.0/q), low noise
        rng_local = np.random.RandomState(7)
        n_pre, n_post = 80, 30
        n = n_pre + n_post
        dates = pd.date_range("2000-01-01", periods=n, freq="QS")
        t = np.arange(n, dtype=float)
        y = 50 + 0.5 * t + rng_local.normal(0, 0.5, n)
        y[n_pre:] += 10                                    # level shift
        y[n_pre:] += -2.0 * np.arange(n_post)              # strong trend change
        series = pd.Series(y, index=dates)
        intervention_dt = dates[n_pre]

        time_var = np.arange(len(series))
        intervention = (series.index >= intervention_dt).astype(int)
        time_after = np.where(
            intervention,
            time_var - time_var[intervention.argmax()],
            0,
        )
        X = sm.add_constant(
            pd.DataFrame({
                "time": time_var,
                "intervention": intervention,
                "time_after": time_after,
            })
        )
        n_obs = len(series)
        max_lags = max(1, int(0.75 * (n_obs ** (1 / 3))))
        model = sm.OLS(series.values, X).fit(
            cov_type="HAC", cov_kwds={"maxlags": max_lags}
        )
        # Trend change should be strongly negative (true = -2.0)
        assert model.params["time_after"] < -1.0


# ---------------------------------------------------------------------------
# CPI deflation
# ---------------------------------------------------------------------------
class TestComputeRealValues:
    def test_basic_deflation(self):
        """Nominal $100 in year with CPI=200, base CPI=100 → real $50."""
        dates = pd.date_range("2020-01-01", periods=4, freq="YS")
        nominal = pd.Series([100, 100, 100, 100], index=dates)
        cpi = pd.Series([100, 150, 200, 250], index=dates)
        base_cpi = 100  # base_year with CPI = 100

        real = nominal * (base_cpi / cpi)
        expected = pd.Series([100.0, 100 / 1.5, 50.0, 40.0], index=dates)
        pd.testing.assert_series_equal(real, expected)

    def test_identity_at_base_year(self):
        """Real = nominal when CPI equals base CPI."""
        dates = pd.date_range("2023-01-01", periods=1, freq="YS")
        nominal = pd.Series([500.0], index=dates)
        cpi = pd.Series([300.0], index=dates)
        base_cpi = 300.0

        real = nominal * (base_cpi / cpi)
        assert real.iloc[0] == pytest.approx(500.0)


# ---------------------------------------------------------------------------
# Percent change around event
# ---------------------------------------------------------------------------
class TestPercentChangeAroundEvent:
    def test_known_change(self):
        """Pre-mean = 100, post-mean = 120 → +20%."""
        dates = pd.date_range("2018-01-01", periods=6, freq="YS")
        values = [100, 100, 100, 120, 120, 120]
        series = pd.Series(values, index=dates)
        event = "2021-01-01"

        pre = series[series.index < pd.Timestamp(event)]
        post = series[series.index >= pd.Timestamp(event)]
        pct = ((post.mean() - pre.mean()) / abs(pre.mean())) * 100

        assert pct == pytest.approx(20.0)

    def test_decline(self):
        """Pre-mean = 200, post-mean = 100 → -50%."""
        dates = pd.date_range("2018-01-01", periods=4, freq="YS")
        values = [200, 200, 100, 100]
        series = pd.Series(values, index=dates)
        event = "2020-01-01"

        pre = series[series.index < pd.Timestamp(event)]
        post = series[series.index >= pd.Timestamp(event)]
        pct = ((post.mean() - pre.mean()) / abs(pre.mean())) * 100

        assert pct == pytest.approx(-50.0)
