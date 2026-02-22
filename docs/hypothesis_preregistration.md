# Pre-Registered Hypothesis

**Date registered:** February 20, 2026
**Status:** POST-ANALYSIS — Data collected and analysis completed (February 21, 2026)

> **Note:** This document was written before data collection. Results are
> reported in [`output/FINDINGS.md`](../output/FINDINGS.md). The verdicts
> below were added post-analysis and are clearly marked.

---

## Master Hypothesis (H₁)

**The bottom 50% of U.S. taxpayers experienced a net welfare loss in 2025 as a direct result of federal economic policy changes, while the top income groups (particularly asset holders and bondholders) captured a disproportionate share of the benefits.**

---

## Sub-Hypotheses & Assumptions

### H1a: Social Program Cuts Hit the Bottom 50% Disproportionately
**Claim:** Federal spending cuts in 2025 disproportionately targeted programs that serve the bottom 50% of earners (e.g., Medicaid, SNAP, housing assistance, education grants, child tax credits, ACA subsidies).

**Testable predictions:**
- Spending on means-tested programs declined in 2025 relative to 2024 baseline
- The dollar value of cuts to bottom-50%-serving programs exceeds cuts to programs serving upper-income groups
- Per-capita benefit reductions are larger for lower-income households

**Key data needed:**
- Federal outlays by function/subfunction (BEA NIPA Table 3.2, Monthly Treasury Statement)
- CBO distribution of federal spending by income quintile
- Program-level appropriations (SNAP, Medicaid, Section 8, Pell Grants, EITC/CTC)

**Verdict (post-analysis):** ✅ **SUPPORTED.** FY2025 outlays fell $188B below CBO
baseline, concentrated in Medicaid (−$36B), income security (−$53B), and
nondefense discretionary (−$95B). The B50 bears $157.6B of the $188B spending
gap. See FINDINGS §4 and §6.

---

### H1b: Effective Tax Burden Shifted Toward the Bottom 50%
**Claim:** Policy changes in 2025 increased the effective tax burden on the bottom 50% of earners, either through direct tax changes, expiration of credits, or indirect taxation.

**Testable predictions:**
- Effective tax rates for the bottom two quintiles increased in 2025
- Tax credits benefiting lower earners (EITC, CTC) were reduced or restricted
- Upper-income tax cuts reduced effective rates for the top quintiles

**Key data needed:**
- CBO Distribution of Household Income (effective tax rates by quintile)
- IRS Statistics of Income (tax liability by AGI bracket)
- Legislative changes to EITC, CTC, standard deduction

**Verdict (post-analysis):** ⚠️ **PARTIALLY TESTED.** Tariff revenue ($195B,
+153% YoY) functions as a regressive consumption tax (see H1c). Direct
income-tax rate changes not independently identifiable in FY2025 data yet.
See FINDINGS §6.

---

### H1c: Tariffs Function as a Regressive Tax on the Bottom 50%
**Claim:** Tariffs imposed in 2025 raised consumer prices on goods that constitute a larger share of spending for lower-income households, functioning as a regressive consumption tax.

**Testable predictions:**
- CPI increased faster for categories with high tariff exposure (food, clothing, electronics, household goods)
- Lower-income households spend a higher share of income on tariff-affected goods
- Tariff revenue increased while consumer surplus decreased (deadweight loss)
- Price pass-through to consumers exceeded 50% of tariff costs

**Key data needed:**
- CPI by category (BLS: food, apparel, household furnishings, etc.)
- Consumer Expenditure Survey (spending shares by income quintile)
- Tariff schedule changes and affected HTS codes
- Import price indices

**Verdict (post-analysis):** ✅ **SUPPORTED.** High-tariff goods CPI +2.30pp vs.
−1.46pp for low-tariff goods (Spearman ρ = 0.684, p = 0.020). The B50 bears
58.1% of tariff burden despite holding 23.0% of income. DWL multiplier ≈ 1.4×.
See FINDINGS §6, Tables 7–10.

---

### H1d: Deficit Spending & Debt Financing Benefit Bondholders at the Bottom 50%'s Expense
**Claim:** The federal deficit increased in 2025. The cost of servicing that debt (interest payments) flows to bondholders—who are overwhelmingly in the top income brackets—while the future debt burden falls on all taxpayers, with regressive effects.

**Testable predictions:**
- Federal deficit (nominal and as % of GDP) increased in FY2025 vs FY2024
- Net interest payments as a share of federal spending increased
- Treasury bond holders are concentrated in the top income quintiles (and institutional/foreign holders)
- Future debt service crowds out spending on programs serving the bottom 50%

**Key data needed:**
- Federal deficit data (FRED: FYFSD, Monthly Treasury Statement)
- Net interest on federal debt (FRED, Treasury)
- Treasury ownership distribution (Federal Reserve Flow of Funds, TreasuryDirect)
- CBO long-term budget projections showing interest vs. discretionary spending

**Verdict (post-analysis):** ✅ **SUPPORTED.** Interest/safety-net ratio reached
0.91 in FY2025 (z = 2.4 above trend). Net interest now exceeds defense spending.
Structural break test significant at 5% level. See FINDINGS §3.4, Table 1d.

---

### H1e: Tax Cuts & Tariff Revenue Benefits Flow to Shareholders
**Claim:** Corporate tax cuts and any tariff-related revenue recycling (rebates, subsidies to domestic producers) primarily benefit shareholders and capital owners, who are disproportionately in the top income brackets.

**Testable predictions:**
- Corporate tax revenue declined in 2025
- Corporate profits and/or stock buybacks increased
- Stock market gains (S&P 500) concentrated among top-quintile households
- Any tariff-related industry subsidies flowed to corporations, not consumers

**Key data needed:**
- Corporate tax receipts (FRED, Treasury)
- Corporate profits (BEA NIPA)
- Stock market performance (S&P 500, sector-level)
- Stock ownership distribution by income (Federal Reserve SCF)
- Any enacted tariff rebate/subsidy programs

---

## Visualization Plan: "Where Did the Money Go?"

### Primary visualization: Sankey/flow diagram showing value transfer

```
SOURCES (Government Revenue & Cuts)          DESTINATIONS (Who Benefits/Loses)
─────────────────────────────────           ──────────────────────────────────
Tax revenue from bottom 50%    ──────┐
                                     ├──→  Interest payments → Bondholders (top quintiles)
Tariff revenue (paid by consumers) ──┤
                                     ├──→  Corporate tax cuts → Shareholders (top quintiles)
Social program cuts ─────────────────┤
                                     ├──→  Defense/other spending → Contractors/employees
Deficit increase (future burden) ────┤
                                     └──→  Net loss: Bottom 50% (reduced benefits + higher prices)
```

### Supporting visualizations:
1. **Stacked bar: Federal spending by function** — 2024 vs 2025, highlighting shifts
2. **Waterfall chart: Bottom-50% welfare accounting** — Starting from 2024 baseline, showing each policy channel's additive/subtractive impact
3. **Distributional bar chart:** Net fiscal impact by income quintile (taxes paid minus benefits received)
4. **Time series with policy markers:** Key welfare indicators (real disposable income, CPI, program enrollment) with 2025 policy dates marked
5. **Dual-axis chart:** Deficit/interest payments growing alongside social program spending declining

---

## Analytical Approach

### Phase 1: Data Collection
- FRED economic indicators (16+ series already configured)
- Treasury Fiscal Data (monthly receipts, outlays, debt)
- CBO historical budget and distributional data
- BLS Consumer Price Index by category
- Federal Reserve Survey of Consumer Finances (asset ownership by income)

### Phase 2: Baseline Construction
- Establish 2024 (pre-policy) baseline for all indicators
- Use CBO projections as counterfactual ("what would have happened without policy changes")

### Phase 3: Impact Estimation
- Interrupted time series around each 2025 policy implementation date
- Distributional incidence analysis (who bears the burden of each policy)
- Partial equilibrium tariff welfare analysis (consumer surplus, producer surplus, government revenue, deadweight loss)

### Phase 4: Synthesis & Visualization
- Aggregate all channels into net welfare impact by income group
- Build the "Where Did the Money Go?" flow visualization
- Sensitivity analysis on key assumptions

---

## Null Hypothesis (H₀)

Federal economic policy changes in 2025 had no differential welfare impact on the bottom 50% of taxpayers relative to higher-income groups, OR the bottom 50% experienced a net welfare gain.

---

## Pre-Registration Notes

- This hypothesis was stated **before** any data collection or analysis
- All sub-hypotheses have falsifiable predictions
- We will report results regardless of whether they support or contradict H₁
- If data is unavailable for a sub-hypothesis, we will document the gap rather than substitute weaker evidence
- Significance level for statistical tests: α = 0.05

## Post-Analysis Summary (added 2026-02-21)

| Hypothesis | Verdict | Key statistic |
|-----------|---------|----------------|
| H1a (spending cuts hit B50) | ✅ Supported | $157.6B of $188B gap borne by B50 |
| H1b (tax burden shifted) | ⚠️ Partial | Tariff = regressive tax; income-tax data pending |
| H1c (tariffs regressive) | ✅ Supported | B50 bears 58.1% of burden, has 23.0% of income |
| H1d (debt service favors top) | ✅ Supported | Interest/safety-net z = 2.4 |
| H1e (benefits to shareholders) | ⚠️ Partial | Corporate profits data limited in FY2025 |

Overall, the master hypothesis H₁ is **broadly supported**: the bottom 50%
bear a combined fiscal burden of ~$239B ($1,282/person, 10.2% of pretax
income) from simultaneous spending cuts and tariff escalation. Results are
robust across all six dimensions tested (see FINDINGS §8).
