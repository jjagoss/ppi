# PPI Toolkit

A Python library for working with Producer Price Index (PPI) data from the Bureau of Labor Statistics.

## Features

- Download and store PPI data and metadata
- Calculate rolling inflation rates over different time horizons
- Search for relevant PPI series by keywords, categories, and date ranges
- Visualize price trends and compare multiple series
- Analyze seasonal patterns and trends

## Installation

```bash
pip install ppi-toolkit
```

## Quick Start
```
from ppi.core.initialize_db import initialize_ppi_database
from ppi.core.ppi_analyzer import PPIAnalyzer
from ppi.core.ppi_visualizer import PPIVisualizer
from ppi.core.ppi_searcher import PPISeriesSearcher


# Initialize the database
db_manager = initialize_ppi_database()

# Find relevant series
searcher = PPISeriesSearcher(db_manager)
fruit_series = searcher.search_by_keyword("fruits")

# Analyze inflation rates
analyzer = PPIAnalyzer(db_manager)
inflation_rates = analyzer.calculate_rolling_changes(fruit_series.iloc[0]['series_id'])

# Visualize results
visualizer = PPIVisualizer(db_manager, analyzer)
fig = visualizer.plot_price_trend(fruit_series.iloc[0]['series_id'])
fig.savefig('fruit_prices.png')
```