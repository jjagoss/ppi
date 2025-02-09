import sqlite3

import pandas as pd


class TestPPIDataManger:
    def test_initialize_database(self, db_manager):
        """
        Test that database initialization creates the expected tables.
        """
        assert db_manager.db_path.exists()

        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='series_metadata'
            """)

            assert cursor.fetchone() is not None

    def test_update_data(self, db_manager, sample_data, sample_metadata):
        """
        Test that data updates work correctly.
        """
        db_manager.update_data(sample_data, sample_metadata)
        retrieved_data = db_manager.get_series_data('WPS0111')

        pd.testing.assert_frame_equal(
            retrieved_data.reset_index(drop=True),
            sample_data.reset_index(drop=True)
        )

    def test_get_series_data_with_date_range(self, db_manager, sample_data, sample_metadata):
        """
        Test that the date range filtering works.
        """
        db_manager.update_data(sample_data, sample_metadata)

        filtered_data = db_manager.get_series_data(
            'WPS0111',
            start_year=2023
        )
        assert len(filtered_data) == 5

        filtered_data = db_manager.get_series_data(
            'WPS0111',
            start_year=2024
        )
        assert len(filtered_data) == 0

    def test_get_latest_data_date(self, db_manager, sample_data, sample_metadata):
        """
        Test that we can correctly identify the latest data point.
        """
        db_manager.update_data(sample_data, sample_metadata)

        latest_year, latest_period = db_manager.get_latest_data_date()
        assert latest_year == 2023
        assert latest_period == 'M05'
