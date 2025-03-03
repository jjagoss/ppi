import logging
from pathlib import Path
from typing import Optional, Any

import io
import pandas as pd
import requests

from ppi.db_models.commodity_data import CommodityData


class PPISeriesDataDownloader:
    """
    Downloads and processes PPI series data that contains the commodity level
    inflation components on a month-over-month basis.
    """
    def __init__(self, cache_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        if cache_dir is None:
            cache_dir = Path.home() / "./ppi_cache"
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.required_columns = {
            "series_id",
            "year",
            "period",
            "value",
            "footnote_codes"
        }

    def download_series_data(self) -> pd.DataFrame:
        """
        Downloads and processes PPI commodities data

        Returns:
            Dataframe containing commodities inflation data with columns:
            - series_id: Unique id for the series
            - year: Int format of year of release
            - period: Str format of month of release
            - value: Indexed inflation amount
            - footnote_code: Any additional errata (often null)
        """

        try:
            headers = {
                'User-Agent': 'justinjagoss@gmail.com'
            }

            # Make the request with timeout and proper headers
            response = requests.get(
                "https://download.bls.gov/pub/time.series/wp/wp.data.1.AllCommodities",
                headers=headers,
                timeout=30  # Set a reasonable timeout
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Parse the content as a CSV using pandas
            commodity_df = pd.read_csv(
                io.StringIO(response.text),
                delimiter='\t',
                dtype={
                    'series_id': str,
                    'year': int,
                    'period': str,
                    'value': float,
                    'footnote_code': str
                }
            )
            self._process_data(commodity_df)
            self._validate_data(commodity_df)
            return commodity_df

        except Exception as e:
            self.logger.error(f"Failed to download series data: {e}")
            raise

    @staticmethod
    def _process_data(commodity_df: pd.DataFrame) -> pd.DataFrame:
        string_cols = ['series_id', 'period', 'footnote_code']
        for col in string_cols:
            if col in commodity_df.columns:
                commodity_df[col] = commodity_df[col].str.strip()

        commodity_df['series_date'] = pd.to_datetime(commodity_df['year'].astype(str) + '-' +
                                                     commodity_df['period'].str[1:] + '-01')
        return commodity_df

    @staticmethod
    def _validate_data(commodity_df) -> dict[str, Any]:
        valid_data = CommodityData(**commodity_df).model_dump()
        return valid_data


def download_ppi_commodity_data(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to download PPI commodities data

    Args:
         cache_dir: Optional directory for caching downloads

    Returns:
        Dataframe containing metadata
    """

    downloader = PPISeriesDataDownloader(cache_dir=cache_dir)
    return downloader.download_series_data()