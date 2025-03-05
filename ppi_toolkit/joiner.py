import os
import sqlite3
import pandas as pd


class PPIJoiner:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), "ppi_toolkit.db")
        self.db_path = db_path

    def get_joined_data(self, series_id: str):
        """Returns a dataframe combining metadata and commodities for a single series_id"""
        query = """
        SELECT m.series_id
             , m.series_title
             , m.seasonal
             , c.year
             , c.period
             , c.value
        FROM metadata m
        JOIN commodities c ON m.series_id = c.series_id
        WHERE m.series_id = ?
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(series_id,))
        return df
