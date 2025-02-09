import pytest
import pandas as pd

from src.ppi.core.ppi_data_manager import PPIDataManager


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
def db_manager(tmp_path):
    """
    Create a temporary database manager for testing.
    Using tmp_path fixture ensures cleanup after tets.
    """
    db_path = tmp_path / 'test_ppi.db'
    return PPIDataManager(db_path)