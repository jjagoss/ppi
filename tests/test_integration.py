# import pytest
# import pandas as pd
# from unittest.mock import patch
#
# from ppi.core.initialize_db import initialize_ppi_database
#
#
# class TestPPIIntegration:
#     @pytest.fixture
#     def mock_downloads(self):
#         """Mock the download functions to return test data."""
#         metadata = pd.DataFrame({
#             'series_id': ['WPS0111'],
#             'group_code': ['01'],
#             'item_code': ['11'],
#             'seasonal': ['S'],
#             'base_date': ['198200'],
#             'series_title': ['Farm products-Fresh fruits and melons'],
#             'begin_year': [2023],
#             'begin_period': ['M01'],
#             'end_year': [2023],
#             'end_period': ['M12']
#         })
#
#         series_data = pd.DataFrame({
#             'series_id': ['WPS0111'] * 5,
#             'year': [2023] * 5,
#             'period': ['M01', 'M02', 'M03', 'M04', 'M05'],
#             'value': [100.0, 101.0, 102.0, 103.0, 104.0],
#             'footnote_codes': [''] * 5
#         })
#
#         # Mock both the convenience functions and the class methods
#         patches = [
#             patch('src.ppi.core.utils.download_metadata.download_ppi_metadata',
#                   return_value=metadata),
#             patch('src.ppi.core.utils.download_series_data.download_ppi_commodity_data',
#                   return_value=series_data),
#             patch('src.ppi.core.utils.download_metadata.PPIMetaDataDownloader.download_metadata',
#                   return_value=metadata),
#             patch('src.ppi.core.utils.download_series_data.PPISeriesDataDownloader.download_series_data',
#                   return_value=series_data),
#             # Also mock pandas read_csv to prevent any actual HTTP requests
#             patch('pandas.read_csv',
#                   side_effect=lambda *args, **kwargs: metadata if 'wp.series' in args[0] else series_data)
#         ]
#
#         mocks = [patcher.start() for patcher in patches]
#         yield mocks[0], mocks[1]  # Return the first two mocks which correspond to our original interface
#
#         # Stop all patches
#         for patcher in patches:
#             patcher.stop()
#
#     def test_full_initialization(self, mock_downloads, tmp_path):
#         """
#         Test the complete initialization process from downloading data
#         to creating and populating the database.
#         """
#         mock_meta, mock_data = mock_downloads
#
#         manager = initialize_ppi_database(str(tmp_path))
#
#         mock_meta.assert_called_once()
#         mock_data.assert_called_once()
#
#         data = manager.get_series_data('WPS0111')
#         assert len(data) == 5
#         assert list(data['value']) == [100.0, 101.0, 102.0, 103.0, 104.0]
#
#         metadata = manager.get_series_metadata('WPS0111')
#         assert len(metadata) == 1
#         assert metadata['series_title'].iloc[0] == 'Farm products-Fresh fruits and melons'
