from ppi_toolkit.search import PPISearcher


def test_ppi_searcher(temp_db):
    temp_db.import_metadata()

    search = PPISearcher(db_path=temp_db.db_path)
    result = search.search_titles("Steel")
    assert len(result) == 10
