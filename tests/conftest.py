import pytest
import pandas as pd

from src.ppi.core.ppi_data_manager import PPIDataManager
from src.ppi.core.utils.download_metadata import PPIMetaDataDownloader


@pytest.fixture
def sample_data():
    """
    Create sample data that mirrors our PPI data structure.
    This gives us controlled test data without needing external files.
    """
    return pd.DataFrame({
        'series_id': ['WPS0111'] * 5,
        'year': [2023] * 5,
        'period': ['M01', 'M02', 'M03', 'M04', 'M05'],
        'value': [100.0, 101.0, 102.0, 103.0, 104.0],
        'footnote_codes': [''] * 5
    })


@pytest.fixture
def sample_metadata():
    """
    Create sample metadata that matches our expected structure.
    """
    return pd.DataFrame({
        'series_id': ['WPS0111'],
        'group_code': ['01'],
        'item_code': ['11'],
        'seasonal': ['S'],
        'base_date': ['198200'],
        'series_title': ['Farm products-Fresh fruits and melons'],
        'begin_year': [2023],
        'begin_period': ['M01'],
        'end_year': [2023],
        'end_period': ['M12']
    })


@pytest.fixture
def sample_raw_metadata():
    """Create sample metadata in the format we expect from BLS."""
    return pd.DataFrame({
        'series_id': ['WPS0111  '],  # Note extra spaces
        'group_code': ['01  '],
        'item_code': ['11  '],
        'seasonal': ['S  '],
        'base_date': ['198200  '],
        'series_title': ['Farm products-Fresh fruits and melons  '],
        'begin_year': [2023],
        'begin_period': ['M01  '],
        'end_year': [2023],
        'end_period': ['M12  ']
    })


@pytest.fixture
def analysis_data():
    dates = pd.date_range(start="2023-01-01", periods=13, freq='M')

    return pd.DataFrame({
        'series_id': ['WPS0111'] * 13,
        'year': [d.year for d in dates],
        'period': [f'M{d.month:02d}' for d in dates],
        'value': [100 * (1.01) **i for i in range (13)],
        'footnote_codes': [''] * 13
    })


@pytest.fixture
def db_manager(tmp_path):
    """
    Create a temporary database manager for testing.
    Using tmp_path fixture ensures cleanup after tets.
    """
    db_path = tmp_path / 'test_ppi.db'
    return PPIDataManager(db_path)


@pytest.fixture
def downloader(tmp_path):
    """
    Create a downloader instance with a temporary cache directory
    """
    return PPIMetaDataDownloader(cache_dir=str(tmp_path))


@pytest.fixture
def mock_data_manager(analysis_data):
    class MockDataManager:
        def __init__(self, data):
            self.data = data

        def get_series_data(self, series_id):
            return self.data

    return MockDataManager(analysis_data)