import io

import pandas as pd
from typing import Optional, Dict, Any
import logging
from pathlib import Path
import pandera as pa
import requests
from ppi.db_models.metadata import Metadata


class PPIMetaDataDownloader:
    """
    Downloads and processes PPI series metadata that describes what each PPI series represents.
    This includes information like what products the series covers, whether it's seasonally
    adjusted, and its time coverage period.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        if cache_dir is None:
            cache_dir = Path.home() / ".ppi_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.required_columns = {
            "series_id",
            "group_code",
            "item_code",
            "seasonal",
            "base_data",
            "series_title",
            "begin_year",
            "begin_period",
            "end_year",
            "end_period"
        }

    def download_metadata(self) -> pd.DataFrame:
        """
        Download and process PPI commodities metadata.

        Returns:
            Dataframe containing series metadata with columns:
            - series_id: Unique id for the series
            - group_code: Major group code
            - item_code: Specific item within teh group
            - seasonal: whether series is seasonally adjusted ('S' or 'U')
            - base_date: Reference period of index values
            - series_title: Description of what the series measures
            - begin_year/period: Start of data coverage
            - end_year/period: End of data coverage
        """
        try:
            headers = {
                'User-Agent': 'justinjagoss@gmail.com'
            }

            self.logger.info("Downloading metadata from BLS...")
            response = requests.get(
                "https://download.bls.gov/pub/time.series/wp/wp.series",
                headers=headers,
                timeout=30
            )

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse the response
            metadata_df = pd.read_csv(
                io.StringIO(response.text),
                delimiter='\t',  # Fixed typo: was "deliter"
                dtype={
                    'series_id': str,
                    'group_code': str,
                    'item_code': str,
                    'seasonal': str,
                    'base_date': str,
                    'series_title': str,
                    'begin_year': int,
                    'begin_period': str,
                    'end_year': int,
                    'end_period': str
                }
            )
            self._process_metadata(metadata_df)
            self._validate_metadata(metadata_df)
            return metadata_df

        except Exception as e:
            self.logger.error(f"Failed to download metadata: {e}")
            raise

    @staticmethod
    def _process_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
        string_cols = ['series_id', 'group_code', 'item_code',
                       'seasonal', 'base_date', 'series_title',
                       'begin_period', 'end_period']

        for col in string_cols:
            if col in metadata_df.columns:
                metadata_df[col] = metadata_df[col].str.strip()

        for period_col in ['begin_period', 'end_period']:
            if period_col in metadata_df.columns:
                metadata_df[period_col] = metadata_df[period_col].str.upper()

        return metadata_df

    def _validate_metadata(self, metadata_df: pd.DataFrame) -> dict[str, Any]:
        try:
            valid_metadata = Metadata.validate(metadata_df)
            return valid_metadata

        except pa.errors.SchemaError as e:
            self.logger.error(f"Failed to validate metadata: {e}")


def download_ppi_metadata(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to download PPI metadata.

    Args:
         cache_dir: Optional directory for caching downloads

    Returns:
        Dataframe containing metadata
    """

    downloader = PPIMetaDataDownloader(cache_dir=cache_dir)
    return downloader.download_metadata()
