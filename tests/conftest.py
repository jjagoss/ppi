import pytest
import pandas as pd

from ppi.core.ppi_analyzer import PPIAnalyzer
from ppi.core.ppi_data_manager import PPIDataManager
from ppi.core.ppi_visualizer import PPIVisualizer
from ppi.core.utils.download_metadata import PPIMetaDataDownloader


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
def visualization_data():
    dates = pd.date_range(start='2022-01-01', period=24, freq='M')

    values = [100]
    for i in range(1, 24):
        month = (i % 12) + 1
        seasonal = 2 if month in [1, 2, 11, 12] else 0
        change = 0.005 + seasonal/100
        values.append(values[-1] * (1 + change))

    return pd.DataFrame({
        'series_id': ['WPS0111'] * 24,
        'year': [d.year for d in dates],
        'period': [f'M{d.month:02d}' for d in dates],
        'value': values,
        'footnote_codes': [''] * 24
    })


@pytest.fixture
def visualization_metadata():
    """Create sample metadata."""
    return pd.DataFrame({
        'series_id': ['WPS0111', 'WPS0112'],
        'group_code': ['01', '01'],
        'item_code': ['11', '12'],
        'seasonal': ['S', 'S'],
        'base_date': ['198200', '198200'],
        'series_title': ['Fresh fruits', 'Fresh vegetables'],
        'begin_year': [2022, 2022],
        'begin_period': ['M01', 'M01'],
        'end_year': [2023, 2023],
        'end_period': ['M12', 'M12']
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
def mock_data_manager(analysis_data, visualization_metadata):
    class MockDataManager:
        def __init__(self, data):
            self.data = data

        def get_series_data(self, series_id, start_year=None, end_year=None):
            data = analysis_data.copy()
            if start_year:
                data = data[data['year'] >= start_year]
            if end_year:
                data = data[data['year'] <= end_year]
            return data

        def get_series_metadata(self, series_id=None):
            return visualization_metadata[visualization_metadata['series_id'] == series_id]

    return MockDataManager(analysis_data)


@pytest.fixture
def visualizer(mock_data_manager):
    analyzer = PPIAnalyzer(mock_data_manager)
    return PPIVisualizer(mock_data_manager, analyzer)