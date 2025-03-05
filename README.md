# PPI Toolkit

A Python library for retrieving, storing, and analyzing **Producer Price Index (PPI)** data from the U.S. Bureau of Labor Statistics (BLS). The library supports:

- Downloading BLS PPI metadata and current commodity data  
- Storing the data in a local SQLite database  
- Searching PPI data series by fuzzy matching or direct lookups  
- Computing annualized percentage changes (1-month, 3-month, 6-month, and 12-month horizons)  

---

## Features

- **Automated Data Ingestion**  
  Fetch metadata and commodity data directly from the BLS text files, then store them in a local SQLite database.

- **Clean, Well-Structured Database**  
  - `metadata` table for series information (e.g. `series_id`, `group_code`, `series_title`, etc.)  
  - `commodities` table for monthly observations (`year`, `period`, `value`, etc.)

- **Fuzzy Text Search**  
  Quickly locate series by approximate matching on their titles.

- **Annualized Changes Calculation**  
  Compute monthly annualized percentage changes over 1-, 3-, 6-, and 12-month intervals.

- **Easy Plotting Hooks (Optional)**  
  Integration points for generating charts using `matplotlib`, `plotly`, etc.

---

## Quickstart

Below is a minimal example of how to install and use the library:

### 1. Install the Library

```bash
pip install ppi-toolkit
```

### 2. Set up the database
```
from ppi_toolkit.database import PPIDataBase

db = PPIDataBase()
db.setup_and_import_data()
```

3. Search for a series
```
from ppi_toolkit.search import PPISearcher

searcher = PPISearcher()  # Uses ~/ppi.db by default
results = searcher.search_titles("steel scrap")

for match in results:
    print(match)
    # Example output: {'series_id': 'WPS101211', 'series_title': 'Carbon steel scrap', 'score': 90}

```

4. Join and analyze data

```
from ppi_toolkit.joiner import PPIJoiner
from ppi_toolkit.analyzer import PPIAnalyzer

# 1. Join data from both tables
joiner = PPIJoiner()
df_joined = joiner.get_joined_data("WPS011101")
print(df_joined.head())

# 2. Compute annualized changes
analyzer = PPIAnalyzer()
df_trends = analyzer.compute_annualized_changes("WPS011101", 2018, 1, 2023, 12)
print(df_trends[["date", "value", "ann_1m", "ann_3m", "ann_6m", "ann_12m"]].tail())
```

### License
This project is released under the MIT License. Feel free to use and modify it in personal or commercial projects, respecting the license terms.

### Acknowledgements 
- Data provided courtesy of the Bureau of Labor Statistics Producer Price Index.
