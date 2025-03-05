import pytest

from ppi_toolkit.analyzer import PPIAnalyzer


def test_annualized_trends(temp_db):
    temp_db.import_metadata()
    temp_db.import_commodities()
    analyzer = PPIAnalyzer(db_path=temp_db.db_path)
    df_result = analyzer.compute_annualized_changes("WPS011101", 2015, 1, 2020, 12)
    last_row = df_result.iloc[-1]
    assert last_row["ann_3m"] == pytest.approx(-54.218964, abs=0.1)

