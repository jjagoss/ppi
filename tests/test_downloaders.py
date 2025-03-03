import pandas as pd
from unittest.mock import MagicMock, patch
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

    @patch('pandas.read_csv')
    def test_download_metadata(self, mock_read_csv, downloader, sample_raw_metadata):
        mock_read_csv.return_value = sample_raw_metadata
        """
        Test the full metadata download process.
        """
        result = downloader.download_metadata()
        mock_read_csv.assert_called_once()

        assert 'bls.gov' in mock_read_csv.call_args_list[0][0][0]
        assert result['series_id'].iloc[0] == 'WPS0111'