import pandas as pd
from datetime import datetime
from src.ppi.core.ppi_analyzer import PPIAnalyzer


class TestPPIAnalyzer:
    def test_calculate_rolling_changes(self, mock_data_manager):
        analyzer = PPIAnalyzer(mock_data_manager)
        results = analyzer.calculate_rolling_changes('WPS0111')

        assert abs(results['one_month'] - 12.68) < 0.1
        assert 12.0 < results['three_month'] < 13.0
        assert 12.0 < results['six_month'] < 13.0
        assert 12.0 < results['twelve_month'] < 13.0

    def test_end_date_filtering(self, mock_data_manager):
        analyzer = PPIAnalyzer(mock_data_manager)

        results = analyzer.calculate_rolling_changes(
            'WPS0111',
            end_year=2023,
            end_period='M06'
        )

        assert abs(results['one_month'] - 12.68) < 0.1

    def test_insufficient_data(self, mock_data_manager):
        """Test handling of insufficient data for rolling windows."""
        # Create data with only 2 months
        short_data = mock_data_manager.get_series_data('WPS0111').iloc[:2]

        class ShortDataManager:
            def get_series_data(self, series_id):
                return short_data

        analyzer = PPIAnalyzer(ShortDataManager())
        results = analyzer.calculate_rolling_changes('WPS0111')

        # One month should work, longer periods should be NaN
        assert not pd.isna(results['one_month'])
        assert pd.isna(results['three_month'])
        assert pd.isna(results['six_month'])
        assert pd.isna(results['twelve_month'])
