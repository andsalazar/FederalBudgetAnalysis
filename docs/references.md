# Literature & Data Sources

## Key References

All references cited in [`output/FINDINGS.md`](../output/FINDINGS.md) are listed
below, grouped by topic. The full annotated literature review is in
[`literature_review.md`](literature_review.md).

### Tariffs & Trade Policy
- Amiti, M., Redding, S. J., & Weinstein, D. E. (2019). The impact of the 2018 tariffs on prices and welfare. *Journal of Economic Perspectives*, 33(4), 187–210.
- Amiti, M., Redding, S. J., & Weinstein, D. E. (2020). Who's paying for the US tariffs? A longer-term perspective. *AEA Papers and Proceedings*, 110, 541–546.
- Cavallo, A., Gopinath, G., Neiman, B., & Tang, J. (2021). Tariff pass-through at the border and at the store. *American Economic Review: Insights*, 3(1), 19–34.
- Clausing, K. A., & Lovely, M. E. (2024). Why Trump's tariff proposals would harm working Americans. PIIE Policy Brief.
- Clausing, K. A., & Obstfeld, M. (2025). Tariffs as fiscal policy. NBER Working Paper No. 34192.
- Fajgelbaum, P. D., Goldberg, P. K., Kennedy, P. J., & Khandelwal, A. K. (2020). The return to protectionism. *Quarterly Journal of Economics*, 135(1), 1–55.
- Gopinath, G., & Neiman, B. (2026). The incidence of tariffs: Rates and reality. NBER Working Paper No. 34620.
- Leibovici, F., & Dunn, J. (2025). What have we learned from the U.S. tariff increases of 2018–19? *Federal Reserve Bank of St. Louis Review*.
- Minton, T., & Somale, M. (2025). Detecting tariff effects on consumer prices in real time. Federal Reserve FEDS Notes.
- Benguria, F., & Saffie, F. (2025). Rounding up the effect of tariffs on financial markets. NBER Working Paper No. 34036.
- The Budget Lab at Yale. (2026). The effect of tariffs on poverty. Budget Lab Working Paper.

### Distributional Fiscal Analysis & Income Inequality
- Piketty, T., Saez, E., & Zucman, G. (2018). Distributional national accounts: Methods and estimates for the United States. *Quarterly Journal of Economics*, 133(2), 553–609.
- Perese, K. (2017). CBO's new framework for analyzing the effects of means-tested transfers and federal taxes on the distribution of household income. CBO Working Paper 2017-09.
- Congressional Budget Office. (2022). The distribution of household income, 2019.
- Wolff, E. N., & Zacharias, A. (2007). The distributional consequences of government spending and taxation in the US, 1989 and 2000. *Review of Income and Wealth*, 53(4), 692–715.
- Bitler, M. P., Gelbach, J. B., & Hoynes, H. W. (2006). What mean impacts miss: Distributional effects of welfare reform experiments. *American Economic Review*, 96(4), 988–1012.

### Wealth Concentration & Asset Ownership
- Batty, M., Bricker, J., Briggs, J., et al. (2019). Introducing the Distributional Financial Accounts of the United States. *Finance and Economics Discussion Series* 2019-017, Federal Reserve Board.
- Bricker, J., Goodman, S., & Moore, K. B. (2020). Wealth and income concentration in the SCF: 1989–2019. *FEDS Notes*, Federal Reserve Board.
- Federal Reserve Board. (2023). Changes in U.S. family finances from 2019 to 2022: Evidence from the Survey of Consumer Finances. *Federal Reserve Bulletin*, 109(4). [Top 10% held 93% of directly and indirectly held equities; top 10% held approximately 67% of bonds and fixed-income securities.]
- Wolff, E. N. (2022). The stock market and the evolution of top wealth shares in the United States. *Journal of Economic Inequality*, 20, 587–609.
- Wolff, E. N. (2024). Inflation, interest, and the secular rise in wealth inequality in the United States: Is the Fed responsible? *Journal of Economic Issues*, 58(1), 1–32.

### Econometric Methods & Causal Inference
- Athey, S., & Imbens, G. W. (2017). The econometrics of randomized experiments. *Handbook of Economic Field Experiments*, 1, 73–140.
- Athey, S., & Imbens, G. W. (2023). Design-based analysis in difference-in-differences settings with staggered adoption. *Journal of Econometrics*, 226(1), 62–79.

### Federal Budget & Fiscal Policy
- Auerbach, A. J., & Gorodnichenko, Y. (2012). Measuring the output responses to fiscal policy. *American Economic Journal: Economic Policy*, 4(2), 1–27.
- Falkenheim, M. (2022). How changes in the federal budget affect the economy. CBO Working Paper.
- Saez, E., & Zucman, G. (2019). *The Triumph of Injustice*. Norton.
- Mertens, K., & Ravn, M. O. (2013). The dynamic effects of personal and corporate income tax changes. *American Economic Review*, 103(4), 1212–1247.
- Zidar, O. (2019). Tax cuts for whom? Heterogeneous effects of tax changes. *Journal of Political Economy*, 127(3), 1437–1472.
- Chetty, R., Grusky, D., Hell, M., Hendren, N., Manduca, R., & Narang, J. (2017). The fading American dream. *Science*, 356(6336), 398–406.

## Data Source Documentation

### FRED (Federal Reserve Economic Data)
- API Documentation: https://fred.stlouisfed.org/docs/api/fred/
- Data dictionary maintained in `config.yaml` under `collectors.fred.series`
- 48 macro series + 12 CPI sub-indices + 11 BEA NIPA government spending series

### CBO Public Data
- Historical Budget Data: https://www.cbo.gov/data/budget-economic-data
- Distribution of Household Income: https://www.cbo.gov/data/distribution-household-income
- Budget and Economic Outlook (Feb 2026): https://www.cbo.gov/publication/61882

### Treasury Fiscal Data
- API Documentation: https://fiscaldata.treasury.gov/api-documentation/
- Monthly Treasury Statement, Tables 5 (outlays by function) & 9 (outlays by agency)

### Census Bureau
- CPS ASEC: https://www.census.gov/programs-surveys/cps.html
- Historical Income Tables (H-2): https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html

### Bureau of Labor Statistics
- Consumer Expenditure Survey: https://www.bls.gov/cex/tables.htm
- CPI data: https://www.bls.gov/cpi/

See [`data/README.md`](../data/README.md) for full provenance, file manifests,
and step-by-step reproduction instructions.
