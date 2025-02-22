import pytest
import pandas as pd
from src.ppi.core.ppi_searcher import PPISearcher


class TestPPISearcher:
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing search functionality."""
        return pd.DataFrame({
            'series_id': [
                'WPS0111', 'WPS0112', 'WPS0211', 'WPS0311', 'WPS0411',
                'WPS1011', 'WPS1012', 'WPS1013'
            ],
            'group_code': [
                '01', '01', '02', '03', '04', '10', '10', '10'
            ],
            'item_code': [
                '11', '12', '11', '11', '11', '11', '12', '13'
            ],
            'seasonal': [
                'S', 'U', 'S', 'S', 'U', 'S', 'S', 'U'
            ],
            'base_date': [
                '198200', '198200', '198200', '198200', '198200',
                '198200', '198200', '198200'
            ],
            'series_title': [
                'Fresh fruits and melons', 'Fresh vegetables',
                'Cereal and bakery products', 'Textile products',
                'Leather products', 'Iron and steel', 'Nonferrous metals',
                'Metal containers'
            ],
            'begin_year': [2010, 2010, 2010, 2010, 2010, 2010, 2010, 2010],
            'begin_period': ['M01'] * 8,
            'end_year': [2023, 2023, 2023, 2023, 2020, 2023, 2023, 2023],
            'end_period': ['M12'] * 8
        })

    @pytest.fixture
    def mock_data_manager(self, sample_metadata):
        """Create a mock data manager that returns our sample metadata."""

        class MockDataManager:
            def get_series_metadata(self, series_id=None):
                if series_id:
                    return sample_metadata[sample_metadata['series_id'] == series_id]
                return sample_metadata

        return MockDataManager()

    @pytest.fixture
    def searcher(self, mock_data_manager):
        return PPISearcher(mock_data_manager)

    def test_search_by_keyword(self, searcher):
        result = searcher.search_by_keyword(keywords="fruits")
        assert len(result) == 1
        assert result.iloc[0]['series_id'] == 'WPS0111'

        results = searcher.search_by_keyword(keywords=['fruits', 'vegetables'], match_all=False)
        assert len(results) == 2
        assert set(results['series_id']) == {'WPS0111', 'WPS0112'}

    def test_search_by_category(self, searcher):
        results = searcher.search_by_category('01', include_subcategories=False)
        assert len(results) == 2
        assert set(results['series_id']) == {'WPS0111', 'WPS0112'}

        results = searcher.search_by_category('10', include_subcategories=True)
        assert len(results) == 3
        assert set(results['series_id']) == {'WPS1011', 'WPS1012', 'WPS1013'}

    def test_search_by_date_range(self, searcher):
        results = searcher.search_by_date_range(min_year=2015, max_year=2019, active_only=False)
        assert len(results) == 8

    def test_get_seasonal_status(self, searcher):
        """Test filtering by seasonal adjustment status."""
        # Get seasonally adjusted series
        results = searcher.get_seasonal_status(seasonal=True)
        assert len(results) == 5
        for idx, row in results.iterrows():
            assert row['seasonal'] == 'S'

        # Get non-seasonally adjusted series
        results = searcher.get_seasonal_status(seasonal=False)
        assert len(results) == 3
        for idx, row in results.iterrows():
            assert row['seasonal'] == 'U'

    def test_suggest_similar_series(self, searcher):
        """Test suggesting similar series."""
        # Find similar series to fruits in same category
        results = searcher.suggest_similar_series('WPS0111', same_category=True)
        assert len(results) == 1  # Only one other in category 01
        assert results.iloc[0]['series_id'] == 'WPS0112'

        # Find similar across categories
        results = searcher.suggest_similar_series('WPS0111', same_category=False)
        assert len(results) >= 1  # Should find some matches

    def test_get_category_map(self, searcher):
        """Test retrieving category map."""
        category_map = searcher.get_category_map()
        assert isinstance(category_map, dict)
        assert '01' in category_map
        assert '10' in category_map
        assert category_map['01'] == 'Farm Products'

    def test_get_summary_statistics(self, searcher):
        """Test summary statistics calculation."""
        stats = searcher.get_summary_statistics()
        assert stats['total_series'] == 8
        assert stats['seasonally_adjusted'] == 5
        assert stats['non_seasonally_adjusted'] == 3
        assert stats['category_01_Farm Products'] == 2
        assert stats['category_10_Metals and Metal Products'] == 3
