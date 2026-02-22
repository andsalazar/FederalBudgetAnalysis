---
title: |
  The Distributional Consequences of Federal Fiscal Policy, FY2000–FY2025: A Quarter-Century of Structural Shift and the 2025 Inflection Point
author:
  - Andy Salazar
date: February 2026
abstract: |
  
  We provide a unified distributional analysis of U.S. federal fiscal policy over FY2000–FY2025, combining 26 annual observations of CBO historical budget data, Census Bureau income-distribution series, CPS ASEC microdata for eight benchmark years (1.4 million person-records), and Treasury Monthly Treasury Statement administrative data. We embed the FY2025 fiscal realignment within this longer trajectory using structural break tests, distinguishing secular trends from genuine policy discontinuities.
  
  Over FY2000–FY2025, total real outlays grew 109%, net interest rose 132%, and customs revenue increased 422% (all in constant FY2024 dollars). Structural break tests identify two of four indicators as genuine policy discontinuities: customs as a share of total revenue jumped from 1.0% to 3.7% against a trend-predicted 1.20% (z = 25.8, structural break); the interest-to-safety-net crowding ratio reached 0.91—approximately double its trend-predicted value of 0.45 (z = 2.4, structural break). The regressive revenue share (excises + customs + FICA), which drifted from 36.6% to 39.1%, remains within the pre-existing trend (z = 0.5), as does the safety-net share of outlays (z = −1.5). Census data confirm a concurrent compression of the bottom 20% income share from 3.6% (2000) to 3.0% (2023) while the top 20% share rose from 49.8% to 52.4%.
  
  Against this structural backdrop, FY2025 represents an inflection point. Federal outlays fell $188 billion below the CBO January 2025 baseline, concentrated in Medicaid (−$36B), income security (−$53B), and nondefense discretionary spending (−$95B). Customs duties reached $195 billion (+153% YoY), generating $100 billion above baseline. The bottom 50% of the income distribution by person pretax income—defined as Q1+Q2+0.5×Q3 of CPS ASEC person-income quintiles (136.6M persons, exactly 50% of the population)—bear a combined fiscal burden of approximately $182 billion from spending cuts and tariff consumer burden ($1,331 per person, or 10.6% of mean pretax income). In the CEX household-income framework, the B50 bears 51.7% of tariff-weighted consumer spending despite holding only 23.0% of household pretax income. High-tariff consumer goods experienced statistically significant price acceleration (+2.30pp vs. −1.46pp for low-tariff goods; Spearman ρ = 0.684, p = 0.020). At the 20th percentile the simulated burden is approximately 383 times larger than at the 99th as a share of income. Results are robust across 21 distinct analytical specifications spanning six robustness dimensions, with 500-draw household-clustered bootstrap confidence intervals. Net interest payments reached $980 billion in FY2025—exceeding combined income security and Medicaid spending ($930B, 105%)—redirecting federal resources from the transfer system toward bondholders concentrated in the top decile.
  
  Following the Supreme Court's invalidation of IEEPA tariff authority (*Learning Resources, Inc. v. Trump*, No. 24-1287, Feb. 20, 2026), we extend the framework to model the combined effects of judicial tariff revocation and the announced 15% universal legislative replacement. Under empirically grounded price stickiness assumptions (Peltzman, 2000; Cavallo, 2018), revocation provides zero consumer relief to B50—the tariff wedge shifts from Treasury to corporate margins while $133B+ in refunds flows to importers—and the replacement tariff nearly doubles the B50 combined burden to $2,341 per person (18.7% of pretax income) under central estimates.

keywords: "Fiscal incidence, tariff pass-through, distributional analysis, income inequality, federal budget, bottom 50%, structural break, CPS ASEC, consumer expenditure"
thanks: "Working Paper. Replication package: https://github.com/andsalazar/FederalBudgetAnalysis. Pre-registration: docs/hypothesis_preregistration.md"
geometry: margin=1in
fontsize: 11pt
linestretch: 1.5
numbersections: false
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{graphicx}
  - \usepackage{float}
  - \usepackage{caption}
  - \captionsetup{font=small,labelfont=bf}
  - \usepackage{hyperref}
  - \hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}
  - \usepackage{amsmath}
  - \usepackage{array}
  - \renewcommand{\arraystretch}{1.2}
  - \setlength{\tabcolsep}{4pt}
---

## 1. Introduction

The fiscal year 2025 federal budget represents one of the most significant reallocations of federal resources in recent decades. Three simultaneous policy shifts—large-scale tariff escalation, reductions in means-tested spending, and structurally elevated debt service costs—converged to alter the distribution of fiscal burdens and benefits across the income distribution.

But how exceptional is FY2025? To answer this question rigorously, we embed the 2025 fiscal configuration within the 26-year span FY2000–FY2025, using structural break tests to distinguish genuine policy discontinuities from secular trends. This longer lens reveals that some features of FY2025—such as the growing share of regressive revenue sources—are continuations of quarter-century trends, while others—most dramatically, the customs revenue explosion—represent statistically identifiable ruptures from the historical pattern.

Despite extensive separate literatures on each channel—tariff incidence (Amiti, Redding & Weinstein, 2019; Fajgelbaum et al., 2020; Cavallo et al., 2021), distributional spending analysis (Piketty, Saez & Zucman, 2018; Congressional Budget Office, 2022), and debt-service dynamics (Falkenheim, 2022)—no published work integrates all three through a unified distributional lens, nor embeds the current moment within the longer structural trajectory. This gap is consequential: each channel reinforces the others in burdening the bottom of the income distribution, and analyzing them in isolation—or without historical context—understates their combined significance.

We address this gap by constructing a fiscal incidence framework that traces each policy change from its aggregate budget impact to its distributional consequences at the household level. Our approach proceeds in six steps:

1. **Structural accounting.** We reconstruct real (FY2024 dollar) federal outlay and revenue composition from FY2000 to FY2025 using CBO Historical Budget Data, deriving safety-net shares, interest crowding ratios, and revenue-source composition over the full 26-year panel.

2. **Structural break identification.** We fit OLS linear trends to four key distributional indicators over indicator-specific training periods (FY2000–2017 for customs and regressive shares; FY2000–2024 excluding COVID-distorted FY2020–2021 for interest and safety-net ratios) and test whether FY2025 values represent statistically significant deviations (|z| > 2.0) from trend-predicted values (see Appendix C for full regression outputs).

3. **Aggregate fiscal accounting.** We measure FY2024–FY2025 changes in federal outlays and revenues using Treasury Monthly Treasury Statement data, CBO budget function tables, and CBO January 2025 baseline projections.

4. **Distributional attribution.** Using CPS ASEC microdata for eight benchmark years (CY2002–CY2023, totaling 1.4 million person records), plus the full CPS ASEC 2024 (115,836 persons, population-weighted to 273 million), we construct the pretax and post-tax income distribution following the Piketty-Saez-Zucman (PSZ) framework, then attribute spending changes to income quintiles using program-specific receipt rates validated against actual CPS transfer variables.

5. **Tariff incidence.** We map 2025 tariff actions to 12 consumer goods categories, measure realized price changes via CPI sub-indices through January 2026, and allocate the tariff burden across quintiles using BLS Consumer Expenditure Survey (CEX) 2023 spending shares.

6. **Welfare analysis and robustness.** We conduct simulated distributional burden analysis by percentile, SPM poverty simulation, CRRA welfare-weighted impact analysis, and subject all findings to six robustness dimensions spanning 21 distinct analytical specifications with household-clustered bootstrap confidence intervals.

7. **Policy scenario analysis.** Following the Supreme Court's invalidation of IEEPA tariff authority (February 20, 2026), we extend the framework to model the distributional consequences of tariff revocation under price stickiness and the announced 15% universal legislative tariff replacement, using the same incidence parameters established in Steps 4–6 (Section 12).

### 1.1 Related Literature

This paper contributes to several strands of literature.

**Tariff incidence.** Amiti, Redding, and Weinstein (2019, 2020) established that the 2018–2019 U.S. tariffs passed through completely to domestic prices. Fajgelbaum et al. (2020, *QJE*) quantified $51 billion in consumer losses with large regional heterogeneity. Cavallo et al. (2021, *AER: Insights*) traced pass-through from customs to retail prices using scanner data. A comprehensive retrospective by Leibovici and Dunn (2025, Federal Reserve Bank of St. Louis) surveys the 2018–19 literature and confirms the consensus that earlier tariff rounds were passed through almost entirely to domestic firms and consumers—establishing a well-identified baseline against which the much larger 2025 escalation can be evaluated. We extend this body of work to the 2025 tariff regime, which reaches $195 billion in annual customs revenue—roughly four times the 2018–19 scale. Contemporaneous analyses by Clausing and Obstfeld (2025) and Minton and Somale (2025) corroborate our finding of significant but potentially partial short-run pass-through. Clausing and Lovely (2024) provide an ex ante distributional analysis of proposed tariff schedules, while Gopinath and Neiman (2026) model the incidence of realized tariff rates on consumer prices. Benguria and Saffie (2025) document tariff effects propagating through financial markets, suggesting additional wealth-channel impacts beyond the consumer price mechanism.

**Tariffs and poverty.** The Budget Lab at Yale (2026) models how the 2025 tariff regime erodes purchasing power of the bottom 50%, mapping tariff-driven price increases (via PCE and CPI-U) onto the Supplemental Poverty Measure. Their finding that tariff costs are deeply regressive in purchasing-power terms provides an independent benchmark for our distributional estimates; our analysis extends their work by integrating tariff incidence with spending cuts and interest-crowding effects within a unified fiscal framework.

**Distributional fiscal analysis.** The CBO's annual report on the distribution of household income (Perese, 2017) and Piketty, Saez, and Zucman (2018) provide the methodological foundation for our income decomposition. We follow the PSZ pretax/post-tax national income framework and validate our propensity-based spending attribution against actual CPS ASEC program receipt rates.

**Spending cuts and poverty.** Bitler, Gelbach, and Hoynes (2006, *QJE*; 2010, *Brookings*) developed methods for estimating heterogeneous treatment effects of welfare reform across the income distribution. We draw on their conceptual framework to motivate our simulation of distributional burden by percentile, applied to the FY2025 spending changes, though our approach uses parametric incidence assumptions rather than statistical QTE estimation.

**Debt service and crowding out.** Falkenheim (2022, CBO Working Paper) and Auerbach and Gorodnichenko (2012) provide frameworks for analyzing how rising interest payments crowd out discretionary and mandatory spending.

### 1.2 Contribution

Our contribution is integrative, historical, and empirical. We provide: (i) the first unified incidence analysis of the 2025 fiscal shift combining all three channels; (ii) a 26-year structural context (FY2000–FY2025) with formal break-point tests distinguishing secular trends from policy discontinuities; (iii) microdata-validated distributional weights using eight benchmark years of CPS ASEC data (1.4 million person-records); (iv) realized price change measurement through January 2026 rather than ex ante projections; and (v) a complete robustness battery meeting the standards articulated in Athey and Imbens (2017).

---

\newpage
## 2. Data

### 2.1 Administrative Budget Data

We collect 69,000+ observations across 160+ economic series from four administrative sources:

| Source | Series/Tables | Observations | Period |
|--------|--------------|-------------|--------|
| FRED (Federal Reserve) | 48 series (GDP, employment, CPI, interest rates, etc.) | 53,291 | 1947–2026 |
| U.S. Treasury Fiscal Data API | MTS Tables 5 & 9 (outlays/revenues by function and agency) | 11,197 | 2015–2025 |
| Congressional Budget Office | Historical Budget Data (67 series) | 4,691 | 1962–2035 |
| BEA NIPA via FRED | 11 government spending series | 512 | 2000–2025 |

For the structural analysis, we extract CBO historical outlay and revenue series back to FY2000, yielding 26 annual observations (FY2000–FY2025 inclusive) for each of 32 budget aggregates in both nominal and real (FY2024 dollar) terms. Budget function spending and agency outlays for recent years are available through the current fiscal year. CBO baseline projections (January 2025) provide the FY2025 counterfactual.

### 2.2 Census Income Distribution Data

We use two complementary income-distribution series spanning the full analysis window:

**Census Table H-2 (household income quintile shares).** Annual aggregate quintile shares (bottom 20% through top 5%) from the Census Bureau's Historical Income Tables, 2000–2023 (24 annual observations). These provide the longest consistent series on U.S. income concentration.

**CPS ASEC microdata (eight benchmark years).** We acquire Current Population Survey Annual Social and Economic Supplement data for calendar years 2002, 2005, 2008, 2011, 2014, 2017, 2020, and 2023 via the Census Bureau API. Each benchmark year comprises 144,000–216,000 person records (age 15+) with full income component detail and supplement weights (`MARSUPWT`), for a combined total of approximately 1.4 million person-records across the eight benchmarks. These enable us to track the evolution of bottom-50% income shares and transfer dependency at the microdata level.

### 2.3 CPS ASEC 2024 Microdata (Primary Cross-Section)

We acquire the CPS ASEC March 2024 via the Census Bureau API. The sample comprises 115,836 person records (age 15+) representing 273 million weighted persons across 51 states and the District of Columbia. The income reference year is Calendar Year 2023, providing a pre-policy baseline.

Income components follow the PSZ framework:
- **Market income:** Earnings + dividends + interest + rent + capital gains + pensions
- **Social insurance:** Social Security + unemployment compensation + veterans' compensation + disability insurance + workers' compensation. Note: means-tested veterans' pensions (received by 0.8% of CPS ASEC persons) are classified under means-tested transfers when identifiable via the `VET_VAL` variable; the remainder—primarily non-means-tested disability compensation and survivors' benefits—are classified as social insurance
- **Means-tested transfers:** SSI + public assistance + financial assistance + educational assistance + child support
- **Federal taxes:** Federal income tax + FICA (Census tax model estimates)
- **Tax credits:** EITC + CTC + ACTC

### 2.4 Consumer Expenditure Survey

We use BLS CEX 2023 published quintile tables (Table 1101) for annual expenditure by goods category and income quintile. CEX quintile boundaries (Q1 < $23,810; Q5 > $127,080) are defined by *consumer unit* (CU) before-tax income, which differs from the person-level income ranking used in the PSZ framework.

To map CEX CU quintiles to a person-weighted B50, we calibrate the cross-walk using CPS ASEC 2024 microdata (115,836 persons). We group respondents by household (PH_SEQ), sum pretax income to approximate CU income, and assign each person their household’s CEX quintile band. The person-weighted 50th percentile of household income is $96,000—which falls in CEX Q4 ($77,025–$127,080). Exactly 41.4% of Q4 persons have household income below this threshold, yielding the calibrated mapping:

$$\text{B50}_{\text{CEX}} = Q_1 + Q_2 + Q_3 + 0.414 \times Q_4$$

This captures exactly 50.0% of persons by household income rank (10.1% + 12.7% + 17.8% + 0.414 × 22.7%). The previously used approximation Q1 + Q2 + 0.25 × Q3 captured only 27.2% of persons due to the large household-size gradient across CEX quintiles (higher-income CUs contain more persons). Sensitivity bounds using Q1+Q2+Q3 only (40.6% of persons) and Q1+Q2+Q3+Q4 (63.3%) bracket the calibrated estimate.

**Important distinction: two quintile systems.** The CEX calibration above applies only to the tariff expenditure share calculation (Section 7), where CEX CU-income quintiles have *unequal* person shares due to household-size gradients. For the counterfactual spending-cut analysis (Section 6) and combined burden (Section 11), we use CPS ASEC *person-income* quintiles, where each quintile contains exactly 20% of persons by construction. In the CPS person-income framework, the bottom 50% is simply Q1+Q2+0.5×Q3 (136.6M persons). The distinction matters: applying the CEX formula (Q1+Q2+Q3+0.414×Q4) to equal-share CPS quintiles would capture 68.3% of persons rather than 50%.

### 2.5 CPI Sub-Indices

We pull 12 CPI-U sub-indices from FRED (through January 2026) covering all major tariff-affected goods categories: new vehicles, used vehicles, apparel, footwear, household furnishings, consumer electronics, toys/recreation, food at home, food away from home, alcoholic beverages, and gasoline. Headline CPI-U serves as the benchmark.

### 2.6 Inflation Adjustment

All dollar values are expressed in constant FY2024 dollars using CPI-U fiscal year averages (FY2024 base: CPI = 311.6). We test robustness to four alternative deflators: PCE, GDP deflator, chained CPI-U, and CPI-W.

---

\newpage
## 3. The 26-Year Structural Trajectory (FY2000–FY2025)

Before analyzing FY2025 in detail, we establish the quarter-century structural context. All dollar values in this section are expressed in constant FY2024 dollars using CPI-U fiscal year averages.

### 3.1 Aggregate Budget Evolution

**Table 1a. Federal Budget Aggregates, FY2000 vs. FY2025 (Real FY2024 Dollars)**

| Measure | FY2000 | FY2025 | Change |
|---------|--------|--------|--------|
| Total Outlays | $3,265B | $6,826B | +$3,561B (+109%) |
| Net Interest | $407B | $944B | +$538B (+132%) |
| Customs Revenue | $36.3B | $189.7B | +$153B (+422%) |
| Income Security | $244B | $387B | +$143B (+58%) |
| Total Revenue | $3,696B | $5,101B* | +$1,405B (+38%) |

*\*FY2025 revenue estimated from CBO projection adjusted for customs above-baseline.*

Total real spending doubled, but the growth was highly uneven across functions. Three patterns stand out:

1. **Interest payments grew faster than any spending category** (+132%), driven by the post-2008 debt accumulation and post-2022 rate normalization. Net interest as a ratio to safety-net spending (income security + Medicaid) rose from 0.89 in FY2000 to 0.91 in FY2025—but this masks a dramatic V-shape, with the ratio falling to 0.19 in FY2021 (pandemic safety-net expansion + near-zero rates) before rebounding sharply.

2. **Customs revenue grew 422% in real terms** (from $36.3B to $189.7B in FY2024 dollars)—the most extreme growth of any revenue source. Note: throughout the paper, the nominal FY2025 customs figure is $195 billion; the real (FY2024 dollar) equivalent is $190 billion. The trajectory was essentially flat (≈1% of revenue) for FY2000–FY2018, then broke sharply upward with Section 301 tariffs (FY2019: 2.0%), and exploded to 3.7% with the 2025 Liberation Day tariffs.

3. **Income security grew just 58%**—far below the 109% increase in total spending—implying a declining share of the budget. The safety-net share of outlays (income security + Medicaid / total) was 14.1% in FY2000, spiked to 27.8% during the pandemic (FY2021), and has since reverted to 15.2%—only slightly above its level a quarter-century ago, despite a larger and older population.

### 3.2 Revenue Composition Shift

**Table 1b. Revenue Composition Shares, FY2000 vs. FY2025**

| Revenue Source | FY2000 Share | FY2025 Share | Change |
|---------------|-------------|-------------|--------|
| Progressive (income + corp. tax) | 59.8% | 57.1% | −2.7pp |
| Regressive (excise + customs + FICA) | 36.6% | 39.1% | +2.5pp |
| Customs alone | 1.0% | 3.7% | +2.7pp |

The federal revenue mix has gradually shifted toward more regressive sources. FICA (Social Security + Medicare payroll taxes) is the dominant regressive component, but customs—essentially zero as a policy tool for two decades—now contributes meaningfully. The regressive share peaked at 46.4% in FY2009 (when income-tax receipts collapsed during the Great Recession) and has fluctuated in the 34–42% range since. FY2025's 39.1% is within the historical band but at the upper end.

### 3.3 Income Distribution Trends (Census H-2 and CPS ASEC)

**Table 1c. Household Income Shares by Quintile, 2000 vs. 2023 (Census H-2)**

| Quintile | 2000 | 2023 | Change |
|----------|------|------|--------|
| Bottom 20% | 3.6% | 3.0% | −0.6pp |
| Second 20% | 8.9% | 8.0% | −0.9pp |
| Middle 20% | 14.8% | 14.0% | −0.8pp |
| Fourth 20% | 23.0% | 22.6% | −0.4pp |
| Top 20% | 49.8% | 52.4% | +2.6pp |
| Top 5% | 22.1% | 23.5% | +1.4pp |

Every quintile below the top lost income share. The bottom 50% share (Q1 + Q2 + ½ × Q3) fell from 19.9% to 18.0%. The top 20% absorbed the entire shift, rising 2.6 percentage points.

CPS ASEC microdata for eight benchmark years confirm this pattern at the person level. The B50 income share (person-weighted, using the PSZ pretax income concept) was 5.1% in CY2002 and rose slightly to 6.1% in CY2023—a modest gain that reflects growing Social Security and transfer payments rather than market income gains. Transfer dependency among the B50, however, *declined* from 44.2% (CY2002) to 41.9% (CY2023), suggesting the bottom half became somewhat less reliant on the very programs now being cut.

### 3.4 Structural Break Tests

For each indicator, we fit an OLS linear trend to a pre-break training period and test whether the FY2025 realized value deviates significantly from the trend-predicted value. The z-score uses the proper out-of-sample prediction standard error:

$$z = \frac{y_{2025} - \hat{y}_{2025}}{\hat{\sigma} \sqrt{1 + \frac{1}{n} + \frac{(x_{2025} - \bar{x})^2}{\sum(x_i - \bar{x})^2}}}$$

where $\hat{\sigma}$ is the residual standard deviation from the training-period OLS, $n$ is the number of training observations, and the additional terms in the denominator account for parameter estimation uncertainty and leverage of the forecast point. This yields appropriately conservative z-scores relative to the naïve residual/σ̂ ratio. $|z| > 2.0$ corresponds to a structural break at approximately the 5% level. Two different training periods are used:

- **Customs share** and **regressive revenue share**: FY2000–FY2017 (18 observations), the pre-tariff-war period ending before Section 301 actions.
- **Interest/safety-net ratio** and **safety-net share**: FY2000–FY2024 excluding the COVID-distorted FY2020–FY2021 (23 observations), because the pandemic-era safety-net explosion and near-zero interest rates would dominate a shorter training window.

**Table 1d. Structural Break Test Results**

| Indicator | Training Period | OLS Slope | Intercept | Predicted FY2025 | Actual FY2025 | z-Score | Verdict |
|-----------|----------------|-----------|-----------|-----------------|--------------|---------|---------|
| Customs / total revenue | FY2000–2017 (n=18) | +0.067pp/decade | −12.28 | 1.20% | 3.72% | **25.8** | **STRUCTURAL BREAK** |
| Interest / safety-net ratio | FY2000–2024 excl. COVID (n=23) | −0.031/decade | 6.63 | 0.45 | 0.91 | **2.4** | **STRUCTURAL BREAK** |
| Regressive revenue share | FY2000–2017 (n=18) | −1.68pp/decade | 377.9 | 37.4% | 39.1% | 0.5 | Within trend |
| Safety-net share of outlays | FY2000–2024 excl. COVID (n=23) | +0.84pp/decade | −152.5 | 17.7% | 15.2% | −1.5 | Within trend |

*Full regression outputs (standard errors, R², residual diagnostics) are reported in Appendix C. Note: z-scores use the proper out-of-sample prediction SE formula, which attenuates all z-scores relative to the naïve residual/σ̂ ratio (e.g., customs z dropped from 34.8 to 25.8); all verdicts are unchanged.*

**Interpretation.** FY2025 is *both* a continuation of long-run structural forces *and* an unprecedented policy discontinuity, depending on which dimension is examined:

- **Customs revenue** is the clearest break: the z-score of 25.8 (using the proper prediction SE) is so extreme that the tariff-driven revenue spike cannot plausibly be attributed to any pre-existing trend. This is a policy regime change, not drift.
- **Interest crowding** also represents a break (z = 2.4): the combination of post-pandemic debt accumulation and rate normalization has pushed interest payments roughly double their trend-predicted level relative to safety-net spending.
- **Regressive revenue composition** and **safety-net budget share** are *within* their pre-existing trends (z = 0.5 and −1.5, respectively), meaning the FY2025 values, while concerning, are not statistically distinguishable from the trajectory established over the prior training periods.

This mixed picture frames the remainder of our analysis: the distributional consequences documented below reflect both a quarter-century of fiscal drift and a sharp FY2025 policy inflection, with the tariff channel driving the most dramatic departure from historical norms.

---

\newpage
## 4. The Aggregate Fiscal Shift in FY2025

### 4.1 Spending Relative to CBO Baseline

We compare actual FY2025 spending estimates against the CBO January 2025 baseline projection. The CBO baseline embodies current-law assumptions and thus provides a "no policy change" counterfactual.

**Table 2. FY2025 Spending: CBO Baseline vs. Actual Estimates**

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

### 4.2 Revenue: The Tariff Spike

Customs duties reached $195 billion in FY2025, compared with $77 billion in FY2024 (+153%) and a CBO baseline of $95 billion. The $100 billion above-baseline customs revenue results from Executive Order tariff actions:

| Date | Action | Scope |
|------|--------|-------|
| Feb 4, 2025 | China +10% (cumulative with Section 301) | ~$350B imports |
| Mar 4, 2025 | China additional +10% (new total +20%) | ~$350B imports |
| Mar 12, 2025 | Steel/aluminum 25% universal (Section 232) | ~$42B imports |
| Apr 2, 2025 | "Liberation Day" — 10% universal + reciprocal rates | All imports |
| Apr 25, 2025 | Auto tariff 25% (Section 232) | ~$282B imports |
| May 12, 2025 | U.S.–China Geneva: China rate reduced to 30% | ~$350B imports |

### 4.3 The Budget Composition Shift: FY2020 → FY2024

**Important context.** FY2020 is a pandemic-distorted base year in which emergency programs (CARES Act, Consolidated Appropriations Act) temporarily inflated federal income security spending to $1,051 billion—nearly triple the pre-pandemic FY2019 level of $486 billion. These programs included the $600/week Federal Pandemic Unemployment Compensation (FPUC), expanded SNAP emergency allotments, Economic Impact Payments, and emergency rental assistance. Any FY2020→FY2024 comparison therefore conflates the mechanical expiration of these one-time programs with ongoing policy changes. We present this window because FY2020 is the most recent year for which comprehensive real-dollar comparison data are available, but readers should interpret the income security decline as overwhelmingly a pandemic-program expiration event, not a baseline spending cut.

**Table 3. Federal Outlay Reallocation (Real FY2024 Dollars)**

| Category | FY2020 | FY2024 | Change |
|----------|--------|--------|--------|
| Net Interest | $345B | $880B | +$534B (+155%) |
| Social Security | $1,090B | $1,454B | +$364B (+33%) |
| Discretionary | $1,628B | $1,810B | +$182B (+11%) |
| Medicaid | $458B | $618B | +$159B (+35%) |
| Veterans | $122B | $192B | +$70B (+57%) |
| Income Security | $1,051B* | $370B | −$681B (−65%) |

*\*FY2020 income security includes ~$565B in one-time pandemic programs (FPUC, EIPs, emergency SNAP). Pre-pandemic FY2019 level: $486B. Interest growth driven by rate normalization + debt accumulation. Medicaid decline reflects unwinding of continuous enrollment. Veterans increase from PACT Act expansion.*

The two starkest movements over this four-year window—net interest (+$534B) and income security (−$681B)—are both dominated by the pandemic and its aftermath rather than by discretionary FY2025 policy choices. The $681 billion income security decline is almost entirely attributable to the expiration of emergency COVID-era programs from the $1,051 billion pandemic peak. Nevertheless, the FY2024 level ($370B) is 24% below the pre-pandemic FY2019 level ($486B) in nominal terms, indicating that post-pandemic normalization has overshot the pre-crisis spending trajectory. This residual shortfall—approximately $116B below the pre-pandemic nominal baseline—does reflect real fiscal tightening for transfer-dependent households.

### 4.4 Interest Payments vs. the Safety Net

By FY2024, net interest ($880B) had reached 89.1% of combined income security plus Medicaid spending ($988B). In FY2025, net interest rose further to $980B—exceeding combined income security and Medicaid ($930B, 105.4%)—a threshold not crossed since the pre–New Deal era. As a share of GDP, interest rose from 1.6% (FY2020) to 3.2% (FY2025)—the highest level since the early 1990s. The 30-year Treasury yield reached 4.70% (+0.62pp since January 2024), directing federal dollars to bondholders whose holdings are concentrated among institutional investors and the top decile of household net worth—who hold approximately 67% of bonds and fixed-income securities (Federal Reserve 2023 SCF; Batty et al. 2019).

### 4.5 Interrupted Time Series

We estimate ITS models around key policy dates using Newey-West (HAC) standard errors to correct for serial correlation in the quarterly data (lag length $L = \lfloor 0.75 \cdot T^{1/3} \rfloor$ following Schwert 1989). With only 3–4 post-intervention quarterly observations for each event, these estimates are severely underpowered by the standards of the ITS literature (Bernal, Cummins & Gasparrini 2017 recommend 8–12 post-intervention points); results should be interpreted as suggestive rather than definitive:
- **Social benefits around January 20, 2025:** Positive level shift (HAC p = 0.026) but negative trend change (−39.1/quarter, HAC p = 0.095), suggesting decelerating growth following automatic COLA adjustments.
- **CPI around April 2, 2025 (Liberation Day):** Structural shift detected (HAC p = 0.008), though the measured effect was attenuated by simultaneous gasoline price declines.

*Note: The p-values above use heteroskedasticity- and autocorrelation-consistent (HAC) standard errors. Pre-correction OLS p-values were substantially smaller, indicating the importance of the serial correlation adjustment.*

---

\newpage
## 5. The Income Distribution: Baseline from CPS ASEC

### 5.1 Income Shares (PSZ Framework)

**Table 4. National Income Shares, CY2023**

| Group | Market Income | Pretax Income | Post-Tax Income | Capital Income |
|-------|-------------- |--------------|-----------------|---------------|
| Bottom 50% | 6.7% | 11.1% | 12.0% | −0.1% |
| Middle 40% | 48.6% | 47.3% | 48.1% | 9.0% |
| Top 10% | 44.7% | 41.6% | 39.9% | 91.1% |
| Top 1% | 13.0% | 11.9% | 11.1% | 42.8% |

The bottom 50% earns 6.7% of market income but receives 12.0% of post-tax income—the difference is entirely attributable to the government transfer system. This makes the B50 uniquely exposed to changes in means-tested spending: the transfer system is the mechanism that doubles their share of national income.

### 5.2 Quintile Income and Transfer Profile

**Table 5. Income and Transfer Receipt by Quintile (Person-Weighted)**

| Quintile | Mean Pretax | Mean Means-Tested | Eff. Tax Rate | SSI Receipt | EITC Mean |
|----------|------------|-------------------|---------------|-------------|-----------|
| Q1 (Bottom 20%) | $396 | $1,606 | 153%* | 6.4% | $108 |
| Q2 | $15,826 | $944 | 7.1% | 3.3% | $329 |
| Q3 | $35,619 | $421 | 11.2% | 0.6% | $269 |
| Q4 | $62,473 | $258 | 14.8% | 0.2% | $23 |
| Q5 (Top 20%) | $167,416 | $198 | 19.7% | 0.1% | $1 |

*\*Q1 effective rate >100% reflects net recipient status (credits exceed income).*

**Propensity validation.** CPS ASEC receipt rates confirm that means-tested transfers are concentrated in the bottom quintiles: SSI receipt is 64:1 (Q1 vs. Q5), public assistance 16:1, and EITC 329:1 in average dollar terms. This validates our HIGH propensity classification for income security programs and demonstrates that spending cuts to these programs are almost exclusively borne by the bottom half of the distribution.

### 5.3 Inequality Measures

- **Gini coefficient (pretax):** 0.587 [95% bootstrap CI: 0.584–0.591, n = 500]
- **Bottom 50% income share:** 11.12% [95% CI: 10.96–11.29]
- **Top 10% / Bottom 50% income ratio:** 18.7:1

---

\newpage
## 6. Distributional Impact of FY2025 Spending Cuts

### 6.1 Methodology

We attribute the $188 billion spending gap to income quintiles using program-specific distributional weights derived from CPS ASEC receipt data and Congressional Research Service benefit allocation estimates:

- **Medicaid (−$36B):** 40% Q1, 30% Q2, 15% Q3, 10% Q4, 5% Q5
- **Income Security (−$53B):** 50% Q1, 30% Q2, 12% Q3, 6% Q4, 2% Q5
- **Nondefense Discretionary (−$95B):** 25% Q1, 25% Q2, 22% Q3, 18% Q4, 10% Q5

### 6.2 Results

**Table 6. Distributional Impact by Quintile**

| Quintile | Spending Cuts | Tariff Burden† | Total Impact | Per Person | % of Pretax Income |
|----------|-------------|---------------|-------------|-----------|-------------------|
| Q1 (Bottom 20%) | −$64.7B | −$14.0B | −$78.7B | −$1,440 | 363.3%* |
| Q2 | −$50.4B | −$21.0B | −$71.4B | −$1,308 | 8.3% |
| Q3 | −$32.7B | −$30.8B | −$63.5B | −$1,162 | 3.3% |
| Q4 | −$23.9B | −$37.8B | −$61.7B | −$1,129 | 1.8% |
| Q5 (Top 20%) | −$12.4B | −$36.4B | −$48.8B | −$893 | 0.5% |

*†Tariff burden from Section 7, using CEX expenditure weights and Amiti et al. (2019) pass-through assumption.*  
*\*Q1 percentage reflects near-zero denominator (mean pretax income $396).*

**Bottom 50% summary:** Total spending cuts borne = $131.4B; tariff consumer burden borne = $50.4B; per-person combined loss = $1,331. The B50 is defined as Q1+Q2+0.5×Q3 of CPS ASEC person-income quintiles (136.6M persons, exactly 50% of the population). See Section 2.4 for the distinction between CPS person-income quintiles (used here) and CEX household-income quintiles (used for tariff expenditure shares in Section 7).

### 6.3 Pattern

The spending-cut channel is strongly progressive in incidence: Q1 bears 35% of the impact while earning less than 1% of pretax income. The tariff channel is regressive in absolute terms (Q5 pays the most dollars) but strongly regressive as a share of income. The combined effect is monotonically regressive: the per-person burden falls from $1,440 (Q1) to $893 (Q5), and far more steeply when expressed as a share of income.

---

\newpage
## 7. Tariff Incidence: Prices, Spending, and the B50 Burden

### 7.1 Did Prices Rise in Tariff-Affected Categories?

**Table 7. CPI Price Changes in Tariff-Affected Consumer Goods (FRED, through January 2026)**

| Category | Eff. Tariff Rate | Pre-Tariff YoY | Post-Tariff YoY | Acceleration | Tariff-Period Bump |
|----------|-----------------|----------------|-----------------|-------------|-------------------|
| Consumer Electronics | 10–145% | −6.05% | +1.57% | **+7.61pp** | +1.61% |
| Household Furnishings | 10–145% | +0.48% | +3.93% | **+3.46pp** | +3.19% |
| Toys and Games | 10–145% | +3.71% | +5.54% | **+1.84pp** | +3.65% |
| Footwear | 10–145% | +1.03% | +1.95% | +0.93pp | +0.15% |
| New Vehicles | 25% | −0.34% | +0.37% | +0.71pp | +0.30% |
| Apparel | 10–145% | +1.32% | +0.60% | −0.72pp | +0.26% |
| Food at Home | 10–25% | +1.84% | +2.18% | +0.33pp | +1.62% |
| Food Away from Home | 5–15% | +3.38% | +3.98% | +0.60pp | +2.95% |
| Alcoholic Beverages | 10–25% | +1.39% | +2.00% | +0.61pp | +1.35% |
| Used Vehicles | 0% | +0.93% | −1.96% | −2.89pp | +1.82% |
| Gasoline | 10–25% | −0.13% | −7.49% | −7.37pp | −4.54% |
| **Headline CPI-U** | **—** | **2.99%** | **2.39%** | **−0.60pp** | **—** |

**Statistical test.** High-tariff goods (>15% effective rate) saw mean acceleration of +2.30pp vs. −1.46pp for low-tariff goods, a 3.76 percentage-point differential. The Spearman rank correlation between tariff rate and price acceleration is **ρ = 0.684 (p = 0.020)**, providing statistically significant evidence (at the 5% level) that tariff-exposed goods experienced above-trend price increases.

Consumer electronics—the most China-dependent category—showed the largest price reversal: from 6.1% annual deflation to 1.6% inflation, a 7.6pp swing consistent with the 30–145% China tariff rate. Household furnishings and toys (also China-heavy) showed 3.2% and 3.7% tariff-period bumps. Gasoline fell due to global oil dynamics and partially offsets the consumer burden.

**Services control group test.** To isolate tariff-driven price effects from broader macroeconomic inflation trends, we compare price acceleration in tariff-affected traded goods against a control group of five non-tradable CPI service categories: medical care (CPIMEDSL), shelter (CUSR0000SAH1), education (CPIEDUSL), services less energy (CUSR0000SASLE), and transportation services (CUSR0000SAS4). These services are effectively non-tradable and therefore unaffected by customs tariffs, serving as a within-economy counterfactual following the identification strategy of Amiti et al. (2019).

**Table 7b. CPI Acceleration: Traded Goods vs. Services**

| Group | Acceleration | n |
|-------|-------------|---|
| Traded goods | **+1.66pp** | 8 |
| Non-tradable services | **−1.78pp** | 5 |
| **Differential** | **+3.44pp** | |

*Tests: Welch's t = 2.044 (p = 0.072\*); Mann-Whitney U = 35.0 (p = 0.015\*\*); Cohen's d = 1.26. \*p < 0.10, \*\*p < 0.05.*

The results are striking: traded goods experienced a mean price acceleration of +1.66pp while non-tradable services actually **decelerated** by −1.78pp over the same period, yielding a traded-minus-services differential of +3.44pp. This rules out the alternative hypothesis that the observed price increases in tariff-exposed goods merely reflect broader inflationary pressure—if anything, background inflation was decelerating. The Mann-Whitney U test rejects the null of equal distributions at the 5% level (p = 0.015), and Cohen’s d of 1.26 indicates a very large effect size. The Welch’s t-test, which is conservative given the small sample, is significant at the 10% level (p = 0.072). Together with the within-goods Spearman test (ρ = 0.684), the services control group provides complementary identification: the Spearman test establishes a dose-response relationship *within* traded goods, while the services comparison controls for economy-wide inflation trends *across* sectors. This pattern is consistent with the retrospective consensus that 2018–19 tariffs were passed through near-completely to domestic prices (Leibovici & Dunn, 2025), applied here at a substantially larger scale.

### 7.2 Expenditure Shares and Tariff Burden by Quintile

**Table 8. Tariff Burden by Income Quintile (CEX 2023)**

| Quintile | Annual Tariff Cost per CU | As % of After-Tax Income |
|----------|--------------------------|--------------------------|
| Q1 (Bottom 20%) | $155 | 1.05% |
| Q2 | $193 | 0.57% |
| Q3 | $237 | 0.43% |
| Q4 | $300 | 0.35% |
| Q5 (Top 20%) | $512 | 0.28% |

**Regressivity ratio: 3.8×** (Q1 burden as % of income / Q5 burden as % of income). The largest cost drivers for the bottom quintile are food at home ($71/yr), food away from home ($66/yr), household furnishings ($21/yr), and used vehicles ($23/yr)—necessities with high import content. Gasoline provided a partial offset (−$56/yr).

### 7.3 B50 Share of Tariff Revenue

**Table 9. Tariff Revenue Attribution**

| Measure | Value |
|---------|-------|
| Total tariff-weighted consumer spending | $451.7B |
| **Bottom 50% share (CEX household-income calibration)** | **51.7%** |
| Q1+Q2+Q3 share (40.6% of persons) | 42.2% |
| Top 20% share | 34.7% |
| B50 paid of $195B total tariff revenue | **$100.9B** |
| B50 paid of $100B above CBO baseline | **$51.7B** |
| Per person (B50 pop = 136.6M) | $739 (total) / $379 (above baseline) |
| As % of B50 mean pretax income ($12,526) | 5.9% / 3.0% |

*The 51.7% tariff share is computed using the CEX household-income calibration (Q1+Q2+Q3+0.414×Q4; see Section 2.4), which correctly captures 50% of persons by household income rank. Per-person figures use the B50 population of 136.6M (50% of the CPS ASEC 2024 population). Sensitivity range: 42.2% (Q1+Q2+Q3 only) to 65.3% (Q1+Q2+Q3+Q4).*

The B50’s 51.7% tariff revenue share exceeds their 23.0% share of aggregate household pretax income (under the household-income ranking used for CEX mapping) by a factor of 2.2, confirming tariffs as a deeply regressive fiscal instrument. Under the PSZ person-level income ranking, B50 holds 11.1% of pretax income, yielding a regressivity factor of 4.7×.

---

\newpage
## 8. Welfare Analysis

### 8.1 CRRA Welfare Weighting (σ = 2)

Using a constant relative risk aversion utility function with σ = 2, we compute welfare-equivalent losses by quintile using mean post-tax income as the consumption proxy. The welfare weight for Q1 exceeds Q5 by a factor of approximately 11,000, reflecting the high marginal utility of income at very low consumption levels and making the Q1 welfare loss orders of magnitude more consequential.

### 8.2 Simulated Distributional Burden by Percentile

Using CPS ASEC 2024 microdata (115,836 persons), we simulate the policy burden at each income percentile under assumed incidence parameters. **This is a parametric simulation exercise, not a statistical estimation of quantile treatment effects (QTE) in the Bitler-Gelbach-Hoynes (2006) or Firpo (2007) sense.** The exercise uses the following assumed parameters: SNAP receipt probability declining linearly from 30% at the bottom to 0% at the 75th percentile; Medicaid receipt declining from 40% to 0% at the 80th percentile; average SNAP benefit $2,800/yr (15% cut); Medicaid value $8,000/enrollee (5.8% cut); tariff consumer burden $140B ($100B revenue × 1.4 DWL). Sensitivity to these assumptions is tested in Section 10.

**Table 10. Simulated Policy Burden Across the Income Distribution**

| Percentile | Mean Income | Per-Person Loss | % of Income |
|-----------|------------|----------------|-------------|
| p5 | $0 | $1,209 | — |
| p20 | $5,342 | $1,057 | 19.8% |
| p30 | $16,326 | $957 | 5.9% |
| p50 (Median) | $35,625 | $755 | 2.1% |
| p70 | $61,497 | $553 | 0.9% |
| p90 | $128,195 | $401 | 0.3% |
| p99 | $671,160 | $347 | <0.1% |

**Regressivity gradient:** The policy burden at the 20th percentile (19.8% of income) is **approximately 383 times** that at the 99th percentile (<0.1% of income).

### 8.3 SPM Poverty Impact Simulation

**Table 11. Poverty Simulation Under SNAP Reduction Scenarios**

| Scenario | SPM Rate | Change | Additional Persons |
|----------|---------|--------|--------------------|
| Baseline | 12.70% | — | — |
| 10% SNAP cut | 12.78% | +0.08pp | +209,494 |
| 25% SNAP cut | 12.89% | +0.19pp | +517,170 |
| 50% SNAP cut | 13.11% | +0.41pp | +1,117,918 |
| 15% all food programs | 12.86% | +0.16pp | +424,712 |
| 30% all food programs | 13.05% | +0.35pp | +947,347 |

A 25% SNAP reduction—consistent with proposed FY2025 appropriations—pushes an estimated 517,000 additional persons below the SPM poverty line. These estimates are directionally consistent with independent modeling by the Budget Lab at Yale (2026), which finds that the 2025 tariff regime alone significantly erodes purchasing power at the bottom of the distribution when mapped onto SPM thresholds via PCE price effects. Our combined-channel estimates (spending cuts + tariffs) imply larger impacts than either channel in isolation.

---

\newpage
## 9. Geographic Heterogeneity: State Exposure Index

Following Fajgelbaum et al. (2020), we construct a composite state-level exposure index using four dimensions: transfer dependency (35% weight), capital income share (15%), bottom-50% income level (30%), and Gini coefficient (20%).

**Table 12. State Exposure Classification**

| Classification | States (exposure score) |
|---------------|------------------------|
| **High Exposure** | Mississippi (1.86), Louisiana (1.60), West Virginia (1.40), New Mexico (1.36), Kentucky (0.91), South Carolina (0.84), Alabama (0.81), Arkansas (0.72), Florida (0.70) |
| **Low Exposure** | DC (−1.78), South Dakota (−1.38), Vermont (−1.16), Minnesota (−1.05), North Dakota (−0.96), New Hampshire (−0.89), Wisconsin (−0.86) |

High-exposure states are concentrated in the Deep South and Appalachia—regions with high transfer dependency, low median incomes, and high inequality. This geographic pattern provides the foundation for synthetic difference-in-differences estimation when post-treatment ASEC data becomes available (September 2026).

---

\newpage
## 10. Robustness

**Table 13. Robustness Battery (6 Dimensions, 21 Distinct Specifications + 500 Bootstrap Draws)**

| Test | Specs | Passed | Detail |
|------|-------|--------|--------|
| Propensity Classification | 4 | ✓ | B50 loss range: $108B–$135B, all negative |
| Tariff Pass-Through | 6 | ✓ | B50 per-person: $132–$527 |
| CBO Baseline Uncertainty | 5 | ✓ | All scenarios show spending below baseline |
| Alternative Deflators | 5 | ✓ | Income security decline >70% under all |
| Bootstrap CIs (n=500, clustered by HH) | 500† | ✓ | B50 share: 11.12% [10.96, 11.29] |
| Placebo (FY2019) | 1 | ✓ | FY2019 gap ≈ $0B vs. FY2025 gap −$404B |

*†Bootstrap draws provide confidence intervals for a single distributional estimate and should not be counted as independent analytical specifications. The 21 distinct specifications span 6 robustness dimensions. Bootstrap resampling is clustered at the household level (PH_SEQ) to preserve within-household correlation.*

---

\newpage
## 11. Combined Fiscal Burden on the Bottom 50%

**Table 14. Total FY2025 Fiscal Impact on the Bottom 50% (Q1+Q2+0.5×Q3 of CPS person-income quintiles; 136.6M persons)**

| Channel | B50 Burden | Per Person | % of Pretax Income |
|---------|-----------|-----------|-------------------|
| Spending cuts (below CBO baseline) | $131.4B | $962 | 7.7% |
| Tariff consumer burden ($140B, DWL-inclusive) | $50.4B | $369 | 2.9% |
| **Combined** | **$181.8B** | **$1,331** | **10.6%** |

*B50 defined as Q1+Q2+0.5×Q3 of CPS ASEC person-income quintiles (each quintile = 20% of persons; B50 = exactly 50% of persons = 136.6M). B50 mean pretax income = $12,526 per person (CPS ASEC 2024). Tariff consumer burden assumes 100% pass-through with 1.4× DWL factor following Amiti et al. (2019). Sensitivity to pass-through and DWL assumptions tested in Section 10 (B50 per-person range: $132–$527). The CEX-based tariff expenditure share (51.7%, Section 7.3) is computed using a separate household-income quintile calibration (Q1+Q2+Q3+0.414×Q4) appropriate for CEX's unequal-person-share quintiles.*

For context, B50 mean pretax income is $12,526 (CPS ASEC 2024 person-level). The combined fiscal burden of 10.6% of pretax income represents a substantial reduction in real living standards for the bottom half of the population—exceeding all means-tested transfer income ($1,111/person) that separates the B50 from their market income baseline.

Simultaneously, net interest payments ($980B in FY2025) flow overwhelmingly to bondholders in the top decile—who hold approximately 67% of bonds and fixed-income securities (Federal Reserve 2023 SCF)—and the S&P 500 has risen 80.7% since January 2023—gains accruing primarily to the top 10%, who hold 93% of equities (Federal Reserve 2023 SCF; up from 89% in the 2019 SCF per Bricker, Goodman & Moore 2020). The FY2025 fiscal configuration thus effects a large transfer from the bottom to the top of the income distribution through three reinforcing channels.

---

\newpage
## 12. Policy Scenario: Judicial Revocation and Legislative Tariff Replacement

*Added February 21, 2026, in response to the Supreme Court's decision in* Learning Resources, Inc. v. Trump*, No. 24-1287 (S. Ct. Feb. 20, 2026), and the administration's subsequent announcement of replacement tariffs.*

### 12.1 Motivation and Assumptions

On February 20, 2026, the Supreme Court held 6-3 in *Learning Resources, Inc. v. Trump*, No. 24-1287 (consolidated with *Trump v. V.O.S. Selections*, No. 25-250), that the International Emergency Economic Powers Act (IEEPA, 50 U.S.C. §1702) does not authorize the President to impose tariffs (Roberts, C.J., delivering the opinion of the Court; Gorsuch and Barrett, JJ., concurring; Thomas, J., dissenting, joined by Kavanaugh and Alito, JJ.). The ruling vacated all IEEPA-based tariffs, including the "Liberation Day" reciprocal tariffs (April 2, 2025), the "trafficking tariffs" on Canada, Mexico, and China (February–March 2025), and additional IEEPA levies on Brazil and India. Section 232 tariffs on steel, aluminum, automobiles, copper, and lumber—imposed under the Trade Expansion Act of 1962—remain unaffected by the ruling (AP, Grantham-Philips, Feb. 20, 2026).

Federal data reported by the Associated Press indicates that Treasury collected more than $133 billion under IEEPA tariff authority as of December 2025 (Price, AP, Feb. 21, 2026). The ruling raises the question of refunds to importers, though the Court did not explicitly order refund procedures.

On the same day, the President signed an executive order under Section 122 of the Trade Act of 1974 imposing a 10% global baseline tariff effective February 24, 2026, subject to a statutory 150-day limit absent Congressional extension. On February 21, 2026, the President announced via Truth Social that he intends to raise the replacement tariff to 15% globally (Price, AP, Feb. 21, 2026). Congressional legislation would be required to make any rate above the Section 122 temporary authority permanent.

This section uses the paper's established distributional framework to model the welfare effects on the bottom 50% (B50) of the revocation and replacement scenarios, holding all other fiscal parameters at their FY2025 values.

**Key assumptions:**

- **Import base:** $3,100B in total U.S. goods imports (Census Bureau 2024)
- **Replacement tariff rate:** 15% uniform on all goods (announced target)
- **Import demand elasticity:** −1.0 (Fajgelbaum et al. 2020)
- **Deadweight loss factor:** 1.4× tariff revenue (Amiti et al. 2019)
- **Trade volume reduction:** 13.0% central estimate (sensitivity: 5–15%)
- **IEEPA refund liability:** $133B+ (AP-reported Treasury collections as of December 2025), financed via debt at 4.5% marginal rate
- **B50 tariff expenditure share:** 33.2% (CPS person-income quintiles: Q1+Q2+0.5×Q3 of CEX expenditure shares)
- **Price stickiness assumption:** Retail prices do not adjust downward upon tariff revocation (see Section 12.2)
- **All other variables held constant** (spending cuts, transfer levels, interest payments exclusive of refund)

### 12.2 Revocation-Only Scenario: Price Stickiness and the Incidence of Relief

A critical distinction determines who benefits from tariff revocation: whether retail prices adjust downward when import costs fall.

**The standard textbook assumption** is that tariff removal reverses the price increase—import costs fall, and competition drives retail prices back to pre-tariff levels. Under this assumption, the $140B DWL-inclusive consumer burden (Section 7) would be eliminated, providing B50 with $50.4B in relief ($369/person).

**However, under the "all other things being equal" assumption** — which the empirical literature on price stickiness supports as the more realistic near-term scenario — tariff revocation does *not* reduce the consumer welfare loss. The reasoning is as follows:

1. **Sunk welfare loss.** The FY2025 tariff burden has already been realized. Consumers have already paid elevated prices throughout the tariff period. Revocation cannot undo the welfare loss already incurred.

2. **Forward-looking price stickiness.** If retailers and importers do not reduce prices after tariff revocation — as extensive evidence on asymmetric price adjustment suggests is the short-run norm (Peltzman, 2000; Cavallo, 2018) — consumers continue to face the same elevated prices. The tariff wedge previously captured by Treasury as customs revenue instead accrues to importer and retailer profit margins. The consumer burden is unchanged; only its destination shifts from government to corporations.

3. **Refunds flow to importers, not consumers.** The $133B+ in IEEPA collections refunded by Treasury goes to the importers who paid customs duties at the border — not to the end consumers who bore the burden through higher retail prices. This constitutes a corporate windfall, debt-financed by the federal government.

4. **Revenue loss creates fiscal pressure.** The government loses approximately $100B per year in above-baseline tariff revenue (FY2025 basis). This revenue gap either widens the deficit or forces additional spending adjustments — both of which disproportionately affect B50 through the spending-cut channel already documented in Section 6.

Under price stickiness, the revocation-only scenario produces:

| Channel | B50 Burden | Per Person | % of Pretax Income |
|---------|-----------|-----------|-------------------|
| Spending cuts (unchanged) | $131.4B | $962 | 7.7% |
| Tariff consumer burden (unchanged; flows to corporate margins) | $50.4B | $369 | 2.9% |
| **Combined (revocation only)** | **$181.8B** | **$1,331** | **10.6%** |
| *Net B50 relief vs. status quo* | *$0* | *$0* | *0.0pp* |

**Additional fiscal costs of revocation:**

- **Refund debt:** $133B+ added to national debt → approximately $6.0B per year in interest at 4.5%
- **Interest distribution:** Top-decile households hold 67% of bonds (Federal Reserve 2023 SCF) → approximately $4.0B per year of refund interest flows to wealthy bondholders
- **Revenue gap:** $100B per year in lost above-baseline customs revenue, increasing deficit pressure

The central finding is that under realistic price stickiness, tariff revocation provides **zero consumer relief** to B50 while generating a $133B+ windfall to importers and costing the government $6B per year in perpetual interest payments. The FY2025 consumer welfare loss ($140B DWL-inclusive) is a sunk cost that revocation cannot reverse, and the forward-looking burden persists until competitive pressure or deliberate repricing erodes the legacy tariff markup — a process that empirical evidence suggests takes 12–24 months at minimum for traded goods (Gopinath, Itskhoki & Rigobon, 2010). Figure 40 diagrams the incidence flow under price stickiness.

### 12.3 15% Universal Legislative Tariff

A 15% uniform tariff on the full $3,100B goods import base generates substantially higher revenue than the targeted executive tariffs it replaces. We model three scenarios to bracket uncertainty in trade elasticity and the effective import base:

**Table 15a. Legislative Tariff Revenue and Burden Estimates**

| Parameter | Low | Central | High |
|-----------|-----|---------|------|
| Effective import base | $1,705B (FTA-exempt) | $3,100B (full) | $3,100B (full) |
| Trade volume reduction | 15% | 13.0% | 5% |
| Tariff revenue | $217.4B | $404.3B | $441.8B |
| Consumer burden (1.4× DWL) | $304.3B | $566.1B | $618.4B |
| B50 tariff burden | $101.2B | $188.2B | $205.6B |

*Low scenario assumes FTA-partner imports exempted and high elasticity response; Central assumes full import base with moderate behavioral response (ε = −1.0); High assumes minimal trade adjustment (ε ≈ −0.35). The 1.4× DWL multiplier follows Amiti et al. (2019).*

Even under the Low scenario, the consumer burden ($304.3B) more than doubles the status quo ($140B). Under the Central scenario, the consumer burden quadruples to $566.1B, reflecting the far broader base of a universal tariff compared to the category-specific executive tariffs.

### 12.4 Combined Scenario: Revocation + Replacement Tariff

Under price stickiness, the combined scenario compounds the burdens. The old IEEPA-era tariff markup remains embedded in retail prices (Section 12.2), and the new 15% tariff adds further cost on goods not previously covered or where the new rate exceeds the legacy markup. Our combined estimates therefore represent a **conservative lower bound** under price stickiness, because they model the 15% tariff as a standalone replacement rather than as additive to residual sticky markups.

Table 15b presents the combined impact, with refund debt-service costs incorporated:

**Table 15b. Status Quo vs. Combined Scenario: B50 Distributional Impact**

| Metric | Status Quo | Low | Central | High |
|--------|-----------|-----|---------|------|
| Tariff revenue ($B) | $195 | $217 | $404 | $442 |
| Consumer burden ($B) | $140 | $304 | $566 | $618 |
| B50 combined burden ($B) | $181.8 | $232.6 | $319.6 | $337.1 |
| B50 per person ($) | $1,331 | $1,703 | $2,341 | $2,468 |
| B50 % of pretax income | 10.6% | 13.6% | 18.7% | 19.7% |
| Net fiscal change vs. FY2025 | — | +$16.4B/yr | +$203.4B/yr | +$240.8B/yr |

*Net fiscal change accounts for the $6.0B/yr interest on refund debt ($133B at 4.5%).*

Under the Central scenario, the B50 combined burden increases by $137.8B (+76%) to $319.6B—equivalent to $2,341 per person or 18.7% of pretax income (Figure 38). This nearly doubles the status quo burden share and exceeds B50 mean transfer income ($1,111/person) by a factor of 2.1. Under price stickiness (Section 12.2), these figures are conservative: residual IEEPA-era markups on goods where the legacy tariff exceeded 15% persist as corporate margins on top of the new tariff burden.

**Table 15c. Quintile Detail, Central Combined Scenario**

| Quintile | Spending Cuts | New Tariff | Total | Per Person | % Pretax Income |
|----------|--------------|------------|-------|-----------|----------------|
| Q1 (bottom 20%) | $64.7B | $58.9B | $123.5B | $2,261 | 571.0%* |
| Q2 | $50.5B | $79.0B | $129.4B | $2,369 | 15.0% |
| Q3 | $32.7B | $100.8B | $133.5B | $2,443 | 6.9% |
| Q4 | $23.9B | $130.9B | $154.8B | $2,833 | 5.5% |
| Q5 (top 20%) | $12.4B | $196.6B | $208.9B | $3,825 | 3.0% |

**Q1 percentage reflects near-zero mean pretax income ($396/person); expressed as a share of total income including transfers ($5,097/person), the burden is approximately 44.3%.* While Q5 pays the largest absolute amount ($208.9B total), the burden-to-income ratio is 190× higher for Q1 than for Q5 (Figure 39). The regressivity exceeds the status quo because a uniform 15% rate applied to all imports amplifies the consumption-tax character of tariffs relative to the category-specific executive tariffs.

### 12.5 Welfare Analysis

Under CRRA utility with σ = 2, welfare weights favor bottom quintiles in proportion to the concavity of utility at low income levels:

| Quintile | Welfare Weight (Q3 = 1.0) |
|----------|--------------------------|
| Q1 | 8,090 |
| Q2 | 5.07 |
| Q3 | 1.00 |
| Q4 | 0.47 |
| Q5 | 0.08 |

The welfare-weighted total loss increases by **57.0%** from the status quo to the Central combined scenario (Figure 41). The large Q1 welfare weight (reflecting the concavity of CRRA utility at very low incomes) means that the tariff burden increase on Q1—from $64.7B under the status quo to $123.5B under the combined scenario—drives the welfare deterioration despite Q1 being the smallest quintile in absolute dollar terms.

### 12.6 Fiscal Implications

The combined scenario presents a complex fiscal trade-off:

1. **Revenue gain:** The 15% tariff generates $404.3B (Central) vs. $195B under IEEPA tariffs—a gross increase of $209.3B per year.
2. **Interest cost:** Debt-financed refunds of IEEPA collections ($133B+) add approximately $6.0B per year in perpetuity.
3. **Net fiscal improvement:** +$203.4B per year (Central, net of refund interest), which could in principle narrow the deficit by approximately 11% against the $1,833B FY2025 deficit.

However, this revenue improvement comes at disproportionate cost to lower-income households. Each additional dollar of tariff revenue generates $1.40 in consumer burden (DWL-inclusive), and the burden is distributed regressively: B50 households bear 33.2% of the tariff burden while earning only 6.7% of pretax income.

Additionally, as established in Section 12.2, price stickiness means consumers bear the full burden of the new 15% tariff on top of any residual IEEPA-era markups that have not yet unwound. The primary beneficiaries of the transition period are importers, who receive $133B+ in refunds and capture the spread between falling import costs and sticky retail prices.

### 12.7 Caveats

This scenario analysis extends the paper's empirical framework to a rapidly-evolving policy configuration and carries additional uncertainties beyond those in Section 13:

1. **Trade elasticity uncertainty.** The 13% central trade reduction may understate or overstate behavioral response; the Low-to-High range ($232.6B–$337.1B in B50 combined burden) brackets this uncertainty.
2. **Retaliation not modeled.** Trading partners may impose retaliatory tariffs on U.S. exports, generating additional welfare losses through reduced export demand and terms-of-trade effects.
3. **General equilibrium effects.** Partial equilibrium analysis does not capture exchange rate adjustment, supply chain restructuring, or domestic production substitution that would unfold over multiple years.
4. **Legal pathway uncertain.** The initial 10% tariff uses Section 122 authority (150-day statutory limit). The announced 15% rate requires Congressional legislation or alternative executive authority; actual enacted policy may differ in rate, scope, or exemptions.
5. **Refund magnitude and mechanism uncertain.** The $133B+ figure is AP-reported Treasury IEEPA collections through December 2025; actual amounts including post-December collections, interest, and any judicial adjustments remain undetermined. The Court did not specify refund procedures.
6. **Price stickiness duration uncertain.** Our central assumption that prices do not adjust downward upon revocation is empirically grounded for the short run (Peltzman, 2000; Gopinath, Itskhoki & Rigobon, 2010), but prices may partially adjust over 12–24 months. The revocation-only scenario results should be interpreted as the near-term (0–12 month) outcome.
7. **Section 232 tariffs remain.** The SCOTUS ruling does not affect Section 232 tariffs on steel, aluminum, automobiles, copper, and lumber, which continue to impose consumer costs not modeled in this scenario's "revocation" component.
8. **Combined burden is a lower bound under stickiness.** If IEEPA-era markups persist while new 15% tariffs are also imposed, the consumer burden exceeds our standalone 15% estimates for goods where the legacy markup exceeds the new rate.

---

\newpage
## 13. Limitations

1. **FY2025 spending estimates.** The spending analysis uses CBO January 2025 baseline projections and partial-year Treasury MTS data available through the initial analysis period. Full-year MTS data for FY2025 (ending September 30, 2025) became available in October 2025; future work should reconcile these estimates against final actuals, though the aggregate spending gap (−$188B vs. CBO baseline) is consistent with independent reports.

2. **CPS ASEC 2024 reflects CY2023 income**—a pre-policy baseline, not the post-policy outcome. The ASEC 2025 (available September 2026) will provide the post-treatment comparison for formal difference-in-differences estimation.

3. **Causal identification is partial.** The CBO counterfactual provides the strongest identification for the spending gap. Tariff price effects are supported by two identification strategies—a within-goods Spearman dose-response (ρ = 0.684, p = 0.020) and a traded-goods-vs.-services control comparison (+3.44pp differential, Mann-Whitney p = 0.015)—but cannot fully separate tariff causality from other supply-side factors without product-level customs-to-retail matching.

4. **Post-pandemic normalization.** Income security declined from a pandemic peak ($1,051B in FY2020). Our FY2019 placebo (gap ≈ $0B vs. FY2025 gap −$404B) helps distinguish policy effects from normalization, but a formal panel DiD is needed for definitive causal claims.

5. **CPI acceleration is supportive but not definitive.** Product-level customs-to-retail matching (Cavallo et al., 2021) would provide cleaner tariff price identification than our category-level CPI approach.

6. **CEX-to-CPS mapping uses calibrated but not exact partitioning.** Our B50 tariff expenditure share (51.7%) uses the CEX household-income calibration (Q1+Q2+Q3+0.414×Q4), which correctly captures 50% of persons by household income rank in the CEX system (see Section 2.4). This differs from the CPS person-income B50 (Q1+Q2+0.5×Q3) used for spending-cut attribution (Section 6) and combined burden (Section 11), because CEX quintiles have unequal person shares while CPS person-income quintiles have equal shares by construction. Both definitions capture exactly 50% of persons, but in different income-ranking frameworks. The CEX mapping still uses published quintile means rather than CEX microdata partitioned at the exact 50th percentile. Linked CEX-CPS microdata, as in Attanasio, Hurst & Pistaferri (2015), would be more precise but is not publicly available at sufficient scale. Sensitivity bounds (Q1+Q2+Q3 through Q1+Q2+Q3+Q4, spanning 42.2–65.3% B50 tariff share) bracket the calibrated 51.7% estimate.

7. **Tariff pass-through identification.** Our difference-in-acceleration approach is validated by two complementary tests: a within-goods Spearman dose-response (ρ = 0.684, p = 0.020) and a services-as-control-group comparison showing traded goods accelerated +1.66pp while non-tradable services decelerated −1.78pp (Mann-Whitney p = 0.015). However, our category-level CPI approach cannot capture product-level heterogeneity. Scanner-data matching of customs duties to specific retail prices (Cavallo et al., 2021) would provide cleaner identification, as would formal panel DiD with product-level variation in tariff exposure.

8. **Gasoline price declines** are driven by global oil markets, not tariff policy, yet they partially offset the measured tariff burden.

---

\newpage
## 14. Conclusion

Embedding FY2025 within a quarter-century of fiscal data reveals a mixed picture: some dimensions of the current fiscal configuration are continuations of long-run structural trends, while others represent genuine policy discontinuities.

The overall shift toward more regressive federal revenue sources (+2.5pp over 25 years) and the secular compression of the bottom 50% income share (from 19.9% to 18.0% of household income) are trends that predate 2025 and would likely have continued under any administration. Similarly, the safety-net share of total outlays (15.2%) has returned to its pre-pandemic level after the COVID-era expansion—its z-score of −1.5 (predicted 17.7%) falls short of the 2.0 threshold, consistent with normalization rather than novel retrenchment, though the magnitude of the shortfall merits monitoring.

What *is* historically anomalous about FY2025 is the tariff channel. Customs revenue's jump from 1.0% to 3.7% of total federal revenue—a z-score of 25.8 against the pre-2018 trend (using the proper out-of-sample prediction SE)—constitutes the most dramatic single-year change in the federal revenue mix since the introduction of the income tax. The interest-crowding channel (z = 2.4) also represents a structural break, driven by post-pandemic debt accumulation and rate normalization pushing interest payments roughly double their trend-predicted level relative to safety-net spending.

The FY2025 fiscal configuration—spending cuts concentrated in means-tested programs, tariff escalation functioning as a regressive consumption tax, and rising interest payments flowing to top-decile bondholders—imposes a combined burden of approximately $1,331 per person on the bottom 50% of the income distribution (136.6M persons; Q1+Q2+0.5×Q3 of CPS person-income quintiles), equivalent to 10.6% of their pretax income. This burden is approximately 383 times larger as a share of income at the 20th percentile than at the 99th.

The Supreme Court's invalidation of IEEPA tariff authority on February 20, 2026 (*Learning Resources, Inc. v. Trump*, No. 24-1287) does not resolve the distributional burden on the bottom 50%. Under empirically grounded price stickiness (Peltzman, 2000; Cavallo, 2018), tariff revocation provides zero consumer relief: retail prices do not adjust downward, and the $133B+ in refunds flows to importers rather than consumers—constituting a debt-financed corporate windfall. The announced 15% universal legislative replacement, if enacted, would nearly double the B50 combined burden from $1,331 to $2,341 per person (Central estimate), with welfare-weighted losses increasing 57% (Section 12). The transition period thus compounds rather than alleviates the distributional consequences documented in this paper.

These findings are robust across 21 distinct analytical specifications spanning six robustness dimensions, with household-clustered bootstrap confidence intervals, and validated against CPS ASEC microdata spanning eight benchmark years (1.4 million person-records) confirming the structural transfer-dependence of the bottom 50%—whose market income share (6.7%) doubles to 12.0% only through the government programs being cut. The statistical evidence of tariff-to-price pass-through is supported by two complementary identification strategies: a within-goods Spearman dose-response (ρ = 0.684, p = 0.020) and a traded-goods-vs.-services comparison (+3.44pp differential, Mann-Whitney p = 0.015), consistent with the broader empirical literature (Amiti et al., 2019; Fajgelbaum et al., 2020; Cavallo et al., 2021).

When the CPS ASEC 2025 becomes available (September 2026), formal synthetic difference-in-differences estimation—following the staggered-adoption framework of Athey and Imbens (2023)—exploiting cross-state tariff and transfer exposure variation will enable causal identification. Until then, the evidence presented here—linking 26 years of fiscal accounting, structural break tests, validated distributional weights, realized price changes, and multiple robustness checks—constitutes the strongest available assessment of who bears the cost of both the long-run fiscal drift and the sharp 2025 inflection point.

---

## References

Amiti, M., Redding, S. J., & Weinstein, D. E. (2019). The impact of the 2018 tariffs on prices and welfare. *Journal of Economic Perspectives*, 33(4), 187–210.

Amiti, M., Redding, S. J., & Weinstein, D. E. (2020). Who's paying for the US tariffs? A longer-term perspective. *AEA Papers and Proceedings*, 110, 541–546.

Athey, S., & Imbens, G. W. (2017). The econometrics of randomized experiments. *Handbook of Economic Field Experiments*, 1, 73–140.

Athey, S., & Imbens, G. W. (2023). Design-based analysis in difference-in-differences settings with staggered adoption. *Journal of Econometrics*, 226(1), 62–79.

Attanasio, O., Hurst, E., & Pistaferri, L. (2015). The evolution of income, consumption, and leisure inequality in the US, 1980–2010. In *Improving the Measurement of Consumer Expenditures*. Chicago: University of Chicago Press.

Auerbach, A. J., & Gorodnichenko, Y. (2012). Measuring the output responses to fiscal policy. *American Economic Journal: Economic Policy*, 4(2), 1–27.

Batty, M., Bricker, J., Briggs, J., et al. (2019). Introducing the Distributional Financial Accounts of the United States. *Finance and Economics Discussion Series* 2019-017, Federal Reserve Board.

Benguria, F., & Saffie, F. (2025). Rounding up the effect of tariffs on financial markets. NBER Working Paper No. 34036.

Bernal, J. L., Cummins, S., & Gasparrini, A. (2017). Interrupted time series regression for the evaluation of public health interventions. *International Journal of Epidemiology*, 46(1), 348–355.

Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2006). What mean impacts miss: Distributional effects of welfare reform experiments. *American Economic Review*, 96(4), 988–1012.

Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2010). Distributional impacts of the Self-Sufficiency Project. *Journal of Public Economics*, 94(11–12), 781–793.

Bricker, J., Goodman, S., & Moore, K. B. (2020). Wealth and income concentration in the SCF: 1989–2019. *FEDS Notes*, Federal Reserve Board.

Cavallo, A. (2018). Scraped data and sticky prices. *Review of Economics and Statistics*, 100(1), 105–119.

Cavallo, A., Gopinath, G., Neiman, B., & Tang, J. (2021). Tariff pass-through at the border and at the store. *American Economic Review: Insights*, 3(1), 19–34.

Clausing, K. A., & Lovely, M. E. (2024). Why Trump's tariff proposals would harm working Americans. PIIE Policy Brief.

Clausing, K. A., & Obstfeld, M. (2025). Tariffs as fiscal policy. NBER Working Paper No. 34192.

Congressional Budget Office. (2022). The distribution of household income, 2019.

Fajgelbaum, P. D., Goldberg, P. K., Kennedy, P. J., & Khandelwal, A. K. (2020). The return to protectionism. *Quarterly Journal of Economics*, 135(1), 1–55.

Falkenheim, M. (2022). How changes in the federal budget affect the economy. CBO Working Paper.

Federal Reserve Board. (2023). Changes in U.S. family finances from 2019 to 2022: Evidence from the Survey of Consumer Finances. *Federal Reserve Bulletin*, 109(4).

Firpo, S. (2007). Efficient semiparametric estimation of quantile treatment effects. *Econometrica*, 75(1), 259–276.

Gopinath, G., Itskhoki, O., & Rigobon, R. (2010). Currency choice and exchange rate pass-through. *American Economic Review*, 100(1), 304–336.

Gopinath, G., & Neiman, B. (2026). The incidence of tariffs: Rates and reality. NBER Working Paper No. 34620.

Leibovici, F., & Dunn, J. (2025). What have we learned from the U.S. tariff increases of 2018–19? Federal Reserve Bank of St. Louis Review.

Minton, T., & Somale, M. (2025). Detecting tariff effects on consumer prices in real time. Federal Reserve FEDS Notes.

Peltzman, S. (2000). Prices rise faster than they fall. *Journal of Political Economy*, 108(3), 466–502.

Price, M. L. (2026, February 21). Trump says he'll raise tariffs to 15 percent after Supreme Court ruling. *Associated Press*.

Perese, K. (2017). CBO's new framework for analyzing the effects of means-tested transfers and federal taxes on the distribution of household income. CBO Working Paper 2017-09.

Piketty, T., Saez, E., & Zucman, G. (2018). Distributional national accounts: Methods and estimates for the United States. *Quarterly Journal of Economics*, 133(2), 553–609.

Schwert, G. W. (1989). Tests for unit roots: A Monte Carlo investigation. *Journal of Business & Economic Statistics*, 7(2), 147–159.

The Budget Lab at Yale. (2026). The effect of tariffs on poverty. Budget Lab Working Paper.

Wolff, E. N., & Zacharias, A. (2007). The distributional consequences of government spending and taxation in the US, 1989 and 2000. *Review of Income and Wealth*, 53(4), 692–715.

---

## Appendix A: Data Sources and Replication

| Source | Access Method | Files |
|--------|-------------|-------|
| FRED (48 series) | fredapi Python package | federal_budget.db |
| Treasury MTS | Fiscal Data API (REST) | federal_budget.db |
| CBO Historical Budget | Manual download + load_cbo_data.py | federal_budget.db |
| CPS ASEC 2024 | Census Bureau API (6 batches) | cps_asec_2024_microdata.csv |
| CPS ASEC Historical (8 yrs) | Census Bureau API | cps_asec_historical_quintiles.csv |
| Census H-2 (24 years) | Census Historical Income Tables | census_income_quintiles.csv |
| CBO 25-Year Trends | federal_budget.db extraction | cbo_25year_trends.csv |
| Derived 25-Year Series | Computed from CBO + Census | derived_25year_series.csv |
| BLS CEX 2023 | Published Table 1101 (hardcoded) | run_tariff_incidence_analysis.py |
| CPI Sub-Indices | FRED (12 series) | tariff_incidence_analysis.json |

All analysis scripts are available in the project repository:

| Script | Purpose |
|--------|---------|
| collect_historical_distribution.py | Census + CPS ASEC historical data (1.4M records) |
| run_25year_analysis.py | 26-year structural trend analysis, break tests |
| acquire_cps_asec.py | Census API microdata acquisition (115,836 persons) |
| run_real_analysis.py | Real-terms spending with propensity tagging |
| run_counterfactual_analysis.py | CBO counterfactual, distributional attribution, simulated burden by percentile, SPM |
| run_tariff_incidence_analysis.py | Tariff price, expenditure, and incidence analysis |
| run_robustness_checks.py | Six-dimension robustness battery (21 specs + bootstrap CIs) |
| generate_charts.py | Descriptive budget visualization (Figures 1–10) |
| generate_new_figures.py | Analytical figures (Figures 28–37) |
| generate_real_charts.py | Real-terms budget visualization (Figures 42–49) |
| run_scotus_tariff_scenario.py | SCOTUS revocation + 15% legislative tariff scenario (Section 12) |
| generate_scotus_figures.py | SCOTUS scenario figures (Figures 38–41) |


### B.1 Descriptive Budget Figures (FY2015–2025)

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

### B.2 Distributional Impact Figures

| Figure | Description | File |
|--------|-------------|------|
| 11 | Income distribution by quintile (CPS ASEC) | `fig1_income_distribution.png` |
| 12 | Distributional impact of FY2025 policy | `fig2_distributional_impact.png` |
| 13 | Simulated distributional burden curve | `fig3_quantile_treatment_effects.png` |
| 14 | SPM poverty simulation | `fig4_spm_poverty_simulation.png` |
| 15 | State exposure classification map | `fig5_state_exposure.png` |
| 16 | Welfare-weighted impact (CRRA σ=2) | `fig6_welfare_weighted_impact.png` |
| 17 | CPI price changes in tariff-affected goods | `fig7_tariff_price_changes.png` |
| 18 | Tariff burden by income quintile (absolute + % of income) | `fig8_tariff_burden_by_quintile.png` |
| 19 | B50 vs. T50 tariff cost by goods category | `fig9_b50_tariff_by_category.png` |

### B.3 26-Year Structural Trend Figures (FY2000–FY2025)

| Figure | Description | File |
|--------|-------------|------|
| 20 | Real spending composition (stacked area, FY2000–2025) | `25yr_spending_composition.png` |
| 21 | Revenue composition shares (stacked area, FY2000–2025) | `25yr_revenue_composition.png` |
| 22 | Interest vs. safety-net spending (25-year trajectory) | `25yr_interest_vs_safetynet.png` |
| 23 | Customs revenue trajectory (with tariff regime markers) | `25yr_customs_trajectory.png` |
| 24 | Income inequality evolution (Census quintile shares) | `25yr_inequality_evolution.png` |
| 25 | B50 transfer dependency and poverty (CPS ASEC benchmarks) | `25yr_poverty_and_benefits.png` |
| 26 | Structural break tests (4-panel: actual vs. trend) | `25yr_structural_breaks.png` |
| 27 | FY2025 context dashboard (6-panel summary) | `25yr_fy2025_context_dashboard.png` |

### B.4 Analytical Figures

| Figure | Description | File |
|--------|-------------|------|
| 28 | Burden decomposition by income percentile (stacked area) | `fig11_burden_decomposition.png` |
| 29 | Structural break prediction bands (forest plot) | `fig12_structural_break_bands.png` |
| 30 | Tariff pass-through: traded goods vs. services control | `fig13_services_price_acceleration.png` |
| 31 | B50 calibration diagram (quintile person shares) | `fig14_b50_calibration.png` |
| 32 | Robustness specification summary (6 dimensions) | `fig15_specification_curve.png` |
| 33 | CBO counterfactual waterfall (baseline to actual) | `fig16_counterfactual_waterfall.png` |
| 34 | Historical B50 income share and transfer dependency | `fig17_historical_b50.png` |
| 35 | Welfare-weighted loss (log-scale, CRRA σ=2) | `fig18_welfare_logscale.png` |
| 36 | State fiscal exposure index (dot plot) | `fig19_state_exposure_dots.png` |
| 37 | SPM poverty dose-response (food program scenarios) | `fig20_spm_dose_response.png` |

### B.5 SCOTUS Scenario Figures (Section 12)

| Figure | Description | File |
|--------|-------------|------|
| 38 | SCOTUS scenario: B50 per-person burden comparison | `fig21_scotus_scenario_comparison.png` |
| 39 | Central combined scenario: quintile burden decomposition | `fig22_scotus_quintile_decomposition.png` |
| 40 | Price stickiness and the incidence of tariff revocation | `fig23_price_stickiness_flows.png` |
| 41 | SCOTUS scenario: sensitivity range and welfare impact | `fig24_scotus_welfare_sensitivity.png` |

### B.6 Real-Terms Budget Supplementary Figures

| Figure | Description | File |
|--------|-------------|------|
| 42 | Real spending by budget function waterfall (FY2020–2025) | `real_budget_function_waterfall.png` |
| 43 | Cumulative real spending by propensity tier | `real_cumulative_by_tier.png` |
| 44 | Defense vs. social spending trajectories (real) | `real_defense_vs_social.png` |
| 45 | Net interest timeline (nominal and real) | `real_interest_timeline.png` |
| 46 | Propensity-tier comparison (HIGH/MID/LOW) | `real_propensity_comparison.png` |
| 47 | Propensity-tier stacked area (FY2019–2025) | `real_propensity_stacked_area.png` |
| 48 | Tariff windfall flow: revenue to asset-holder gains | `real_tariff_windfall_flow.png` |
| 49 | Top agencies by real spending change | `real_top_agencies.png` |

## Appendix C: Structural Break Regression Detail

Table C1 reports the full OLS outputs underlying the structural break tests in Table 1d (Section 3.4). For each indicator, we regress the annual series on fiscal year over the indicator-specific training period and compute the z-score using the out-of-sample prediction standard error: $z = (y_{2025} - \hat{y}_{2025}) / SE_{pred}$, where $SE_{pred} = \hat{\sigma} \sqrt{1 + 1/n + (x_{2025} - \bar{x})^2 / SS_x}$. This accounts for both residual variance and parameter estimation uncertainty, yielding appropriately widened standard errors for out-of-sample predictions (compared to the naïve $z = \text{residual}/\hat{\sigma}$ which understates uncertainty).

**Table C1. Full OLS Regression Outputs**

| Parameter | Customs / Rev | Interest / Safety-net | Regressive Rev Share | Safety-net / Outlays |
|-----------|:------------:|:---------------------:|:-------------------:|:-------------------:|
| Training period | FY2000–2017 | FY2000–2024 excl. COVID | FY2000–2017 | FY2000–2024 excl. COVID |
| N (training obs) | 18 | 23 | 18 | 23 |
| Intercept (α̂) | −12.28 | 6.63 | 377.9 | −152.5 |
| Slope (β̂) | +0.0067 pp/yr | −0.0031 /yr | −0.168 pp/yr | +0.084 pp/yr |
| SE(β̂) | 0.0035 | 0.0051 | 0.131 | 0.045 |
| R² | 0.19 | 0.02 | 0.09 | 0.14 |
| σ̂ (residual std) | 0.072 | 0.166 | 2.73 | 1.46 |
| Predicted FY2025 | 1.20% | 0.450 | 37.4% | 17.7% |
| Actual FY2025 | 3.72% | 0.910 | 39.1% | 15.2% |
| Residual | +2.52 | +0.46 | +1.7 | −2.5 |
| **z-score** | **25.8** | **2.4** | **0.5** | **−1.5** |

*Notes:* Slopes are expressed in native units per year (percentage points per year for share variables, ratio units per year for the interest/safety-net ratio). Standard errors are OLS heteroskedasticity-uncorrected given the small sample sizes. The z-score uses the full out-of-sample prediction SE (see §3.4), which inflates the denominator relative to naïve σ̂ by the factor $\sqrt{1 + 1/n + (x_{new} - \bar{x})^2/SS_x}$; this correction is most material for the customs indicator where FY2025 has high leverage relative to the FY2000–2017 training window. The z-score threshold of |z| > 2.0 corresponds approximately to p < 0.05 under normality of residuals. Customs and regressive share use the pre-tariff-war training period (FY2000–2017) to avoid contamination from the Section 232/301 tariff actions beginning in 2018. Interest and safety-net indicators use the full panel excluding FY2020–2021 to prevent the COVID-era spending explosion and near-zero interest rate regime from dominating the trend estimate. Z-scores reflect the corrected out-of-sample prediction SE formula (run 2026-02-21).

\newpage

## Appendix B: Figures

![Federal outlay composition (stacked area, FY2015-2025)](figures/01_outlay_composition.png){width=90%}

![Revenue by source (stacked area)](figures/02_revenue_composition.png){width=90%}

![Net interest vs. safety-net spending](figures/03_interest_vs_safety_net.png){width=90%}

![CPI essentials indexed (with tariff event markers)](figures/04_cpi_essentials.png){width=90%}

![Corporate profits vs. wages (indexed)](figures/05_profits_vs_wages.png){width=90%}

![Customs revenue spike (bar chart)](figures/06_customs_revenue_spike.png){width=90%}

![Federal deficit trend (with policy periods)](figures/07_deficit_trend.png){width=90%}

![Income security waterfall (FY2019-2025)](figures/09_income_security_waterfall.png){width=90%}

![Net interest as percent of GDP](figures/10_interest_pct_gdp.png){width=90%}

![Customs revenue trajectory (with tariff regime markers)](figures/25yr_customs_trajectory.png){width=90%}

![FY2025 context dashboard (6-panel summary)](figures/25yr_fy2025_context_dashboard.png){width=90%}

![Income inequality evolution (Census quintile shares)](figures/25yr_inequality_evolution.png){width=90%}

![Interest vs. safety-net spending (25-year trajectory)](figures/25yr_interest_vs_safetynet.png){width=90%}

![B50 transfer dependency and poverty (CPS ASEC benchmarks)](figures/25yr_poverty_and_benefits.png){width=90%}

![Revenue composition shares (stacked area, FY2000–2025)](figures/25yr_revenue_composition.png){width=90%}

![Real spending composition (stacked area, FY2000–2025)](figures/25yr_spending_composition.png){width=90%}

![Structural break tests (4-panel: actual vs. trend)](figures/25yr_structural_breaks.png){width=90%}

![Burden decomposition by income percentile (stacked area)](figures/fig11_burden_decomposition.png){width=90%}

![Structural break prediction bands (forest plot)](figures/fig12_structural_break_bands.png){width=90%}

![Tariff pass-through: traded goods vs. services control](figures/fig13_services_price_acceleration.png){width=90%}

![B50 calibration diagram (quintile person shares)](figures/fig14_b50_calibration.png){width=90%}

![Robustness specification summary (6 dimensions)](figures/fig15_specification_curve.png){width=90%}

![CBO counterfactual waterfall (baseline to actual)](figures/fig16_counterfactual_waterfall.png){width=90%}

![Historical B50 income share and transfer dependency](figures/fig17_historical_b50.png){width=90%}

![Welfare-weighted loss (log-scale, CRRA σ=2)](figures/fig18_welfare_logscale.png){width=90%}

![State fiscal exposure index (dot plot)](figures/fig19_state_exposure_dots.png){width=90%}

![Income distribution by quintile (CPS ASEC)](figures/fig1_income_distribution.png){width=90%}

![SPM poverty dose-response (food program scenarios)](figures/fig20_spm_dose_response.png){width=90%}

![SCOTUS scenario: B50 per-person burden comparison (Section 12)](figures/fig21_scotus_scenario_comparison.png){width=90%}

![Central combined scenario: quintile burden decomposition (Section 12)](figures/fig22_scotus_quintile_decomposition.png){width=90%}

![Price stickiness and the incidence of tariff revocation (Section 12)](figures/fig23_price_stickiness_flows.png){width=90%}

![SCOTUS scenario: sensitivity range and welfare impact (Section 12)](figures/fig24_scotus_welfare_sensitivity.png){width=90%}

![Distributional impact of FY2025 policy](figures/fig2_distributional_impact.png){width=90%}

![Simulated distributional burden curve](figures/fig3_quantile_treatment_effects.png){width=90%}

![SPM poverty simulation](figures/fig4_spm_poverty_simulation.png){width=90%}

![State exposure classification map](figures/fig5_state_exposure.png){width=90%}

![Welfare-weighted impact (CRRA)](figures/fig6_welfare_weighted_impact.png){width=90%}

![CPI price changes in tariff-affected goods](figures/fig7_tariff_price_changes.png){width=90%}

![Tariff burden by income quintile](figures/fig8_tariff_burden_by_quintile.png){width=90%}

![B50 vs. T50 tariff cost by goods category](figures/fig9_b50_tariff_by_category.png){width=90%}

![Budget function waterfall (real terms)](figures/real_budget_function_waterfall.png){width=90%}

![Cumulative spending by tier (real terms)](figures/real_cumulative_by_tier.png){width=90%}

![Defense vs. social spending (real terms)](figures/real_defense_vs_social.png){width=90%}

![Interest payment timeline (real terms)](figures/real_interest_timeline.png){width=90%}

![Propensity classification comparison](figures/real_propensity_comparison.png){width=90%}

![Propensity stacked area chart](figures/real_propensity_stacked_area.png){width=90%}

![Tariff windfall flow diagram. Assumes 4.5% 10-yr rate (FRED DGS10), 20× P/E (conservative); equity ownership 93% top-10 (Fed 2023 SCF), bond ownership ~67% top-10 (Fed DFA)](figures/real_tariff_windfall_flow.png){width=90%}

![Top agencies by spending change](figures/real_top_agencies.png){width=90%}

