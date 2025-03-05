import os
import sqlite3
import datetime
import pandas as pd


class PPIAnalyzer:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), "ppi_toolkit.db")
        self.db_path = db_path

    def _query_series(self, series_id: str) -> pd.DataFrame:
        """
        Helper to retrieve (year, period, value) for a series_id from the commodities table,
        plus its seasonal and series title from metadata.
        """
        query = """
        SELECT c.year, c.period, c.value
        FROM commodities c
        JOIN metadata m ON c.series_id = m.series_id
        WHERE c.series_id = ?
        ORDER BY c.year, c.period
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(series_id,))
        return df

    def _year_period_to_date(self, row):
        """
        Convert numeric year and period into a formatted date string.
        """
        y = int(row["year"])
        month = int(row["period"].replace("M", ""))
        return datetime.date(y, month, 1)

    def compute_annualized_changes(self, series_id: str, start_year: int,
                                   start_month: int, end_year: int, end_month: int) -> pd.DataFrame:
        """
        Returns a dataframe with columns for 1, 3, 6, 12 month annualized changes for the date range specified.
        Example usage:
            df_result = compute_annualized_changes("WPS011101", 2015,1, 2020,12)
        """
        df = self._query_series(series_id)
        df["date"] = df.apply(self._year_period_to_date, axis=1)
        df = df.sort_values("date")

        start_date = datetime.date(start_year, start_month, 1)
        end_date = datetime.date(end_year, end_month, 1)
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

        df["value_1m_ago"] = df["value"].shift(1)
        df["value_3m_ago"] = df["value"].shift(3)
        df["value_6m_ago"] = df["value"].shift(6)
        df["value_12m_ago"] = df["value"].shift(12)

        def annualized_pct(current, old, months):
            if old is None or old == 0 or pd.isna(old) or pd.isna(current):
                return None

            ratio = current / old
            exponent = 12.0 / months
            return (ratio ** exponent - 1) * 100

        df["ann_1m"] = df.apply(lambda r: annualized_pct(r["value"], r["value_1m_ago"], 1), axis=1)
        df["ann_3m"] = df.apply(lambda r: annualized_pct(r["value"], r["value_3m_ago"], 3), axis=1)
        df["ann_6m"] = df.apply(lambda r: annualized_pct(r["value"], r["value_6m_ago"], 6), axis=1)
        df["ann_12m"] = df.apply(lambda r: annualized_pct(r["value"], r["value_12m_ago"], 12), axis=1)

        df.drop(["value_1m_ago", "value_3m_ago", "value_6m_ago", "value_12m_ago"], axis=1, inplace=True)

        return df