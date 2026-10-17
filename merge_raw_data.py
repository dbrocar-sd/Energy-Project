"""
Merge the five raw EIA exports into one table: Top20_Energy_Panel.csv
(one row per country per year, 2005-2025). Values are copied unchanged.

Run from the repository folder:  python merge_raw_data.py
"""
import pandas as pd

RAW = "data_raw/"
YEARS = list(range(2005, 2026))


def add_rows(rows, country, column, values):
    """Store one value per year for one country and one column."""
    for year in YEARS:
        rows.append({"Country": country, "Year": year, "column": column,
                     "value": values.get(year)})


rows = []

# 1. Production and consumption (Excel). Each country has a name row followed by
#    7 production rows and 7 consumption rows, in this order:
fuels = ["Total", "Coal", "Natural Gas", "Petroleum", "Nuclear+Renewables",
         "Nuclear", "Renewables"]
pc = pd.read_excel(RAW + "Top20_ProductionConsumption.xlsx", header=None)
pc_years = pc.iloc[1, 1:].astype(int).tolist()
country = None
position = 0
for i in range(2, len(pc)):
    label = pc.iloc[i, 0]
    if isinstance(label, str) and not label.startswith(" "):   # country name row
        country = label.strip()
        position = 0
        continue
    section = "Production" if position < 7 else "Consumption"
    column = f"{section} {fuels[position % 7]} (quad Btu)"
    values = dict(zip(pc_years, pc.iloc[i, 1:]))
    add_rows(rows, country, column, values)
    position += 1

# 2. GDP (Excel): one row per country
gdp = pd.read_excel(RAW + "Top20_GDP.xlsx", header=None)
gdp_years = gdp.iloc[1, 1:].astype(int).tolist()
for i in range(3, len(gdp)):
    values = dict(zip(gdp_years, gdp.iloc[i, 1:]))
    add_rows(rows, gdp.iloc[i, 0].strip(), "GDP PPP (Billion 2015$)", values)

# 3. Population (CSV): first line is a report date, then a header, then a title row
pop = pd.read_csv(RAW + "Population.csv", skiprows=1)
for i in range(1, len(pop)):
    values = {int(y): pop.loc[i, y] for y in pop.columns[2:]}
    add_rows(rows, pop.iloc[i, 1].strip(), "Population (Thousands)", values)

# 4. Crude oil and natural gas trade (CSV): country row, "Imports" row, data row,
#    "Exports" row, data row
def read_trade(filename, fuel, unit):
    trade = pd.read_csv(RAW + filename, skiprows=1, dtype=str)
    country = None
    flow = None
    for i in range(len(trade)):
        label = str(trade.iloc[i, 1]).strip()
        if pd.isna(trade.loc[i, "API"]):
            if label in ["Imports", "Exports"]:
                flow = label
            else:
                country = label
            continue
        values = {}
        for y in YEARS:
            if str(y) in trade.columns:
                values[y] = pd.to_numeric(trade.loc[i, str(y)], errors="coerce")
        add_rows(rows, country, f"{flow} {fuel} ({unit})", values)

read_trade("Crude_oil_importsexports.csv", "Crude Oil", "Mb/d")
read_trade("Natural_gas_importexport.csv", "Natural Gas", "bcf")

# 5. Reshape: one row per country per year, one column per variable
long = pd.DataFrame(rows)
long["value"] = pd.to_numeric(long["value"], errors="coerce")
panel = long.pivot_table(index=["Country", "Year"], columns="column",
                         values="value", dropna=False).reset_index()

column_order = (["Country", "Year"]
                + [f"Production {f} (quad Btu)" for f in fuels]
                + [f"Consumption {f} (quad Btu)" for f in fuels]
                + ["GDP PPP (Billion 2015$)", "Population (Thousands)",
                   "Imports Crude Oil (Mb/d)", "Imports Natural Gas (bcf)",
                   "Exports Crude Oil (Mb/d)", "Exports Natural Gas (bcf)"])
panel = panel[column_order].sort_values(["Country", "Year"])
panel.to_csv("Top20_Energy_Panel.csv", index=False)
print("Saved Top20_Energy_Panel.csv", panel.shape)
