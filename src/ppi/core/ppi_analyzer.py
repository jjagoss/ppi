import pandas as pd
import numpy as np
from typing import Optional, Dict
from .ppi_data_manager import PPIDataManager


class PPIAnalyzer:
    """
    Analyzes PPI data to calculate wholesale inflation measures.
    """

    def __init__(self, data_manager: PPIDataManager):
        self.data_manager = data_manager

    def calculate_rolling_changes(self,
                                  series_id: str,
                                  end_year: Optional[int] = None,
                                  end_period: Optional[str] = None
                                  ) -> Dict[str, float]:
        """
        Calculate annualized PPI changes over different rolling periods.

        Args:
            series_id: The PPI series to analyze
            end_year: Optional year to end analysis (defaults to latest)
            end_period: Optional period to end analysis (defaults to latest)

        Returns:
            Dictionary containing:
             - one_month: Annualized one month-over-month change
             - three_month: Annualized three month rolling average change
             - six_month: Annualized six month rolling average change
             - twelve_month: Annualized twelve month rolling average change
        """

        series_data = self.data_manager.get_series_data(series_id)
        series_data['date'] = pd.to_datetime(
            series_data.apply(
                lambda x: f"{x['year']}-{x['period'][1:]}-01",
                axis=1
            )
        )
        series_data = series_data.sort_values(by='date')

        if end_year is not None and end_period is not None:
            month = int(end_period[1:])
            end_date = pd.to_datetime(f"{end_year}-{month:02d}-01")
            series_data = series_data[series_data['date'] <= end_date]

        pct_change = series_data['value'].pct_change()

        def annualized_rolling_geo_mean(series: pd.Series, window: int) -> float:
            """
            Calculate annualized geometric mean of rolling window.
            """
            if len(series) < window:
                return np.nan

            growth_rates = (1 + series.iloc[-window:])
            geo_mean = np.prod(growth_rates) ** (1 / window) - 1
            return (1 + geo_mean) ** 12 - 1

        results = {
            'one_month': ((1 + pct_change.iloc[-1]) ** 12 - 1) * 100,
            'three_month': annualized_rolling_geo_mean(pct_change, 3) * 100,
            'six_month': annualized_rolling_geo_mean(pct_change, 6) * 100,
            'twelve_month': annualized_rolling_geo_mean(pct_change, 12) * 100
        }

        return results
