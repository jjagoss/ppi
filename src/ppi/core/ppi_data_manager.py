import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import logging

class PPIDataManager:
    """
    Managed PPI (Producer Price Index) data storage and retrieval.
    Handles initial setup and periodic updates of the database.
    """

    def __init__(self, db_path: Path = Path("ppi_data.db")):
        """
        InInitialize the data manager with a specified database path.

        Args:
            db_path (Path): Path to where the database should be stored.
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)

        # Create database if it doesn't exist
        self.initialize_database()

    def initialize_database(self):
        """Set up the initial database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create tables for series metadata
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS series_metadata (
                series_id TEXT PRIMARY KEY,
                group_code TEXT,
                item_code TEXT
                seasonal TEXT
                base_data TEXT
                series_title TEXT
                begin_year INTEGER
                begin_period TEXT
                end_year INTEGER
                end_period TEXT
                )
            """)
            conn.commit()

    def update_data(self, series_data: pd.DataFrame, metadata: pd.DataFrame):
        """
        Update the database with new data.

        Args:
        series_data: Dataframe containing time series values
        metadata: Dataframe containing series metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            metadata.to_sql('series_metadata', conn, if_exists='replace', index=False)
            series_data.to_sql('series_data', conn, if_exists='replace', index=False)

            self.logger.info(f"Updated database with {len(series_data)} data points and {len(metadata)} metadata records")

    def get_series_data(self, series_id: str, start_year: Optional[int] = None,
                        end_year: Optional[int] = None) -> pd.DataFrame:

        """
        Retrieve data for a specific series.

        Args:
            series_id: The series identifier to retrieve
            start_year: Optional start year filter
            end_year: Optional end year filter

        Returns:
            Dataframe containing the requested time series data
        """

        query = "SELECT * FROM series_data WHERE series_id = ?"
        params = [series_id]

        if start_year is not None:
            query += " AND year >= ?"
            params.append(start_year)

        if end_year is not None:
            query += " AND year <= ?"
            params.append(end_year)

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(query, conn, params=params)

    def get_series_metadata(self, series_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve mdatadata for one or all series

        Args:
            series_id: Optional specific series to retrieve metadata for

        Returns:
            DataFrame containing the requested metadata
        """
        query = "SELECT * FROM series_metadata"
        params = None

        if series_id is not None:
            query += " WHERE series_id = ?"
            params = [series_id]

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(query, conn, params=params)

    def get_latest_data_date(self) -> Tuple[int, str]:
        """
        Get the most recent data in the database

        Returns:
            Tuple of (year, period representing the latest data point
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT year, period
            FROM series_data
            ORDER BY year DESC, period DESC
            LIMIT 1
            """)
            return cursor.fetchone()

    def cleanup(self):
        """Remove the database file."""
        if self.db_path.exists():
            self.db_path.unlink()
            self.logger.info(f"Removed database file {self.db_path}")
