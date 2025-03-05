import os
import sqlite3
import pandas as pd
from rapidfuzz import process, fuzz


class PPISearcher:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser('~'), 'ppi_toolkit.db')
        self.db_path = db_path

    def _get_all_series_titles(self):
        """Retrun a Dataframe with (series_id, series_title)."""
        query = "SELECT series_id, series_title FROM metadata"
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        return df

    def search_titles(self, user_query: str, limit=10):
        """
        Return a list of the best matching series based on series_title using
        fuzzy matching.
        """
        df = self._get_all_series_titles()
        titles = df["series_title"].tolist()
        results = process.extract(user_query,
                                  titles,
                                  scorer=fuzz.WRatio,
                                  limit=limit)

        output = []
        for match_title, score, idx in results:
            row = df.iloc[idx]
            output.append({
                "series_id": row["series_id"],
                "series_title": row["series_title"],
                "score": score
            })
        output.sort(key=lambda x: x["score"], reverse=True)
        return output

