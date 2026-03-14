---
title: |
  The Distributional Incidence of U.S. Federal Fiscal Policy, FY2000–FY2025: Trend, Departure, and the Bottom 50%
author:
  - Andy Salazar
date: March 2026 (Revised)
abstract: |
  
  The combined fiscal burden of tariff escalation, means-tested spending cuts, and interest crowding on the bottom 50% of the U.S. income distribution reached $1,331 per person (10.6% of pretax income) in FY2025—an amount comparable to total means-tested transfer income separating B50 households from their market-income baseline. I embed FY2025 within a 26-year panel (FY2000–FY2025) of CBO budget data, Treasury administrative records, and CPS ASEC microdata (1.4 million person-records) and use out-of-sample prediction tests to classify each distributional channel as either a departure from its historical trajectory or a continuation of pre-existing trends. Two channels register as statistically significant departures: customs revenue's share of total revenue jumped from 1.0% to 3.7% (z = 25.8), and the interest-to-safety-net crowding ratio doubled to 0.91 (z = 2.4). Two others—the regressive revenue share and the safety-net outlay share—remain within their quarter-century trajectories. The channels classified as departures are precisely those that burden the bottom 50% most heavily. Whether these departures prove temporary or permanent cannot be assessed from a single post-departure observation; this paper identifies them, traces their distributional incidence, and distinguishes them from secular trends that require fundamentally different policy responses.

keywords: "fiscal incidence, tariff incidence, income distribution, means-tested transfers, departure from trend, bottom 50%"
thanks: "Working Paper. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6285038. JEL: H22, H23, H53, D31, F13, E62. Replication package: https://github.com/andsalazar/FederalBudgetAnalysis. Pre-registration: docs/hypothesis_preregistration.md"
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

The fiscal year 2025 federal budget simultaneously altered three channels of fiscal incidence: tariffs escalated to levels not seen since before the income tax, means-tested spending fell $188 billion below baseline, and interest payments on the national debt exceeded combined income security and Medicaid spending for the first time since the pre–New Deal era. Each of these shifts has distributional consequences that fall disproportionately on lower-income households. The combined fiscal burden on the bottom 50% (B50) of the income distribution is $1,331 per person—10.6% of pretax income—an amount comparable to total means-tested transfer income separating B50 households from their market-income baseline.

But a descriptive accounting of FY2025 alone is insufficient for policy analysis. A fundamental empirical question precedes prescription: *which of the channels driving this burden represent departures from historical fiscal trajectories, and which are continuations of secular trends?* This distinction matters because trends and departures call for fundamentally different policy responses. If the growing regressivity of the federal revenue mix is a 25-year trend, it will not reverse with a change of administration; it requires structural tax reform. If the tariff explosion is a statistically identifiable departure from the historical pattern, it is attributable to specific policy choices and, in principle, reversible.

I answer this question by embedding fiscal year 2025 within the 26-year span FY2000–FY2025 and testing whether key distributional indicators deviate significantly from their historical trajectories. For each indicator, I fit an OLS linear trend over a pre-treatment training period and test whether the FY2025 realized value falls outside the out-of-sample prediction interval (|z| > 2.0). I then trace the distributional consequences of the identified departures to the bottom 50% of the income distribution using CPS ASEC microdata.

**Preview of findings.** Two of four indicators register as statistically significant departures from trend: customs revenue as a share of total revenue (z = 25.8) and the interest-to-safety-net crowding ratio (z = 2.4). Two do not: the regressive revenue share (z = 0.5) and the safety-net outlay share (z = -1.5). The channels classified as departures are precisely those imposing the largest burden on the bottom 50%—a combined $1,331 per person (10.6% of pretax income), validated across 21 robustness specifications.

An important limitation: a single post-departure observation cannot distinguish a temporary shock from a permanent regime change. The departure-from-trend tests identify FY2025 as a statistical outlier relative to the 26-year trajectory, but whether the customs and crowding channels revert or persist is an empirical question that future data must resolve. The contribution of this paper is not to settle permanence but to (a) quantify the distributional burden, (b) identify *which* channels drive it, and (c) distinguish those channels from secular trends that would persist under any plausible counterfactual.

**Contribution.** My primary contribution is an integrated multi-channel analysis of the distributional incidence of FY2025 fiscal policy on the bottom 50%—combining tariff pass-through, means-tested spending cuts, and interest crowding in a unified framework that the existing literature (Piketty, Saez & Zucman, 2018; CBO, 2022; Wolff & Zacharias, 2007) has not attempted. The departure-from-trend classification serves as a diagnostic tool that organizes this distributional analysis: it reveals that the channels identified as departures are precisely those that burden the B50 most heavily, while the channels classified as within-trend—though also regressive—require fundamentally different policy responses. A secondary contribution is the integration of CPS ASEC microdata (1.4 million person-records) with administrative budget data to construct validated distributional weights for multi-channel incidence analysis.

### 1.1 Related Literature

**Tariff incidence.** Amiti, Redding, and Weinstein (2019, 2020) established near-complete pass-through of 2018–2019 tariffs to domestic prices. Fajgelbaum et al. (2020, *QJE*) quantified $51 billion in consumer losses with regional heterogeneity. Cavallo et al. (2021, *AER: Insights*) traced customs-to-retail pass-through using scanner data. Leibovici and Dunn (2025, Federal Reserve Bank of St. Louis) survey the 2018–19 evidence and confirm near-complete consumer incidence. I extend this work to the 2025 tariff regime at roughly four times the 2018–19 scale. Contemporaneous analyses by Clausing and Obstfeld (2025), Minton and Somale (2025), Gopinath and Neiman (2026), and The Budget Lab at Yale (2026) corroborate significant and regressive pass-through.

**Distributional fiscal analysis.** The CBO's distributional framework (Perese, 2017) and Piketty, Saez, and Zucman (2018) provide the methodological foundation for my income decomposition. Wolff and Zacharias (2007) conduct a similar multi-channel fiscal incidence analysis for 1989–2000, but without departure-from-trend identification or tariff incidence. Bitler, Gelbach, and Hoynes (2006, 2010) develop methods for distributional effects of spending changes that motivate my simulation approach.

**Debt service and crowding out.** Falkenheim (2022) and Auerbach and Gorodnichenko (2012) analyze how rising interest payments crowd out discretionary and mandatory spending. I formalize this as a testable departure-from-trend indicator.

---

\newpage
## 2. Data

### 2.1 Administrative Budget Data

I collect 69,000+ observations across 160+ economic series from four administrative sources:

| Source | Series/Tables | Observations | Period |
|--------|--------------|-------------|--------|
| FRED (Federal Reserve) | 48 series (GDP, employment, CPI, interest rates) | 53,291 | 1947–2026 |
| U.S. Treasury Fiscal Data API | MTS Tables 5 & 9 (outlays/revenues by function) | 11,197 | 2015–2025 |
| Congressional Budget Office | Historical Budget Data (67 series) | 4,691 | 1962–2035 |
| BEA NIPA via FRED | 11 government spending series | 512 | 2000–2025 |

For the structural analysis, I extract CBO historical outlay and revenue series back to FY2000, yielding 26 annual observations for each of 32 budget aggregates in both nominal and real (FY2024 dollar) terms. CBO baseline projections (January 2025) provide the FY2025 counterfactual.

### 2.2 Census Income Distribution Data

**Census Table H-2.** Annual household income quintile shares, 2000–2023 (24 observations).

**CPS ASEC microdata (eight benchmark years).** Calendar years 2002, 2005, 2008, 2011, 2014, 2017, 2020, 2023 via the Census Bureau API, comprising approximately 1.4 million person-records (age 15+) with full income component detail and supplement weights.

**CPS ASEC 2024.** 115,836 person records representing 273 million weighted persons. Income reference year CY2023 (pre-policy baseline). Income components follow the PSZ framework: market income (earnings + capital), social insurance (Social Security + unemployment + veterans), means-tested transfers (SSI + public assistance + educational assistance), federal taxes (income + FICA), and tax credits (EITC + CTC).

### 2.3 Consumer Expenditure Survey

BLS CEX 2023 published quintile tables (Table 1101) for expenditure by goods category and income quintile. I calibrate the CEX-to-CPS cross-walk using CPS ASEC 2024 microdata: grouping respondents by household, the person-weighted 50th percentile of household income is $96,000, yielding:

$$\text{B50}_{\text{CEX}} = Q_1 + Q_2 + Q_3 + 0.414 \times Q_4$$

This captures exactly 50.0% of persons by household income rank (see Appendix A for calibration details; income distribution baseline in Appendix B). For the spending-cut analysis, I use CPS person-income quintiles where B50 = Q1+Q2+0.5$\times$Q3 (136.6M persons).

### 2.4 CPI Sub-Indices

Twelve CPI-U sub-indices from FRED (through January 2026) covering tariff-affected goods categories plus five non-tradable service categories as controls.

### 2.5 Inflation Adjustment

All dollar values in constant FY2024 dollars (CPI-U base = 311.6). Robustness to PCE, GDP deflator, chained CPI-U, and CPI-W tested in Section 7.

---

\newpage
## 3. Conceptual Framework

### 3.1 Three Channels of Fiscal Incidence

I model the distributional impact of federal fiscal policy through three channels that may operate simultaneously:

1. **The tariff channel.** Tariffs function as a consumption tax whose incidence depends on import content of consumer goods and spending shares across the income distribution. Because lower-income households spend a higher share of income on goods (vs. services) and on import-intensive necessities (food, clothing, household goods), tariff burdens are regressive as a share of income (Fajgelbaum et al., 2020).

2. **The spending-cut channel.** Reductions in means-tested federal spending (Medicaid, income security, nondefense discretionary) fall disproportionately on households that receive these transfers. CPS ASEC data confirm extreme concentration: SSI receipt rates are 64:1 (Q1 vs. Q5), EITC dollar values 329:1.

3. **The interest-crowding channel.** Rising debt service redirects federal outlays from transfers (which flow to lower-income households) to interest payments (which flow to bondholders concentrated in the top decile—67% of bonds and fixed-income securities per the Federal Reserve 2023 SCF).

### 3.2 Trend vs. Departure

The key conceptual distinction is between *secular trends* and *departures from trend*. A secular trend in distributional incidence—such as a gradual shift toward more regressive revenue sources—reflects structural forces (demographic change, globalization, legislative drift) that persist across administrations. A departure from trend—such as the sudden explosion of tariff revenue—reflects identifiable policy choices whose distributional consequences can be attributed to specific actions.

This distinction generates testable predictions:
- **If FY2025 is a trend continuation:** distributional indicators should fall within the prediction interval of pre-existing trajectories. Policy response requires structural reform.
- **If FY2025 is a departure from trend:** indicators should deviate significantly from trend predictions. The departure is attributable to identifiable policies and is, in principle, reversible—though whether it proves temporary or permanent cannot be assessed from a single observation.

These predictions generate four testable hypotheses:

- **H1 (Customs departure):** The customs revenue share in FY2025 exceeds the out-of-sample prediction interval from the FY2000–2017 trend (|z| > 2.0).
- **H2 (Crowding departure):** The interest-to-safety-net ratio in FY2025 exceeds the out-of-sample prediction interval from the FY2000–2024 trend (|z| > 2.0).
- **H3 (Trend continuity):** The regressive revenue share and safety-net outlay share in FY2025 fall within their respective prediction intervals (|z| $\leq$ 2.0).
- **H4 (Regressive departure):** The channels classified as departures from trend impose a larger per-person burden on the bottom 50% than the channels classified as within-trend.

### 3.3 Interaction Effects

The three channels reinforce one another through two mechanisms:
- **Budget composition:** Interest crowding reduces the fiscal space available for transfers, amplifying the spending-cut channel.
- **Income-base erosion:** Tariff-driven price increases erode the real purchasing power of the transfers that remain, compounding the welfare loss from spending reductions.

This means analyzing any channel in isolation—as the existing literature does—understates the combined burden on the bottom 50%.

---

\newpage
## 4. Empirical Strategy

### 4.1 Departure-from-Trend Identification

For each of four distributional indicators, I test whether the FY2025 value constitutes a statistically significant departure from the historical trajectory. The procedure is:

1. **Training period selection.** I use indicator-specific training periods to avoid contamination:
   - *Customs share* and *regressive revenue share*: FY2000–FY2017 (n = 18), ending before Section 301 tariff actions.
   - *Interest/safety-net ratio* and *safety-net outlay share*: FY2000–FY2024 excluding COVID-distorted FY2020–FY2021 (n = 23).

2. **OLS trend estimation.** For each indicator $y$, I estimate:
$$y_t = \alpha + \beta \cdot t + \varepsilon_t$$
over the training period.

3. **Out-of-sample prediction test.** The z-score uses the proper prediction standard error:

$$z = \frac{y_{2025} - \hat{y}_{2025}}{\hat{\sigma} \sqrt{1 + \frac{1}{n} + \frac{(x_{2025} - \bar{x})^2}{\sum(x_i - \bar{x})^2}}}$$

where $\hat{\sigma}$ is the residual standard deviation, $n$ is the training sample size, and the denominator accounts for parameter estimation uncertainty and forecast-point leverage. $|z| > 2.0$ corresponds to a statistically significant departure at approximately the 5% level.

4. **Classification.** Indicators with $|z| > 2.0$ are classified as departures from trend; those with $|z| \leq 2.0$ as within-trend.

### 4.2 Aggregate Fiscal Accounting

I measure the FY2025 fiscal shift by comparing actual spending and revenue against the CBO January 2025 baseline projection (*The Budget and Economic Outlook: 2025 to 2035*), which embodies current-law assumptions and thus provides a "no policy change" counterfactual.

### 4.3 Tariff Price Pass-Through

I test for tariff-driven price increases using two complementary identification strategies:

**Within-goods dose-response.** The Spearman rank correlation between effective tariff rate and CPI price acceleration across 12 consumer goods categories provides a non-parametric test of whether higher-tariff goods experienced above-trend price increases.

**Services control group.** I compare CPI acceleration in eight tariff-exposed traded goods against five non-tradable service categories (medical care, shelter, education, services less energy, transportation services) that are unaffected by customs tariffs, following the identification logic of Amiti et al. (2019). Difference in acceleration isolates the tariff signal from background inflation trends.

### 4.4 Distributional Attribution

Spending cuts are attributed to income quintiles using program-specific distributional weights derived from CPS ASEC receipt data:
- **Medicaid (-$36B):** 40% Q1, 30% Q2, 15% Q3, 10% Q4, 5% Q5
- **Income Security (-$53B):** 50% Q1, 30% Q2, 12% Q3, 6% Q4, 2% Q5
- **Nondefense Discretionary (-$95B):** 25% Q1, 25% Q2, 22% Q3, 18% Q4, 10% Q5

These weights are validated against CPS ASEC program receipt rates: SSI receipt is 64:1 (Q1 vs. Q5), public assistance 16:1, EITC 329:1 in average dollar terms (Table B2).

Tariff burden is allocated using BLS CEX 2023 expenditure shares by quintile, with the B50 share (51.7%) calibrated via the CPS-CEX cross-walk (Section 2.3). Deadweight loss is estimated at 1.4$\times$ tariff revenue following Amiti et al. (2019), with sensitivity ranging from 1.0$\times$ to 2.0$\times$.

### 4.5 Robustness Design

I subject all findings to six dimensions of robustness (21 distinct specifications plus 500-draw household-clustered bootstrap): propensity classification (4 specs), tariff pass-through (6 specs), CBO baseline uncertainty (5 specs), alternative deflators (5 specs), bootstrap confidence intervals (500 draws), and a placebo test (FY2019). Welfare analysis and poverty simulations appear in Appendix C; departure-from-trend regression detail in Appendix D; data sources and replication instructions in Appendix F; all figures are cataloged in Appendix G.

---

\newpage
## 5. Results I: Trend vs. Departure Classification

### 5.1 The 26-Year Fiscal Trajectory

Before presenting break test results, I establish the structural context. All values in constant FY2024 dollars.

**Table 1. Federal Budget Aggregates, FY2000 vs. FY2025 (Real FY2024 $)**

| Measure | FY2000 | FY2025 | Change |
|---------|--------|--------|--------|
| Total Outlays | $3,265B | $6,826B | +109% |
| Net Interest | $407B | $944B | +132% |
| Customs Revenue | $36.3B | $189.7B | +422% |
| Income Security | $244B | $387B | +58% |

Three patterns stand out: (i) interest payments grew faster than any spending category (+132%); (ii) customs revenue grew 422%—the most extreme growth of any revenue source; (iii) income security grew just 58%, well below the 109% increase in total spending, implying a declining share.

**Table 2. Revenue Composition, FY2000 vs. FY2025**

| Revenue Source | FY2000 | FY2025 | Change |
|---------------|--------|--------|--------|
| Progressive (income + corp.) | 59.8% | 57.1% | -2.7pp |
| Regressive (excise + customs + FICA) | 36.6% | 39.1% | +2.5pp |
| Customs alone | 1.0% | 3.7% | +2.7pp |

Census data confirm a concurrent compression of income shares: the B50 household income share fell from 19.9% (2000) to 18.0% (2023), while the top 20% rose from 49.8% to 52.4%.

### 5.2 Departure-from-Trend Test Results

**Table 3. Departure-from-Trend Tests**

| Indicator | Training | Predicted FY2025 | Actual FY2025 | z-Score | Classification |
|-----------|---------|-----------------|--------------|---------|----------------|
| Customs / total revenue | FY2000–2017 | 1.20% | 3.72% | **25.8** | **Departure** |
| Interest / safety-net | FY2000–2024 excl. COVID | 0.45 | 0.91 | **2.4** | **Departure** |
| Regressive revenue share | FY2000–2017 | 37.4% | 39.1% | 0.5 | Trend |
| Safety-net / total outlays | FY2000–2024 excl. COVID | 17.7% | 15.2% | -1.5 | Trend |

Full OLS outputs in Appendix D. The results partition FY2025 into two categories:

**Departures from trend (z > 2.0).** The customs share (z = 25.8) is the most statistically extreme: a 26-fold deviation from the prediction standard error, driven by Liberation Day and related executive tariff actions that took customs revenue from $77B (FY2024) to $195B (FY2025). The interest/safety-net ratio (z = 2.4) reflects the compounding of post-pandemic debt accumulation and rate normalization, pushing interest payments roughly double their trend-predicted level relative to safety-net spending. Together, these departures represent a large and identifiable shift in fiscal incidence toward channels that disproportionately burden lower-income households.

**Within-trend (|z| $\leq$ 2.0).** The regressive revenue share (z = 0.5) and safety-net outlay share (z = -1.5) are not statistically distinguishable from their 25-year trajectories. FY2025 did not initiate the shift toward more regressive revenue or away from safety-net spending—these are multi-decade trends that would persist under any plausible counterfactual. The safety-net share (15.2%, predicted 17.7%) merits monitoring but does not meet the departure threshold once COVID-era observations are excluded from the training sample.

### 5.3 The Aggregate FY2025 Fiscal Shift

I compare actual FY2025 spending against the CBO January 2025 baseline:

**Table 4. FY2025 Spending: CBO Baseline vs. Actual**

| Category | CBO Baseline | Actual | Gap |
|----------|-------------|--------|-----|
| Social Security | $1,530B | $1,530B | $0B |
| Medicare | $869B | $869B | $0B |
| Medicaid | $616B | $580B | -$36B |
| Income Security | $403B | $350B | -$53B |
| Nondefense Discretionary | $755B | $660B | -$95B |
| Net Interest | $952B | $980B | +$28B |
| **Total** | **$7,023B** | **$6,835B** | **-$188B** |

The $188B shortfall is concentrated in three categories with high bottom-50% incidence; unlisted categories account for the difference between the displayed items and the total. On the revenue side, customs duties reached $195B nominal (+153% YoY; $189.7B in real FY2024 dollars per Table 1), generating $100B above baseline.

### 5.4 Tariff Price Pass-Through

**Table 5. CPI Acceleration: Tariff-Affected vs. Control Categories**

| Category | Eff. Tariff | Pre-Tariff YoY | Post-Tariff YoY | Acceleration |
|----------|------------|----------------|-----------------|-------------|
| Consumer Electronics | 10–145% | -6.05% | +1.57% | **+7.61pp** |
| Household Furnishings | 10–145% | +0.48% | +3.93% | **+3.46pp** |
| Toys and Games | 10–145% | +3.71% | +5.54% | **+1.84pp** |
| Footwear | 10–145% | +1.03% | +1.95% | +0.93pp |
| New Vehicles | 25% | -0.34% | +0.37% | +0.71pp |
| Food at Home | 10–25% | +1.84% | +2.18% | +0.33pp |
| Gasoline | 10–25% | -0.13% | -7.49% | -7.37pp |

**Identification test 1 (within-goods dose-response).** Spearman rank correlation between tariff rate and price acceleration: **$\rho$ = 0.684, p = 0.020**. High-tariff goods (>15% effective rate) saw mean acceleration of +2.30pp vs. -1.46pp for low-tariff goods.

**Identification test 2 (services control group).** Traded goods accelerated +1.66pp while non-tradable services decelerated -1.78pp, yielding a differential of +3.44pp (Mann-Whitney p = 0.015, Cohen's d = 1.26). This rules out the hypothesis that observed price increases reflect broader inflationary pressure.

---

\newpage
## 6. Results II: Distributional Consequences of the Departures from Trend

Having established which features of FY2025 are departures from trend and confirmed tariff-to-price pass-through, I now trace their distributional consequences.

### 6.1 Who Bears the FY2025 Fiscal Shift?

**Table 6. Distributional Impact by Quintile**

| Quintile | Spending Cuts | Tariff Burden | Total | Per Person | % Pretax Income |
|----------|-------------|--------------|-------|-----------|----------------|
| Q1 (Bottom 20%) | -$64.7B | -$14.0B | -$78.7B | -$1,440 | 363.3%* |
| Q2 | -$50.4B | -$21.0B | -$71.4B | -$1,308 | 8.3% |
| Q3 | -$32.7B | -$30.8B | -$63.5B | -$1,162 | 3.3% |
| Q4 | -$23.9B | -$37.8B | -$61.7B | -$1,129 | 1.8% |
| Q5 (Top 20%) | -$12.4B | -$36.4B | -$48.8B | -$893 | 0.5% |

*Q1 percentage reflects near-zero pretax income ($396/person). The B50 is Q1+Q2+0.5$\times$Q3 of CPS person-income quintiles (136.6M persons).*

The spending-cut channel is strongly progressive in incidence (Q1 bears 35% of cuts). The tariff channel is regressive as a share of income. The combined effect is monotonically regressive: burden falls from $1,440 (Q1) to $893 (Q5) per person, and steeply when expressed as income shares.

### 6.2 Combined B50 Burden

**Table 7. Total FY2025 Fiscal Impact on the Bottom 50%**

| Channel | B50 Burden | Per Person | % Pretax Income |
|---------|-----------|-----------|----------------|
| Spending cuts | $131.4B | $962 | 7.7% |
| Tariff consumer burden (DWL-inclusive) | $50.4B | $369 | 2.9% |
| **Combined** | **$181.8B** | **$1,331** | **10.6%** |

B50 mean pretax income is $12,526 (CPS ASEC 2024). The $1,331 benchmark is robust across specifications: propensity classification yields a B50 loss range of $108B–$135B, and the tariff channel spans $132–$527 per person depending on pass-through assumptions (Table 9). Even at the lower bound, the combined burden is comparable in magnitude to total means-tested transfer income ($1,111/person) that separates the B50 from their market income baseline.

### 6.3 The Regressivity Gradient

Using CPS ASEC 2024 microdata, I simulate the policy burden at each income percentile:

**Table 8. Simulated Policy Burden by Percentile**

| Percentile | Mean Income | Per-Person Loss | % of Income |
|-----------|------------|----------------|-------------|
| p20 | $5,342 | $1,057 | 19.8% |
| p50 (Median) | $35,625 | $755 | 2.1% |
| p90 | $128,195 | $401 | 0.3% |
| p99 | $671,160 | $347 | <0.1% |

The burden at the 20th percentile (19.8% of income) exceeds that at the 99th percentile (<0.1%) by more than two orders of magnitude—a gradient driven primarily by the departure-from-trend channels: tariff escalation and interest crowding.

### 6.4 The Interest-Crowding Mechanism

Net interest payments reached $980B in FY2025, reaching 105% of combined income security and Medicaid ($930B). This threshold was last crossed in the pre–New Deal era. Interest payments flow to bondholders concentrated in the top decile (67% of bonds and fixed-income securities, Federal Reserve 2023 SCF), while the spending they crowd out—Medicaid, income security, nondefense discretionary—flows to the bottom quintiles. The interest/safety-net ratio's classification as a departure from trend (z = 2.4) is consistent with a substantial redistribution from the bottom to the top of the income distribution operating through the federal balance sheet.

---

\newpage
## 7. Robustness

**Table 9. Robustness Battery (6 Dimensions, 21 Specifications + 500 Bootstrap Draws)**

| Test | Specs | Result |
|------|-------|--------|
| Propensity Classification | 4 | B50 loss range: $108B–$135B, all negative |
| Tariff Pass-Through | 6 | B50 per-person: $132–$527 |
| CBO Baseline Uncertainty | 5 | All scenarios below baseline |
| Alternative Deflators | 5 | Income security decline >70% under all |
| Bootstrap CIs (n=500, HH-clustered) | 500 | B50 share: 11.12% [10.96, 11.29] |
| Placebo (FY2019) | 1 | FY2019 gap $\approx$ $0B vs. FY2025 -$404B |

All 21 specifications confirm the direction and approximate magnitude of B50 fiscal burden. The FY2019 placebo test—applying the identical methodology to a non-event year—produces a spending gap of approximately $0B, confirming that the FY2025 findings are not an artifact of the CBO baseline methodology.

---

\newpage
## 8. Limitations

1. **FY2025 spending estimates** use CBO January 2025 baseline and partial-year Treasury data. Full-year reconciliation against final MTS actuals is warranted.

2. **CPS ASEC 2024 reflects CY2023 income**—a pre-policy baseline. When the ASEC 2025 becomes available (September 2026), formal difference-in-differences estimation exploiting cross-state tariff and transfer exposure variation will enable causal identification.

3. **Causal identification is partial.** The CBO counterfactual identifies the spending gap. Tariff price effects are supported by two identification strategies (within-goods dose-response $\rho$ = 0.684, p = 0.020; traded-vs.-services differential +3.44pp, p = 0.015) but cannot fully separate tariff causality from other supply-side factors.

4. **Post-pandemic normalization** in income security spending is partially captured by the FY2019 placebo test but requires a formal panel DiD for definitive causal claims.

5. **CEX-to-CPS mapping** uses a calibrated but not exact partitioning. Sensitivity bounds (42.2–65.3% B50 tariff share) bracket the 51.7% estimate.

6. **Price stickiness duration** is uncertain. My near-term (0–12 month) assumption is empirically grounded but prices may partially adjust over 12–24 months.

---

\newpage
## 9. Conclusion

The combined fiscal burden of tariff escalation, means-tested spending cuts, and interest crowding on the bottom 50% of the U.S. income distribution reached $1,331 per person in FY2025—10.6% of pretax income, robust across 21 specifications. This amount is comparable in magnitude to total means-tested transfer income ($1,111/person) separating B50 households from their market-income baseline, and exceeds the burden at the 99th percentile by more than two orders of magnitude as a share of income.

Embedding FY2025 within 26 years of fiscal data reveals that this burden is part trend, part departure—and the distinction matters for both diagnosis and remedy.

The gradual shift toward more regressive federal revenue (+2.5pp over 25 years) and the compression of the B50 income share (from 19.9% to 18.0%) are secular trends that predate 2025, would continue under any administration, and require structural reform. The safety-net outlay share, while below its trend-predicted level, does not meet the departure threshold (z = -1.5) once pandemic-era observations are excluded.

What is historically anomalous is the tariff channel. The customs revenue share jumped from 1.0% to 3.7% of total revenue—a z-score of 25.8, the most dramatic single-year change in the federal revenue mix since the introduction of the income tax. The interest-crowding ratio (z = 2.4) also departs from trend, pushing interest payments to double their predicted level relative to safety-net spending. These departures are precisely the channels that burden the bottom 50% most heavily.

Whether these departures prove temporary or permanent is a question this paper cannot answer from a single post-departure observation. What the analysis does establish is that the FY2025 fiscal configuration is a statistical outlier relative to its 26-year trajectory, that the outlier channels are those with the most regressive incidence, and that the within-trend channels—though also regressive—require fundamentally different policy responses. The distinction between trend and departure is not merely taxonomic; it is the difference between problems that require structural reform and problems that are, in principle, reversible through targeted policy action.

Appendix E extends the framework to the post-*Learning Resources* policy environment, showing that tariff revocation under price stickiness provides limited near-term consumer relief and that the announced legislative replacement would amplify rather than resolve the departure.

When the CPS ASEC 2025 becomes available (September 2026), synthetic difference-in-differences estimation following Athey and Imbens (2023) will enable formal causal identification and provide the first evidence on whether the FY2025 departures persist, revert, or deepen. Until then, the evidence presented here—linking 26 years of fiscal accounting, departure-from-trend tests, realized price pass-through, and validated distributional weights—constitutes the strongest available assessment of which features of FY2025 are trend, which are departure, and who bears the cost of each.

---

## Declaration of Interest

The author declares no competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. This research received no external funding.

---

## Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process

During the preparation of this work the author used Claude Opus 4.6 in order to code this project and make available on GitHub. After using this tool/service, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.

---

## References

Amiti, M., Redding, S. J., & Weinstein, D. E. (2019). The impact of the 2018 tariffs on prices and welfare. *Journal of Economic Perspectives*, 33(4), 187–210.

Amiti, M., Redding, S. J., & Weinstein, D. E. (2020). Who's paying for the US tariffs? A longer-term perspective. *AEA Papers and Proceedings*, 110, 541–546.

Athey, S., & Imbens, G. W. (2023). Design-based analysis in difference-in-differences settings with staggered adoption. *Journal of Econometrics*, 226(1), 62–79.

Auerbach, A. J., & Gorodnichenko, Y. (2012). Measuring the output responses to fiscal policy. *American Economic Journal: Economic Policy*, 4(2), 1–27.

Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2006). What mean impacts miss. *American Economic Review*, 96(4), 988–1012.

Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2010). Distributional impacts of the Self-Sufficiency Project. *Journal of Public Economics*, 94(11–12), 781–793.

Cavallo, A. (2018). Scraped data and sticky prices. *Review of Economics and Statistics*, 100(1), 105–119.

Cavallo, A., Gopinath, G., Neiman, B., & Tang, J. (2021). Tariff pass-through at the border and at the store. *AER: Insights*, 3(1), 19–34.

Clausing, K. A., & Obstfeld, M. (2025). Tariffs as fiscal policy. NBER WP 34192.

Congressional Budget Office. (2022). The distribution of household income, 2019.

Fajgelbaum, P. D., Goldberg, P. K., Kennedy, P. J., & Khandelwal, A. K. (2020). The return to protectionism. *QJE*, 135(1), 1–55.

Falkenheim, M. (2022). How changes in the federal budget affect the economy. CBO Working Paper.

Federal Reserve Board. (2023). Changes in U.S. family finances from 2019 to 2022. *Federal Reserve Bulletin*, 109(4).

Gopinath, G., Itskhoki, O., & Rigobon, R. (2010). Currency choice and exchange rate pass-through. *AER*, 100(1), 304–336.

Gopinath, G., & Neiman, B. (2026). The incidence of tariffs: Rates and reality. NBER WP 34620.

Leibovici, F., & Dunn, J. (2025). What have we learned from the U.S. tariff increases of 2018–19? *FRB St. Louis Review*.

Minton, T., & Somale, M. (2025). Detecting tariff effects on consumer prices in real time. FEDS Notes.

Peltzman, S. (2000). Prices rise faster than they fall. *JPE*, 108(3), 466–502.

Perese, K. (2017). CBO's framework for analyzing means-tested transfers and federal taxes. CBO WP 2017-09.

Piketty, T., Saez, E., & Zucman, G. (2018). Distributional national accounts: Methods and estimates for the United States. *QJE*, 133(2), 553–609.

The Budget Lab at Yale. (2026). The effect of tariffs on poverty. Working Paper.

Wolff, E. N., & Zacharias, A. (2007). The distributional consequences of government spending and taxation in the US. *Review of Income and Wealth*, 53(4), 692–715.

---

\newpage
## Appendix A: B50 Calibration and CEX-CPS Cross-Walk

CEX quintile boundaries (Q1 < $23,810; Q5 > $127,080) are defined by consumer unit before-tax income, which differs from person-level income ranking. I calibrate the cross-walk using CPS ASEC 2024 (115,836 persons): grouping by household (PH_SEQ), summing pretax income, and assigning each person their household's CEX quintile band. The person-weighted 50th percentile of household income is $96,000—in CEX Q4 ($77,025–$127,080). Exactly 41.4% of Q4 persons have household income below this threshold:

$$\text{B50}_{\text{CEX}} = Q_1 + Q_2 + Q_3 + 0.414 \times Q_4$$

This captures 50.0% of persons (10.1% + 12.7% + 17.8% + 0.414 $\times$ 22.7%). Sensitivity bounds: Q1+Q2+Q3 only (40.6%, 42.2% tariff share) to Q1+Q2+Q3+Q4 (63.3%, 65.3% tariff share).

**Important distinction.** The CEX calibration applies only to tariff expenditure share calculations. For spending-cut attribution, I use CPS person-income quintiles where each quintile contains exactly 20% of persons: B50 = Q1+Q2+0.5$\times$Q3 (136.6M persons).

---

\newpage
## Appendix B: Income Distribution Baseline (CPS ASEC)

**Table B1. National Income Shares, CY2023 (PSZ Framework)**

| Group | Market Income | Pretax Income | Post-Tax Income | Capital Income |
|-------|-------------- |--------------|-----------------|---------------|
| Bottom 50% | 6.7% | 11.1% | 12.0% | -0.1% |
| Middle 40% | 48.6% | 47.3% | 48.1% | 9.0% |
| Top 10% | 44.7% | 41.6% | 39.9% | 91.1% |
| Top 1% | 13.0% | 11.9% | 11.1% | 42.8% |

The B50 earns 6.7% of market income but receives 12.0% of post-tax income—the difference is entirely attributable to the transfer system, making the B50 uniquely exposed to cuts in means-tested spending.

**Table B2. Income and Transfer Receipt by Quintile (Person-Weighted)**

| Quintile | Mean Pretax | Mean Means-Tested | Eff. Tax Rate | SSI Receipt | EITC Mean |
|----------|------------|-------------------|---------------|-------------|-----------|
| Q1 (Bottom 20%) | $396 | $1,606 | 153%* | 6.4% | $108 |
| Q2 | $15,826 | $944 | 7.1% | 3.3% | $329 |
| Q3 | $35,619 | $421 | 11.2% | 0.6% | $269 |
| Q4 | $62,473 | $258 | 14.8% | 0.2% | $23 |
| Q5 (Top 20%) | $167,416 | $198 | 19.7% | 0.1% | $1 |

Inequality measures: Gini (pretax) = 0.587 [95% CI: 0.584–0.591]; B50 income share = 11.12% [10.96–11.29]; Top 10% / B50 ratio = 18.7:1.

---

\newpage
## Appendix C: Welfare Analysis and Simulations

### C.1 CRRA Welfare Weighting ($\sigma$ = 2)

Under CRRA with $\sigma$ = 2, the welfare weight for Q1 exceeds Q5 by a factor of approximately 11,000, making Q1 welfare losses orders of magnitude more consequential.

### C.2 SPM Poverty Simulation

**Table C1. Poverty Simulation Under SNAP Reduction Scenarios**

| Scenario | SPM Rate | Change | Additional Persons |
|----------|---------|--------|--------------------|
| Baseline | 12.70% | — | — |
| 10% SNAP cut | 12.78% | +0.08pp | +209,494 |
| 25% SNAP cut | 12.89% | +0.19pp | +517,170 |
| 50% SNAP cut | 13.11% | +0.41pp | +1,117,918 |

### C.3 Geographic Heterogeneity: State Exposure Index

Following Fajgelbaum et al. (2020), composite state-level exposure using transfer dependency (35%), capital income share (15%), B50 income level (30%), and Gini (20%):

| Classification | States |
|---------------|--------|
| **High Exposure** | MS (1.86), LA (1.60), WV (1.40), NM (1.36), KY (0.91), SC (0.84) |
| **Low Exposure** | DC (-1.78), SD (-1.38), VT (-1.16), MN (-1.05), ND (-0.96) |

This geographic variation forms the basis for future synthetic DiD estimation with post-treatment ASEC data.

---

\newpage
## Appendix D: Departure-from-Trend Regression Detail

**Table D1. Full OLS Outputs**

| Parameter | Customs / Rev | Interest / Safety-net | Regressive Rev Share | Safety-net / Outlays |
|-----------|:------------:|:---------------------:|:-------------------:|:-------------------:|
| Training period | FY2000–2017 | FY2000–2024 excl. COVID | FY2000–2017 | FY2000–2024 excl. COVID |
| N | 18 | 23 | 18 | 23 |
| Intercept ($\alpha$̂) | -12.28 | 6.63 | 377.9 | -152.5 |
| Slope ($\beta$̂) | +0.0067 pp/yr | -0.0031 /yr | -0.168 pp/yr | +0.084 pp/yr |
| SE($\beta$̂) | 0.0035 | 0.0051 | 0.131 | 0.045 |
| R² | 0.19 | 0.02 | 0.09 | 0.14 |
| $\sigma$̂ | 0.072 | 0.166 | 2.73 | 1.46 |
| Predicted FY2025 | 1.20% | 0.450 | 37.4% | 17.7% |
| Actual FY2025 | 3.72% | 0.910 | 39.1% | 15.2% |
| **z-score** | **25.8** | **2.4** | **0.5** | **-1.5** |

The z-score uses the full out-of-sample prediction SE:  $SE_{pred} = \hat{\sigma} \sqrt{1 + 1/n + (x_{new} - \bar{x})^2/SS_x}$.

---

\newpage
## Appendix E: Policy Scenario Analysis—Judicial Revocation and Legislative Replacement

Following the Supreme Court's invalidation of IEEPA tariff authority (*Learning Resources, Inc. v. Trump*, No. 24-1287, Feb. 20, 2026), this appendix extends the departure-from-trend framework to model the distributional consequences of tariff revocation and the announced 15% universal legislative replacement.

### E.1 Tariff Revocation Does Not Reverse the B50 Burden

Under the empirically grounded assumption of asymmetric price adjustment (Peltzman, 2000; Cavallo, 2018; Gopinath, Itskhoki & Rigobon, 2010), tariff revocation does not reduce consumer prices in the near term. The tariff wedge shifts from Treasury revenue to importer/retailer margins, while $133B+ in refunds flows to the importers who paid duties at the border—not to consumers. Under price stickiness, the B50 burden is unchanged at $1,331/person.

### E.2 The 15% Legislative Replacement Nearly Doubles the Burden

A 15% uniform tariff on the full $3,100B goods import base generates substantially higher consumer burden than the targeted executive tariffs:

**Table E1. B50 Burden: Status Quo vs. Combined Revocation + Replacement**

| Metric | Status Quo | Central Scenario |
|--------|-----------|------------------|
| Consumer burden | $140B | $566B |
| B50 combined burden | $181.8B | $319.6B |
| B50 per person | $1,331 | $2,341 |
| B50 % of pretax income | 10.6% | 18.7% |

Under the central scenario, the B50 combined burden increases 76% to $2,341 per person—exceeding B50 mean transfer income by a factor of 2.1. The broader import base of a universal tariff amplifies its consumption-tax character relative to category-specific executive tariffs. Sensitivity analysis (Low: $1,703; High: $2,468 per person) brackets trade elasticity uncertainty.

### E.3 Implications for the Departure-from-Trend Framework

The transition from IEEPA tariffs to a legislative replacement does not reverse the customs-revenue departure. Under the central scenario, customs revenue increases from $195B to $404B, pushing the z-score even further above the departure threshold. The only scenario that reverses the departure is full tariff revocation *with* flexible downward price adjustment and *without* a replacement tariff—a combination that is neither empirically likely in the short run nor politically plausible given the announced 15% replacement.

### E.4 SCOTUS Scenario Figures

| Figure | Description |
|--------|-------------|
| E1 | B50 per-person burden: status quo vs. replacement scenarios |
| E2 | Price stickiness incidence flow diagram |
| E3 | Sensitivity range and welfare impact |

---

\newpage
## Appendix F: Data Sources and Replication

| Source | Access Method | Files |
|--------|-------------|-------|
| FRED (48 series) | fredapi Python | federal_budget.db |
| Treasury MTS | Fiscal Data API | federal_budget.db |
| CBO Historical Budget | Manual + load_cbo_data.py | federal_budget.db |
| CPS ASEC 2024 | Census Bureau API | cps_asec_2024_microdata.csv |
| CPS ASEC Historical (8 yrs) | Census Bureau API | cps_asec_historical_quintiles.csv |
| Census H-2 (24 yrs) | Census Historical Income Tables | census_income_quintiles.csv |
| BLS CEX 2023 | Table 1101 | run_tariff_incidence_analysis.py |

All scripts available at [github.com/andsalazar/FederalBudgetAnalysis](https://github.com/andsalazar/FederalBudgetAnalysis).

---


### G.1 Departure-from-Trend and 26-Year Trend Figures

| Figure | Description |
|--------|-------------|
| 1 | Departure-from-trend tests: actual vs. trend-predicted (4-panel) |
| 2 | Customs revenue trajectory with tariff regime markers |
| 3 | Interest vs. safety-net spending (25-year) |
| 4 | Revenue composition shares (stacked, FY2000–2025) |
| 5 | Income inequality evolution (Census quintile shares) |

### G.2 Distributional Impact Figures

| Figure | Description |
|--------|-------------|
| 6 | Distributional impact by quintile (spending cuts + tariff) |
| 7 | Burden decomposition by income percentile (stacked area) |
| 8 | Tariff pass-through: traded goods vs. services control |
| 9 | CPI price changes in tariff-affected goods |
| 10 | Tariff burden by quintile (absolute + % of income) |
| 11 | CBO counterfactual waterfall |

### G.3 Robustness Figures

| Figure | Description |
|--------|-------------|
| 12 | Specification curve (6 robustness dimensions) |
| 13 | Departure-from-trend prediction bands (forest plot) |
| 14 | B50 calibration diagram |

### G.4 Supplementary Figures

Figures 15–48: Descriptive budget visualizations, real-terms analysis, agency-level detail, historical B50 trends, SPM dose-response, state exposure maps, welfare analysis (log-scale). All figures are embedded in the PDF appendix; source data and scripts are available in the replication package.

\newpage

## Appendix G: Figures

![Departure-from-trend tests (4-panel: actual vs. trend)](figures/25yr_structural_breaks.png){width=90%}

![Customs revenue trajectory (with tariff regime markers)](figures/25yr_customs_trajectory.png){width=90%}

![Interest vs. safety-net spending (25-year trajectory)](figures/25yr_interest_vs_safetynet.png){width=90%}

![Revenue composition shares (stacked area, FY2000–2025)](figures/25yr_revenue_composition.png){width=90%}

![Income inequality evolution (Census quintile shares)](figures/25yr_inequality_evolution.png){width=90%}

![Distributional impact of FY2025 policy](figures/fig2_distributional_impact.png){width=90%}

![Burden decomposition by income percentile (stacked area)](figures/fig11_burden_decomposition.png){width=90%}

![Tariff pass-through: traded goods vs. services control](figures/fig13_services_price_acceleration.png){width=90%}

![CPI price changes in tariff-affected goods](figures/fig7_tariff_price_changes.png){width=90%}

![Tariff burden by income quintile](figures/fig8_tariff_burden_by_quintile.png){width=90%}

![CBO counterfactual waterfall (baseline to actual)](figures/fig16_counterfactual_waterfall.png){width=90%}

![Robustness specification summary (6 dimensions)](figures/fig15_specification_curve.png){width=90%}

![Departure-from-trend prediction bands (forest plot)](figures/fig12_structural_break_bands.png){width=90%}

![B50 calibration diagram (quintile person shares)](figures/fig14_b50_calibration.png){width=90%}

![Federal outlay composition (stacked area, FY2015-2025)](figures/01_outlay_composition.png){width=90%}

![Revenue by source (stacked area)](figures/02_revenue_composition.png){width=90%}

![Net interest vs. safety-net spending](figures/03_interest_vs_safety_net.png){width=90%}

![CPI essentials indexed (with tariff event markers)](figures/04_cpi_essentials.png){width=90%}

![Corporate profits vs. wages (indexed)](figures/05_profits_vs_wages.png){width=90%}

![Customs revenue spike (bar chart)](figures/06_customs_revenue_spike.png){width=90%}

![Federal deficit trend (with policy periods)](figures/07_deficit_trend.png){width=90%}

![Income security waterfall (FY2019-2025)](figures/09_income_security_waterfall.png){width=90%}

![Net interest as percent of GDP](figures/10_interest_pct_gdp.png){width=90%}

![FY2025 context dashboard (6-panel summary)](figures/25yr_fy2025_context_dashboard.png){width=90%}

![B50 transfer dependency and poverty (CPS ASEC benchmarks)](figures/25yr_poverty_and_benefits.png){width=90%}

![Real spending composition (stacked area, FY2000–2025)](figures/25yr_spending_composition.png){width=90%}

![Historical B50 income share and transfer dependency](figures/fig17_historical_b50.png){width=90%}

![Welfare-weighted loss (log-scale, CRRA $\sigma$=2)](figures/fig18_welfare_logscale.png){width=90%}

![State fiscal exposure index (dot plot)](figures/fig19_state_exposure_dots.png){width=90%}

![Income distribution by quintile (CPS ASEC)](figures/fig1_income_distribution.png){width=90%}

![SPM poverty dose-response (food program scenarios)](figures/fig20_spm_dose_response.png){width=90%}

![SCOTUS scenario: B50 per-person burden comparison (Appendix E)](figures/fig21_scotus_scenario_comparison.png){width=90%}

![Central combined scenario: quintile burden decomposition (Appendix E)](figures/fig22_scotus_quintile_decomposition.png){width=90%}

![Price stickiness and the incidence of tariff revocation (Appendix E)](figures/fig23_price_stickiness_flows.png){width=90%}

![SCOTUS scenario: sensitivity range and welfare impact (Appendix E)](figures/fig24_scotus_welfare_sensitivity.png){width=90%}

![Simulated distributional burden curve](figures/fig3_quantile_treatment_effects.png){width=90%}

![SPM poverty simulation](figures/fig4_spm_poverty_simulation.png){width=90%}

![State exposure classification map](figures/fig5_state_exposure.png){width=90%}

![Welfare-weighted impact (CRRA)](figures/fig6_welfare_weighted_impact.png){width=90%}

![B50 vs. T50 tariff cost by goods category](figures/fig9_b50_tariff_by_category.png){width=90%}

![Budget function waterfall (real terms)](figures/real_budget_function_waterfall.png){width=90%}

![Cumulative spending by tier (real terms)](figures/real_cumulative_by_tier.png){width=90%}

![Defense vs. social spending (real terms)](figures/real_defense_vs_social.png){width=90%}

![Interest payment timeline (real terms)](figures/real_interest_timeline.png){width=90%}

![Propensity classification comparison](figures/real_propensity_comparison.png){width=90%}

![Propensity stacked area chart](figures/real_propensity_stacked_area.png){width=90%}

![Tariff windfall flow diagram. Assumes 4.5% 10-yr rate (FRED DGS10), 20$\times$ P/E (conservative); equity ownership 93% top-10 (Fed 2023 SCF), bond ownership ~67% top-10 (Fed DFA)](figures/real_tariff_windfall_flow.png){width=90%}

![Top agencies by spending change](figures/real_top_agencies.png){width=90%}

