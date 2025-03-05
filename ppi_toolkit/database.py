import os
import sqlite3
import csv
from io import StringIO

import pandas as pd
import requests
import logging

METADATA_COLUMNS = ["series_id", "group_code", "item_code", "seasonal", "base_date",
                    "series_title", "footnote_codes", "begin_year", "begin_period",
                    "end_year", "end_period"]
COMMODITY_COLUMNS = ["series_id", "year", "period", "value", "footnote_codes"]

class PPIDataBase:
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser('~'), 'ppi_toolkit.db')
        self.METADATA_FILE = "https://download.bls.gov/pub/time.series/wp/wp.series"
        self.COMMODITY_FILE = "https://download.bls.gov/pub/time.series/wp/wp.data.0.Current"

    def create_connection(self, db_path: str = None):
        """Create a database connection to the SQLite database"""
        if db_path is None:
            db_path = self.db_path
        conn = sqlite3.connect(db_path)
        return conn

    def create_tables(self):
        """Create metadata and commodity tables."""
        conn = self.create_connection()
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS metadata")
        cur.execute("DROP TABLE IF EXISTS commodities")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
            series_id TEXT,
            group_code TEXT,
            item_code TEXT,
            seasonal TEXT,
            base_date TEXT,
            series_title TEXT,
            footnote_codes TEXT,
            begin_year TEXT,
            begin_period TEXT,
            end_year TEXT,
            end_period TEXT
        )
    """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id TEXT,
            year TEXT,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            FOREIGN KEY(series_id) REFERENCES metadata(series_id)
        )
    """)
        conn.commit()
        conn.close()

    def _import_data(self, file_path: str, table_name: str, header_names: list = None):
        headers = {'User-Agent': 'justinjagoss@gmail.com'}
        response = requests.get(file_path, headers=headers)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), delimiter='\t', header=None, names=header_names, skiprows=1)
        df["series_id"] = df["series_id"].astype(str).str.strip()
        conn = self.create_connection()
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()

    def import_metadata(self):
        self._import_data(self.METADATA_FILE, "metadata", header_names=METADATA_COLUMNS)

    def import_commodities(self):
        self._import_data(self.COMMODITY_FILE, "commodities", header_names=COMMODITY_COLUMNS)

    def setup_and_import_data(self):
        self.create_tables()
        self.import_metadata()
        self.import_commodities()
        logging.info("Database created and populated, ready for use!")


if __name__ == '__main__':
    ppi_database = PPIDataBase()
    ppi_database.setup_and_import_data()
