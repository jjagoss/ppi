import pandas as pd
from unittest.mock import MagicMock, patch, Mock
from ppi.core.utils.download_metadata import PPIMetaDataDownloader
from ppi.core.utils.download_series_data import PPISeriesDataDownloader


class TestPPPIMetaDataDownloader:
    def test_process_metadata(self, downloader, sample_raw_metadata):
        """
        Test that metadata processing correctly cleans the data.
        """
        processed = downloader._process_metadata(sample_raw_metadata.copy())

        assert processed['series_id'].iloc[0] == 'WPS0111'
        assert processed['group_code'].iloc[0] == '01'

        assert processed['begin_period'].iloc[0] == 'M01'
