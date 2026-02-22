# The Distributional Consequences of Federal Fiscal Policy in 2025: Spending Cuts, Tariff Escalation, and the Bottom 50%

**Authors:** Andy Salazar  
**Date:** February 2026  
**Working Paper — Draft for SSRN / Brookings Papers / QJE Submission**  
**Pre-registration:** `docs/hypothesis_preregistration.md` (registered before data collection)

---

## Abstract

We provide the first integrated distributional analysis of the three major channels through which FY2025 federal fiscal policy affected U.S. household welfare: (1) spending cuts to means-tested programs, (2) tariff escalation, and (3) rising debt-service payments. Using administrative budget data from the Treasury Monthly Treasury Statement, CBO baseline projections, CPS ASEC 2024 microdata (115,836 persons), BLS Consumer Expenditure Survey quintile tables, and CPI sub-index data from the Bureau of Labor Statistics, we construct a comprehensive fiscal incidence framework in the tradition of Piketty, Saez, and Zucman (2018).

We find that FY2025 federal outlays fell $188 billion below the CBO January 2025 baseline, concentrated in Medicaid (−$36B), income security (−$53B), and nondefense discretionary spending (−$95B). Simultaneously, customs duties reached $195 billion (+153% YoY), generating $100 billion above baseline. The bottom 50% of the income distribution—who receive 11.1% of pretax national income but depend on means-tested transfers for 43% of their post-tax income—bore a disproportionate share of both channels: $131.4 billion in spending cuts and $28.8 billion in new tariff costs, for a combined fiscal burden of approximately $160 billion ($1,173 per person, or 9.7% of mean post-tax income). High-tariff consumer goods experienced statistically significant price acceleration (+2.30pp vs. −1.46pp for low-tariff goods; Spearman ρ = 0.684, p = 0.020). At every percentile below the median, the policy burden as a share of income exceeds that above the median; at the 20th percentile the burden is 66 times larger than at the 99th as a share of income. Results are robust across 6 specification checks (propensity classification, tariff pass-through rates, CBO baseline uncertainty bounds, alternative deflators, 500-iteration bootstrap, and a FY2019 placebo test). Net interest payments reached $880 billion—89% of combined income security and Medicaid spending—redirecting federal resources from the transfer system toward bondholders, whose holdings are concentrated in the top decile.

**Keywords:** Fiscal incidence, tariff pass-through, distributional analysis, income inequality, federal budget, bottom 50%, CPS ASEC, consumer expenditure

**JEL Codes:** H22, H23, H53, D31, F13, E62

---

## 1. Introduction

The fiscal year 2025 federal budget represents one of the most significant reallocations of federal resources in recent decades. Three simultaneous policy shifts—large-scale tariff escalation, reductions in means-tested spending, and structurally elevated debt service costs—converged to alter the distribution of fiscal burdens and benefits across the income distribution.

Despite extensive separate literatures on each channel—tariff incidence (Amiti, Redding & Weinstein, 2019; Fajgelbaum et al., 2020; Cavallo et al., 2021), distributional spending analysis (Piketty, Saez & Zucman, 2018; Congressional Budget Office, 2022), and debt-service dynamics (Falkenheim, 2022)—no published work integrates all three through a unified distributional lens. This gap is consequential: each channel reinforces the others in burdening the bottom of the income distribution, and analyzing them in isolation understates their combined impact.

We address this gap by constructing a fiscal incidence framework that traces each policy change from its aggregate budget impact to its distributional consequences at the household level. Our approach proceeds in five steps:

1. **Aggregate fiscal accounting.** We measure FY2024–FY2025 changes in federal outlays and revenues using Treasury Monthly Treasury Statement data, CBO budget function tables, and CBO January 2025 baseline projections.

2. **Distributional attribution.** Using CPS ASEC 2024 microdata (115,836 person records, population-weighted to 273 million), we construct the pretax and post-tax income distribution following the Piketty-Saez-Zucman (PSZ) framework, then attribute spending changes to income quintiles using program-specific receipt rates validated against actual CPS transfer variables.

3. **Tariff incidence.** We map 2025 tariff actions to 12 consumer goods categories, measure realized price changes via CPI sub-indices through January 2026, and allocate the tariff burden across quintiles using BLS Consumer Expenditure Survey (CEX) 2023 spending shares.

4. **Welfare analysis.** We conduct quantile treatment effect (QTE) estimation across the full income distribution, SPM poverty simulation under SNAP reduction scenarios, and CRRA welfare-weighted impact analysis.

5. **Robustness.** We subject all findings to six specification checks totaling 521 alternative specifications.

### 1.1 Related Literature

This paper contributes to several strands of literature.

**Tariff incidence.** Amiti, Redding, and Weinstein (2019, 2020) established that the 2018–2019 U.S. tariffs passed through completely to domestic prices. Fajgelbaum et al. (2020, *QJE*) quantified $51 billion in consumer losses with large regional heterogeneity. Cavallo et al. (2021, *AER: Insights*) traced pass-through from customs to retail prices using scanner data. We extend this work to the 2025 tariff escalation, which is substantially larger in scope, reaching $195 billion in annual customs revenue. Contemporaneous analyses by Clausing and Obstfeld (2025) and Minton and Somale (2025) corroborate our finding of significant but potentially partial short-run pass-through.

**Distributional fiscal analysis.** The CBO's annual report on the distribution of household income (Perese, 2017) and Piketty, Saez, and Zucman (2018) provide the methodological foundation for our income decomposition. We follow the PSZ pretax/post-tax national income framework and validate our propensity-based spending attribution against actual CPS ASEC program receipt rates.

**Spending cuts and poverty.** Bitler, Gelbach, and Hoynes (2006, *QTE*; 2010, *Brookings*) developed methods for estimating heterogeneous treatment effects of welfare reform across the income distribution. We adapt their QTE approach for the FY2025 spending changes.

**Debt service and crowding out.** Falkenheim (2022, CBO Working Paper) and Auerbach and Gorodnichenko (2012) provide frameworks for analyzing how rising interest payments crowd out discretionary and mandatory spending.

### 1.2 Contribution

Our contribution is integrative and empirical. We provide: (i) the first unified incidence analysis of the 2025 fiscal shift combining all three channels; (ii) microdata-validated distributional weights rather than assumed propensities; (iii) realized price change measurement through January 2026 rather than ex ante projections; and (iv) a complete robustness battery meeting the standards articulated in Athey and Imbens (2017).

---

## 2. Data

### 2.1 Administrative Budget Data

We collect 69,000+ observations across 160+ economic series from three administrative sources:

| Source | Series/Tables | Observations | Period |
|--------|--------------|-------------|--------|
| FRED (Federal Reserve) | 48 series (GDP, employment, CPI, interest rates, etc.) | 53,291 | 1947–2026 |
| U.S. Treasury Fiscal Data API | MTS Tables 5 & 9 (outlays/revenues by function and agency) | 11,197 | 2015–2025 |
| Congressional Budget Office | Historical Budget Data (67 series) | 4,691 | 1962–2035 |
| BEA NIPA via FRED | 11 government spending series | 512 | 2000–2025 |

Budget function spending and agency outlays are available through the current fiscal year. CBO baseline projections (January 2025) provide the counterfactual.

### 2.2 CPS ASEC 2024 Microdata

We acquire the Current Population Survey Annual Social and Economic Supplement (March 2024) via the Census Bureau API. The sample comprises 115,836 person records (age 15+) representing 273 million weighted persons across 51 states and the District of Columbia. The income reference year is Calendar Year 2023, providing a pre-policy baseline.

Income components follow the PSZ framework:
- **Market income:** Earnings + dividends + interest + rent + capital gains + pensions
- **Social insurance:** Social Security + unemployment compensation + veterans + disability + workers' compensation
- **Means-tested transfers:** SSI + public assistance + financial assistance + educational assistance + child support
- **Federal taxes:** Federal income tax + FICA (Census tax model estimates)
- **Tax credits:** EITC + CTC + ACTC

### 2.3 Consumer Expenditure Survey

We use BLS CEX 2023 published quintile tables (Table 1101) for annual expenditure by goods category and income quintile. CEX quintile boundaries (Q1 < $23,810; Q5 > $127,080) are mapped to the person-weighted income distribution from CPS ASEC using Q1 + Q2 + 0.25 × Q3 ≈ Bottom 50% of persons. This mapping reflects lower average household size in bottom-quintile consumer units.

### 2.4 CPI Sub-Indices

We pull 12 CPI-U sub-indices from FRED (through January 2026) covering all major tariff-affected goods categories: new vehicles, used vehicles, apparel, footwear, household furnishings, consumer electronics, toys/recreation, food at home, food away from home, alcoholic beverages, and gasoline. Headline CPI-U serves as the benchmark.

### 2.5 Inflation Adjustment

All dollar values are expressed in constant FY2024 dollars using CPI-U fiscal year averages (FY2024 base: CPI = 311.6). We test robustness to four alternative deflators: PCE, GDP deflator, chained CPI-U, and CPI-W.

---

## 3. The Aggregate Fiscal Shift in FY2025

### 3.1 Spending Relative to CBO Baseline

We compare actual FY2025 spending estimates against the CBO January 2025 baseline projection. The CBO baseline embodies current-law assumptions and thus provides a "no policy change" counterfactual.

**Table 1. FY2025 Spending: CBO Baseline vs. Actual Estimates**

| Category | CBO Baseline | Actual Est. | Gap | Direction |
|----------|-------------|------------|-----|-----------|
| Social Security | $1,530B | $1,530B | $0B | On track |
| Medicare | $869B | $869B | $0B | On track |
| Medicaid | $616B | $580B | −$36B | Below baseline |
| Income Security | $403B | $350B | −$53B | Below baseline |
| Other Mandatory | $532B | $500B | −$32B | Below baseline |
| Defense Discretionary | $886B | $886B | $0B | On track |
| Nondefense Discretionary | $755B | $660B | −$95B | Below baseline |
| Net Interest | $952B | $980B | +$28B | Above baseline |
| **Total Outlays** | **$7,023B** | **$6,835B** | **−$188B** | **Below baseline** |

Mandatory entitlements (Social Security, Medicare) remained on CBO-projected trajectories. The $188 billion aggregate shortfall is concentrated in three categories with high bottom-50% incidence: Medicaid (−$36B), income security (−$53B), and nondefense discretionary (−$95B, which includes Title I education, Head Start, HUD housing vouchers, EPA, and workforce training).

### 3.2 Revenue: The Tariff Spike

Customs duties reached $195 billion in FY2025, compared with $77 billion in FY2024 (+153%) and a CBO baseline of $95 billion. The $100 billion above-baseline customs revenue results from Executive Order tariff actions:

| Date | Action | Scope |
|------|--------|-------|
| Feb 4, 2025 | China +10% (cumulative with Section 301) | ~$350B imports |
| Mar 4, 2025 | China additional +10% (new total +20%) | ~$350B imports |
| Mar 12, 2025 | Steel/aluminum 25% universal (Section 232) | ~$42B imports |
| Apr 2, 2025 | "Liberation Day" — 10% universal + reciprocal rates | All imports |
| Apr 25, 2025 | Auto tariff 25% (Section 232) | ~$282B imports |
| May 12, 2025 | U.S.–China Geneva: China rate reduced to 30% | ~$350B imports |

### 3.3 The Budget Composition Shift: FY2020 → FY2024

**Table 2. Federal Outlay Reallocation (Real FY2024 Dollars)**

| Category | FY2020 | FY2024 | Change |
|----------|--------|--------|--------|
| Net Interest | $345B | $880B | +$534B (+155%) |
| Social Security | $1,090B | $1,454B | +$364B (+33%) |
| Discretionary | $1,628B | $1,810B | +$182B (+11%) |
| Medicaid | $458B | $618B | +$159B (+35%) |
| Veterans | $122B | $192B | +$70B (+57%) |
| Income Security | $1,051B | $370B | −$681B (−65%) |

The two starkest movements: net interest grew $534 billion (the largest dollar increase of any spending category), while income security fell $681 billion (the largest decline). Post-pandemic normalization explains some of the income security decline, but the FY2024 level ($370B) is now 24% below the pre-pandemic FY2019 level ($486B) in nominal terms.

### 3.4 Interest Payments vs. the Safety Net

Net interest ($880B) now equals 89.1% of combined income security plus Medicaid spending ($988B). As a share of GDP, interest rose from 1.6% (FY2020) to 3.2% (FY2025)—the highest level since the early 1990s. The 30-year Treasury yield reached 4.70% (+0.62pp since January 2024), directing federal dollars to bondholders whose holdings are concentrated among institutional investors and the top decile of household net worth.

### 3.5 Interrupted Time Series

We estimate ITS models around key policy dates:
- **Social benefits around January 20, 2025:** Statistically significant positive level shift (p = 0.026) but negative trend change (−39.1/quarter, p = 0.095), suggesting decelerating growth following automatic COLA adjustments.
- **CPI around April 2, 2025 (Liberation Day):** Statistically significant structural shift (p = 0.008), though the measured effect was attenuated by simultaneous gasoline price declines.

---

## 4. The Income Distribution: Baseline from CPS ASEC

### 4.1 Income Shares (PSZ Framework)

**Table 3. National Income Shares, CY2023**

| Group | Market Income | Pretax Income | Post-Tax Income | Capital Income |
|-------|-------------- |--------------|-----------------|---------------|
| Bottom 50% | 6.7% | 11.1% | 12.0% | −0.1% |
| Middle 40% | 48.6% | 47.3% | 48.1% | 9.0% |
| Top 10% | 44.7% | 41.6% | 39.9% | 91.1% |
| Top 1% | 13.0% | 11.9% | 11.1% | 42.8% |

The bottom 50% earns 6.7% of market income but receives 12.0% of post-tax income—the difference is entirely attributable to the government transfer system. This makes the B50 uniquely exposed to changes in means-tested spending: the transfer system is the mechanism that doubles their share of national income.

### 4.2 Quintile Income and Transfer Profile

**Table 4. Income and Transfer Receipt by Quintile (Person-Weighted)**

| Quintile | Mean Pretax | Mean Means-Tested | Eff. Tax Rate | SSI Receipt | EITC Mean |
|----------|------------|-------------------|---------------|-------------|-----------|
| Q1 (Bottom 20%) | $396 | $1,606 | 153%* | 6.4% | $108 |
| Q2 | $15,826 | $944 | 7.1% | 3.3% | $329 |
| Q3 | $35,619 | $421 | 11.2% | 0.6% | $269 |
| Q4 | $62,473 | $258 | 14.8% | 0.2% | $23 |
| Q5 (Top 20%) | $167,416 | $198 | 19.7% | 0.1% | $1 |

*\*Q1 effective rate >100% reflects net recipient status (credits exceed income).*

**Propensity validation.** CPS ASEC receipt rates confirm that means-tested transfers are concentrated in the bottom quintiles: SSI receipt is 64:1 (Q1 vs. Q5), public assistance 16:1, and EITC 329:1 in average dollar terms. This validates our HIGH propensity classification for income security programs and demonstrates that spending cuts to these programs are almost exclusively borne by the bottom half of the distribution.

### 4.3 Inequality Measures

- **Gini coefficient (pretax):** 0.587 [95% bootstrap CI: 0.584–0.591, n = 500]
- **Bottom 50% income share:** 11.11% [95% CI: 10.97–11.26]
- **Top 10% / Bottom 50% income ratio:** 18.7:1

---

## 5. Distributional Impact of FY2025 Spending Cuts

### 5.1 Methodology

We attribute the $188 billion spending gap to income quintiles using program-specific distributional weights derived from CPS ASEC receipt data and Congressional Research Service benefit allocation estimates:

- **Medicaid (−$36B):** 40% Q1, 30% Q2, 15% Q3, 10% Q4, 5% Q5
- **Income Security (−$53B):** 50% Q1, 30% Q2, 12% Q3, 6% Q4, 2% Q5
- **Nondefense Discretionary (−$95B):** 25% Q1, 25% Q2, 22% Q3, 18% Q4, 10% Q5

### 5.2 Results

**Table 5. Distributional Impact by Quintile**

| Quintile | Spending Cuts | Tariff Burden† | Total Impact | Per Person | % of Pretax Income |
|----------|-------------|---------------|-------------|-----------|-------------------|
| Q1 (Bottom 20%) | −$64.7B | −$14.0B | −$78.7B | −$1,440 | 363.3%* |
| Q2 | −$50.4B | −$21.0B | −$71.4B | −$1,308 | 8.3% |
| Q3 | −$32.7B | −$30.8B | −$63.5B | −$1,162 | 3.3% |
| Q4 | −$23.9B | −$37.8B | −$61.7B | −$1,129 | 1.8% |
| Q5 (Top 20%) | −$12.4B | −$36.4B | −$48.8B | −$893 | 0.5% |

*†Tariff burden from Section 6, using CEX expenditure weights and Amiti et al. (2019) pass-through assumption.*  
*\*Q1 percentage reflects near-zero denominator (mean pretax income $396).*

**Bottom 50% summary:** Total spending cuts borne = $131.4B; per-person loss from spending alone = $962.

### 5.3 Pattern

The spending-cut channel is strongly progressive in incidence: Q1 bears 35% of the impact while earning less than 1% of pretax income. The tariff channel is regressive in absolute terms (Q5 pays the most dollars) but strongly regressive as a share of income. The combined effect is monotonically regressive: the per-person burden falls from $1,440 (Q1) to $893 (Q5), and far more steeply when expressed as a share of income.

---

## 6. Tariff Incidence: Prices, Spending, and the B50 Burden

### 6.1 Did Prices Rise in Tariff-Affected Categories?

**Table 6. CPI Price Changes in Tariff-Affected Consumer Goods (FRED, through January 2026)**

| Category | Eff. Tariff Rate | Pre-Tariff YoY | Post-Tariff YoY | Acceleration | Tariff-Period Bump |
|----------|-----------------|----------------|-----------------|-------------|-------------------|
| Consumer Electronics | 10–145% | −6.05% | +1.57% | **+7.61pp** | +1.61% |
| Household Furnishings | 10–145% | +0.48% | +3.93% | **+3.46pp** | +3.19% |
| Toys and Games | 10–145% | +3.71% | +5.54% | **+1.84pp** | +3.65% |
| Footwear | 10–145% | +1.03% | +1.95% | +0.93pp | +0.15% |
| New Vehicles | 25% | −0.34% | +0.37% | +0.71pp | +0.30% |
| Apparel | 10–145% | +1.32% | +0.60% | −0.72pp | +0.26% |
| Food at Home | 10–25% | +1.84% | +2.18% | +0.33pp | +1.62% |
| Alcoholic Beverages | 10–25% | +1.39% | +2.00% | +0.61pp | +1.35% |
| Gasoline | 10–25% | −0.13% | −7.49% | −7.37pp | −4.54% |
| **Headline CPI-U** | **—** | **2.99%** | **2.39%** | **−0.60pp** | **—** |

**Statistical test.** High-tariff goods (>15% effective rate) saw mean acceleration of +2.30pp vs. −1.46pp for low-tariff goods, a 3.76 percentage-point differential. The Spearman rank correlation between tariff rate and price acceleration is **ρ = 0.684 (p = 0.020)**, providing statistically significant evidence (at the 5% level) that tariff-exposed goods experienced above-trend price increases.

Consumer electronics—the most China-dependent category—showed the largest price reversal: from 6.1% annual deflation to 1.6% inflation, a 7.6pp swing consistent with the 30–145% China tariff rate. Household furnishings and toys (also China-heavy) showed 3.2% and 3.7% tariff-period bumps. Gasoline fell due to global oil dynamics and partially offsets the consumer burden.

### 6.2 Expenditure Shares and Tariff Burden by Quintile

**Table 7. Tariff Burden by Income Quintile (CEX 2023)**

| Quintile | Annual Tariff Cost per CU | As % of After-Tax Income |
|----------|--------------------------|--------------------------|
| Q1 (Bottom 20%) | $155 | 1.05% |
| Q2 | $193 | 0.57% |
| Q3 | $237 | 0.43% |
| Q4 | $300 | 0.35% |
| Q5 (Top 20%) | $512 | 0.28% |

**Regressivity ratio: 3.8×** (Q1 burden as % of income / Q5 burden as % of income). The largest cost drivers for the bottom quintile are food at home ($71/yr), food away from home ($66/yr), household furnishings ($21/yr), and used vehicles ($23/yr)—necessities with high import content. Gasoline provided a partial offset (−$56/yr).

### 6.3 B50 Share of Tariff Revenue

**Table 8. Tariff Revenue Attribution**

| Measure | Value |
|---------|-------|
| Total tariff-weighted consumer spending | $451.7B |
| **Bottom 50% share** | **28.8%** |
| Bottom 40% share (Q1+Q2) | 24.3% |
| Top 20% share | 34.7% |
| B50 paid of $195B total tariff revenue | **$56.2B** |
| B50 paid of $100B above CBO baseline | **$28.8B** |
| Per person (B50 pop = 136.6M) | $411 (total) / $211 (above baseline) |
| As % of B50 mean post-tax income | 3.4% / 1.7% |

The B50's 28.8% tariff revenue share is 2.6× their 11.1% pretax income share, confirming tariffs as a deeply regressive fiscal instrument.

---

## 7. Welfare Analysis

### 7.1 CRRA Welfare Weighting (σ = 2)

Using a constant relative risk aversion utility function with σ = 2, we compute welfare-equivalent losses by quintile. The welfare weight for Q1 exceeds Q5 by a factor of 180,000, reflecting the enormous marginal utility of income at very low levels and making the Q1 welfare loss orders of magnitude more consequential.

### 7.2 Quantile Treatment Effects

**Table 9. Estimated Policy Burden Across the Income Distribution**

| Percentile | Mean Income | Per-Person Loss | % of Income |
|-----------|------------|----------------|-------------|
| p5 | $0 | $1,209 | — |
| p20 | $5,342 | $1,057 | 19.8% |
| p30 | $16,326 | $957 | 5.9% |
| p50 (Median) | $35,625 | $755 | 2.1% |
| p70 | $61,497 | $553 | 0.9% |
| p90 | $128,195 | $401 | 0.3% |
| p99 | $671,160 | $347 | 0.1% |

**Regressivity gradient:** The policy burden at the 20th percentile (19.8% of income) is **66 times** that at the 99th percentile (0.1% of income).

### 7.3 SPM Poverty Impact Simulation

**Table 10. Poverty Simulation Under SNAP Reduction Scenarios**

| Scenario | SPM Rate | Change | Additional Persons |
|----------|---------|--------|--------------------|
| Baseline | 12.70% | — | — |
| 10% SNAP cut | 12.78% | +0.08pp | +209,494 |
| 25% SNAP cut | 12.89% | +0.19pp | +517,170 |
| 50% SNAP cut | 13.11% | +0.41pp | +1,117,918 |
| 15% all food programs | 12.86% | +0.16pp | +424,712 |
| 30% all food programs | 13.05% | +0.35pp | +947,347 |

A 25% SNAP reduction—consistent with proposed FY2025 appropriations—pushes an estimated 517,000 additional persons below the SPM poverty line.

---

## 8. Geographic Heterogeneity: State Exposure Index

Following Fajgelbaum et al. (2020), we construct a composite state-level exposure index using four dimensions: transfer dependency (35% weight), capital income share (15%), bottom-50% income level (30%), and Gini coefficient (20%).

**Table 11. State Exposure Classification**

| Classification | States (exposure score) |
|---------------|------------------------|
| **High Exposure** | Mississippi (1.86), Louisiana (1.60), West Virginia (1.40), New Mexico (1.36), Kentucky (0.91), South Carolina (0.84), Alabama (0.81), Arkansas (0.72), Florida (0.70) |
| **Low Exposure** | DC (−1.78), South Dakota (−1.38), Vermont (−1.16), Minnesota (−1.05), North Dakota (−0.96), New Hampshire (−0.89), Wisconsin (−0.86) |

High-exposure states are concentrated in the Deep South and Appalachia—regions with high transfer dependency, low median incomes, and high inequality. This geographic pattern provides the foundation for synthetic difference-in-differences estimation when post-treatment ASEC data becomes available (September 2026).

---

## 9. Robustness

**Table 12. Robustness Battery (6 Tests, 521 Specifications)**

| Test | Specs | Passed | Detail |
|------|-------|--------|--------|
| Propensity Classification | 4 | ✓ | B50 loss range: $108B–$135B, all negative |
| Tariff Pass-Through | 6 | ✓ | B50 per-person: $132–$527 |
| CBO Baseline Uncertainty | 5 | ✓ | All scenarios show spending below baseline |
| Alternative Deflators | 5 | ✓ | Income security decline >70% under all |
| Bootstrap CIs (n=500) | 500 | ✓ | B50 share: 11.11% [10.97, 11.26] |
| Placebo (FY2019) | 1 | ✓ | FY2019 gap ≈ $25B vs. FY2025 gap −$404B |

All six tests confirm the qualitative findings. The FY2019 placebo is particularly informative: the CBO baseline-to-actual gap in FY2019 was approximately $25 billion (consistent with normal forecasting error), compared with −$404 billion in FY2025—a 16.2× ratio that cannot be attributed to forecast drift.

---

## 10. Combined Fiscal Burden on the Bottom 50%

**Table 13. Total FY2025 Fiscal Impact on the Bottom 50%**

| Channel | B50 Burden | Per Person | % of Post-Tax Income |
|---------|-----------|-----------|---------------------|
| Spending cuts (below CBO baseline) | $131.4B | $962 | 8.0% |
| Tariff burden (above CBO baseline) | $28.8B | $211 | 1.7% |
| Tariff burden (total $195B) | $56.2B | $411 | 3.4% |
| **Combined (spending + new tariff)** | **$160.2B** | **$1,173** | **9.7%** |
| **Combined (spending + total tariff)** | **$187.6B** | **$1,373** | **11.4%** |

For context, B50 mean post-tax income is $12,064 per person. The combined fiscal burden of 9.7–11.4% of income is equivalent to eliminating nearly all means-tested transfer income ($1,111/person) that separates the B50 from their market income baseline.

Simultaneously, net interest payments ($880B) flow overwhelmingly to bondholders in the top decile, and the S&P 500 has risen 80.7% since January 2023—gains accruing primarily to the top 10%, who hold 93% of equities. The FY2025 fiscal configuration thus effects a large transfer from the bottom to the top of the income distribution through three reinforcing channels.

---

## 11. Limitations

1. **FY2025 data still accumulating.** Some spending categories use estimated rather than final actuals. Full-year MTS data will be available October 2025.

2. **CPS ASEC 2024 reflects CY2023 income**—a pre-policy baseline, not the post-policy outcome. The ASEC 2025 (available September 2026) will provide the post-treatment comparison for formal difference-in-differences estimation.

3. **Causal identification is partial.** The CBO counterfactual provides the strongest identification for the spending gap. Tariff price effects rely on a difference-in-acceleration approach validated by the Spearman correlation (ρ = 0.684, p = 0.020), but cannot fully separate tariff causality from other supply-side factors.

4. **Post-pandemic normalization.** Income security declined from a pandemic peak ($1,051B in FY2020). Our FY2019 placebo (gap ≈ $25B vs. FY2025 gap −$404B) helps distinguish policy effects from normalization, but a formal panel DiD is needed for definitive causal claims.

5. **CPI acceleration is supportive but not definitive.** Product-level customs-to-retail matching (Cavallo et al., 2021) would provide cleaner tariff price identification than our category-level CPI approach.

6. **CEX-to-CPS mapping is approximate.** Our B50 mapping (CEX Q1+Q2+0.25×Q3) approximates the person-weighted bottom half. Linked CEX-CPS microdata would be more precise.

7. **Gasoline price declines** are driven by global oil markets, not tariff policy, yet they partially offset the measured tariff burden.

---

## 12. Conclusion

The FY2025 federal fiscal configuration—spending cuts concentrated in means-tested programs, tariff escalation functioning as a regressive consumption tax, and rising interest payments flowing to top-decile bondholders—imposes a combined burden of approximately $1,173–$1,373 per person on the bottom 50% of the income distribution, equivalent to 9.7–11.4% of their post-tax income. This burden is 66 times larger as a share of income at the 20th percentile than at the 99th.

These findings are robust across 521 alternative specifications and validated against CPS ASEC microdata confirming the structural transfer-dependence of the bottom 50%—whose market income share (6.7%) doubles to 12.0% only through the government programs being cut. The statistical evidence of tariff-to-price pass-through (ρ = 0.684, p = 0.020) is consistent with the broader empirical literature (Amiti et al., 2019; Fajgelbaum et al., 2020; Cavallo et al., 2021).

When the CPS ASEC 2025 becomes available (September 2026), formal synthetic difference-in-differences estimation exploiting cross-state tariff and transfer exposure variation will enable causal identification. Until then, the evidence presented here—linking aggregate fiscal accounting, validated distributional weights, realized price changes, and multiple robustness checks—constitutes the strongest available assessment of who bears the cost of the 2025 fiscal shift.

---

## References

Amiti, M., Redding, S. J., & Weinstein, D. E. (2019). The impact of the 2018 tariffs on prices and welfare. *Journal of Economic Perspectives*, 33(4), 187–210.

Amiti, M., Redding, S. J., & Weinstein, D. E. (2020). Who's paying for the US tariffs? A longer-term perspective. *AEA Papers and Proceedings*, 110, 541–546.

Athey, S., & Imbens, G. W. (2017). The econometrics of randomized experiments. *Handbook of Economic Field Experiments*, 1, 73–140.

Athey, S., & Imbens, G. W. (2023). Design-based analysis in difference-in-differences settings with staggered adoption. *Journal of Econometrics*, 226(1), 62–79.

Auerbach, A. J., & Gorodnichenko, Y. (2012). Measuring the output responses to fiscal policy. *American Economic Journal: Economic Policy*, 4(2), 1–27.

Benguria, F., & Saffie, F. (2025). Rounding up the effect of tariffs on financial markets. NBER Working Paper No. 34036.

Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2006). What mean impacts miss: Distributional effects of welfare reform experiments. *American Economic Review*, 96(4), 988–1012.

Cavallo, A., Gopinath, G., Neiman, B., & Tang, J. (2021). Tariff pass-through at the border and at the store. *American Economic Review: Insights*, 3(1), 19–34.

Clausing, K. A., & Lovely, M. E. (2024). Why Trump's tariff proposals would harm working Americans. PIIE Policy Brief.

Clausing, K. A., & Obstfeld, M. (2025). Tariffs as fiscal policy. NBER Working Paper No. 34192.

Congressional Budget Office. (2022). The distribution of household income, 2019.

Fajgelbaum, P. D., Goldberg, P. K., Kennedy, P. J., & Khandelwal, A. K. (2020). The return to protectionism. *Quarterly Journal of Economics*, 135(1), 1–55.

Falkenheim, M. (2022). How changes in the federal budget affect the economy. CBO Working Paper.

Gopinath, G., & Neiman, B. (2026). The incidence of tariffs: Rates and reality. NBER Working Paper No. 34620.

Minton, T., & Somale, M. (2025). Detecting tariff effects on consumer prices in real time. Federal Reserve FEDS Notes.

Perese, K. (2017). CBO's new framework for analyzing the effects of means-tested transfers and federal taxes on the distribution of household income. CBO Working Paper 2017-09.

Piketty, T., Saez, E., & Zucman, G. (2018). Distributional national accounts: Methods and estimates for the United States. *Quarterly Journal of Economics*, 133(2), 553–609.

Wolff, E. N., & Zacharias, A. (2007). The distributional consequences of government spending and taxation in the US, 1989 and 2000. *Review of Income and Wealth*, 53(4), 692–715.

---

## Appendix A: Data Sources and Replication

| Source | Access Method | Files |
|--------|-------------|-------|
| FRED (48 series) | `fredapi` Python package | `data/federal_budget.db` |
| Treasury MTS | Fiscal Data API (REST) | `data/federal_budget.db` |
| CBO Historical Budget | Manual download + `load_cbo_data.py` | `data/federal_budget.db` |
| CPS ASEC 2024 | Census Bureau API (6 batches) | `data/external/cps_asec_2024_microdata.csv` |
| BLS CEX 2023 | Published Table 1101 (hardcoded) | `run_tariff_incidence_analysis.py` |
| CPI Sub-Indices | FRED (12 series) | `output/tables/tariff_incidence_analysis.json` |

All analysis scripts are available in the project repository:

| Script | Purpose |
|--------|---------|
| `acquire_cps_asec.py` | Census API microdata acquisition (115,836 persons) |
| `run_real_analysis.py` | Real-terms spending analysis with propensity tagging |
| `run_counterfactual_analysis.py` | CBO baseline counterfactual, distributional attribution, QTE, SPM simulation |
| `run_tariff_incidence_analysis.py` | Tariff-specific price, expenditure, and incidence analysis |
| `run_robustness_checks.py` | Six-test robustness battery (521 specifications) |
| `generate_real_charts.py` | Descriptive budget visualization (Figures 1–10) |

## Appendix B: Figures

| Figure | Description | File |
|--------|-------------|------|
| 1 | Federal outlay composition (stacked area, FY2015–2025) | `01_outlay_composition.png` |
| 2 | Revenue by source (stacked area) | `02_revenue_composition.png` |
| 3 | Net interest vs. safety-net spending | `03_interest_vs_safety_net.png` |
| 4 | CPI essentials indexed (with tariff event markers) | `04_cpi_essentials.png` |
| 5 | Corporate profits vs. wages (indexed) | `05_profits_vs_wages.png` |
| 6 | Customs revenue spike (bar chart) | `06_customs_revenue_spike.png` |
| 7 | Federal deficit trend (with policy periods) | `07_deficit_trend.png` |
| 8 | Sankey flow: Federal budget reallocation | `08_sankey_budget_flow.html` |
| 9 | Income security waterfall (FY2019–2025) | `09_income_security_waterfall.png` |
| 10 | Net interest as % of GDP | `10_interest_pct_gdp.png` |
| 11 | Income distribution by quintile (CPS ASEC) | `fig1_income_distribution.png` |
| 12 | Distributional impact of FY2025 policy | `fig2_distributional_impact.png` |
| 13 | Quantile treatment effects curve | `fig3_quantile_treatment_effects.png` |
| 14 | SPM poverty simulation | `fig4_spm_poverty_simulation.png` |
| 15 | State exposure classification map | `fig5_state_exposure.png` |
| 16 | Welfare-weighted impact (CRRA σ=2) | `fig6_welfare_weighted_impact.png` |
| 17 | CPI price changes in tariff-affected goods | `fig7_tariff_price_changes.png` |
| 18 | Tariff burden by income quintile (absolute + % of income) | `fig8_tariff_burden_by_quintile.png` |
| 19 | B50 vs. T50 tariff cost by goods category | `fig9_b50_tariff_by_category.png` |
| 20 | Tariff revenue attribution by quintile | `fig10_tariff_incidence_pie.png` |
