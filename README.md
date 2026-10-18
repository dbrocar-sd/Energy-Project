# Which Energy Producers Will Still Have Energy to Sell in 2030?

**MSBA 502: Analytics Programming · University of San Diego · Course Project**
**Team:** Austin Lucht, Dylan Brocar

This repository contains the combined EIA dataset, Python analysis notebook, data-merging script, and project documentation. The README provides an overview of the business problem, analytical methods, findings, and instructions for running the analysis.

---

## 1. Business problem

Countries that import energy, such as Japan, South Korea and most of Europe, depend on a small group of producing countries. Utilities in those countries usually secure supply with contracts that last 10 to 20 years.

The risk: a producer can be a large exporter today and still be a poor long-term partner. As its economy and population grow, it uses more of its own energy, so less is left to export. Mexico is a real example: in 2010 it could export about 15% of the energy it produced; by 2024 it was a net importer.

**Question:** Of the world's top 20 energy-producing countries, which will still be reliable energy exporters by 2030, and which should a buyer diversify away from?

**Audience:** the procurement and strategy team at an energy-importing utility.

| Stakeholder | Why they care |
|---|---|
| Utility procurement team (main audience) | Who to sign long-term contracts with |
| Commodity traders and investors | Where supply may tighten and prices rise |
| Producer-country governments | How long their export revenue will last |
| Consumers in importing countries | Stable energy prices and supply |

---

## 2. Repository contents

| File | Description |
|---|---|
| `README.md` | Project overview, methodology, findings, and instructions |
| `energy_supplier_analysis.ipynb` | Main Python notebook containing data cleaning, analysis, forecasting, clustering, and visualizations |
| `Top20_Energy_Panel.csv` | Combined dataset containing energy and economic data for 20 countries |
| `merge_raw_data.py` | Python script used to merge the original EIA datasets |
| `requirements.txt` | Python libraries required to run the analysis |

---

## 3. How to run the project

### Option A: Google Colab (easiest, nothing to install)
1. Download `energy_supplier_analysis.ipynb` and `Top20_Energy_Panel.csv` from this repository (click the file, then the download icon).
2. Go to [colab.research.google.com](https://colab.research.google.com), choose **File → Upload notebook**, and select the notebook.
3. Click the **folder icon** in the left sidebar, then the **upload icon**, and upload `Top20_Energy_Panel.csv`.
4. Choose **Runtime → Run all**. The charts are saved to a `figures` folder in the Files panel.

### Option B: On your own computer
1. Install Python 3, then install the packages: `pip install -r requirements.txt`
2. Download this repository (green **Code** button → **Download ZIP**) and unzip it.
3. In the unzipped folder, run `jupyter notebook energy_supplier_analysis.ipynb` and choose **Run All**.
4. Optional: run `python merge_raw_data.py` to rebuild `Top20_Energy_Panel.csv` from the raw EIA files.

---

## 4. Data

**Source:** U.S. Energy Information Administration (EIA), International Data Browser: https://www.eia.gov/international/data/world (downloaded October 2026).

**Countries:** the top 20 energy producers: Algeria, Australia, Brazil, Canada, China, India, Indonesia, Iran, Iraq, Kazakhstan, Kuwait, Mexico, Nigeria, Norway, Qatar, Russia, Saudi Arabia, South Africa, United Arab Emirates, United States.

| Raw file (`data_raw/`) | Contents | Units | Years used |
|---|---|---|---|
| `Top20_ProductionConsumption.xlsx` | Total energy production and consumption, by fuel | quadrillion Btu | 2005-2024 |
| `Top20_GDP.xlsx` | GDP at purchasing power parity | billion 2015 US$ | 2005-2025 |
| `Population.csv` | Population | thousands of people | 2005-2025 |
| `Crude_oil_importsexports.csv` | Crude oil imports and exports | thousand barrels per day | 2005-2018 (2020 for 5 countries) |
| `Natural_gas_importexport.csv` | Dry natural gas imports and exports | billion cubic feet | 2005-2024 |

**Merging.** `merge_raw_data.py` reshapes the five files into one table, `Top20_Energy_Panel.csv`: one row per country per year (20 countries × 21 years = 420 rows) and 22 columns. Values are copied unchanged; only the layout changes. Years before 2005 were dropped because many series are missing there.

**Data issues found and handled in the notebook:**
- The 2025 rows contain only GDP and population, so the analysis uses 2005-2024.
- EIA labels population "Mperson" (millions), but the values are thousands (China = 1,302,100), so we divide by 1,000.
- Crude oil trade data stops in 2018 for 15 countries because of EIA's publication lag. We leave these values missing instead of guessing.

---

## 5. Methods

All steps are in `energy_supplier_analysis.ipynb`, in this order.

**Cleaning.** Rename columns to short names, keep 2005-2024, convert population to millions, check missing values.

**New variables.**
- `net_exports` = production − consumption: the energy a country has left over to sell
- `export_share` = net_exports ÷ production: the share of output available to export
- `energy_intensity` = consumption ÷ GDP
- `consumption_growth`, `production_growth` = yearly % change

**Validation.** We checked whether production minus consumption matches real trade by correlating each country's oil and gas surplus with EIA's actual net exports (exports − imports). Correlation: **0.98 for oil, 0.995 for gas**, so the measure is a reliable stand-in for exports.

**Linear regression.** OLS of log(energy consumption) on log(GDP), log(population) and year. Using logs means the GDP coefficient reads as "% change in energy use for a 1% change in GDP." A second version adds country fixed effects, so each country is compared only with itself over time.

**Forecast to 2030.** For each country, a straight-line trend is fitted to production and to consumption (2010-2024) and extended to 2030. If consumption is growing faster than production, we calculate the year the two lines cross: when the country would stop exporting. Each country gets a status: net importer, becomes importer by 2040, shrinking exporter (export share falls more than 5 points), growing exporter (rises more than 5 points), or stable exporter.

**K-means clustering.** Three standardized features per country: export share (2024), average consumption growth (2015-2024), and production change (2015-2024). The elbow method pointed to k = 4.

**Supplier reliability score (0-100).** For the 17 countries that export today. Each input is scaled 0 to 1, then weighted:

| Weight | Input | Better when |
|---|---|---|
| 40% | Forecast export share in 2030 | higher |
| 30% | Average consumption growth 2015-2024 | lower |
| 20% | Production change 2015-2024 | higher |
| 10% | Production stability (std. dev. of yearly growth) | lower |

Top 5 = "lock in long-term", bottom 5 = "diversify away", the rest = "watch". Any country forecast to shrink or stop exporting is also "diversify away". As a sensitivity check, we recomputed the score with equal weights.

---

## 6. Results

**17 of the top 20 producers export energy; China, India and Mexico are net importers.**

![Net exports 2024](figures/chart1_net_exports.png)

**Home demand is catching up with production in several exporters.** Nigeria's production fell about 26% from 2015 to 2024; Algeria's home consumption nearly doubled since 2005; Mexico's lines crossed around 2015.

![Production vs consumption](figures/chart2_production_vs_consumption.png)

**Economic growth drives energy demand.** The regression explains 87% of the variation in energy consumption (R² = 0.874). A 1% rise in GDP goes with about a **1.24%** rise in energy use across countries, and **0.62%** within a country over time (fixed-effects model, R² = 0.995).

![GDP vs consumption](figures/chart3_gdp_vs_consumption.png)

**Forecast to 2030.**

| Status | Countries |
|---|---|
| Becomes importer by 2040 | Nigeria (about 2037), South Africa (about 2027) |
| Shrinking exporter | Algeria (export share 55% → 48%), Iran (31% → 23%) |
| Growing exporter | Canada, Russia, Brazil, United States |
| Stable exporter | Norway, Qatar, Kuwait, Australia, Iraq, Saudi Arabia, UAE, Kazakhstan, Indonesia |
| Net importer | China, India, Mexico |

![Forecast](figures/chart4_forecast.png)

**Four types of producer (k-means).**

| Cluster | Countries |
|---|---|
| Established exporters | Algeria, Australia, Canada, Kazakhstan, Kuwait, Nigeria, Norway, Qatar, Russia, Saudi Arabia, UAE |
| Exporters with fast-rising demand | Indonesia, Iran, Iraq |
| Near-balanced producers | Brazil, Mexico, South Africa, United States |
| Fast-growing importers | China, India |

![Clusters](figures/chart5_clusters.png)

**Supplier reliability ranking.** The ranking barely changes with equal weights (rank correlation 0.90).

![Ranking](figures/chart6_ranking.png)

---

## 7. Recommendation

| Recommendation | Countries |
|---|---|
| **Lock in long-term contracts** | Norway, Qatar, Australia, Canada, Kazakhstan |
| **Watch** | United Arab Emirates, Kuwait, Brazil, Saudi Arabia, Russia, United States |
| **Diversify away** | Algeria, Indonesia, Nigeria, Iran, Iraq, South Africa |

Iraq exports a large share of its output today, but its home demand is growing 7.2% a year, the fastest in the data, so its surplus is unlikely to last.

**Bottom line:** the biggest producer is not always the safest supplier. Watch home demand, not just production.

---

## 8. Limitations and future work

**Limitations**
- Forecasts are straight-line trends; they cannot capture sanctions, new discoveries, price shocks or policy changes.
- EIA's international browser does not provide proved reserves, so we cannot estimate how long each country's supply will last.
- Crude oil trade data ends in 2018 for most countries (used only for validation).
- Totals combine all fuels, so a country can export gas while importing oil.

**Future work (MSBA 503)**
- Add proved reserves and oil and gas prices from other sources
- Use time-series forecasting (ARIMA or Prophet) instead of straight lines
- Add bilateral trade flows to see which importers depend on which suppliers

---

## 9. Contributions

| Team member | Contribution | Share |
|---|---|---|
| [Partner A] | Data collection, cleaning, new variables, validation, regression, forecast | __% |
| [Partner B] | Clustering, reliability score, sensitivity check, charts | __% |

[Add a note on tools used, including any AI assistance, as required by the course policy.]
