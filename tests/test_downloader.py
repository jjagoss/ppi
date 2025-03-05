from ppi_toolkit.database import METADATA_COLUMNS, COMMODITY_COLUMNS
from ppi_toolkit.joiner import PPIJoiner

def test_tables_exist(temp_db):
    """"Test that the metadata and commodities tables exist and include expected columns."""
    conn = temp_db.create_connection()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(metadata)")
    metadata_info = cur.fetchall()
    metadata_columns = [col[1] for col in metadata_info]
    for col in METADATA_COLUMNS:
        assert col in metadata_columns, f"Column {col} not found in metadata table"

    cur.execute("PRAGMA table_info(commodities)")
    commodities_info = cur.fetchall()
    commodities_columns = [col[1] for col in commodities_info]
    for col in COMMODITY_COLUMNS:
        assert col in commodities_columns, f"Column {col} not found in commodities table"


def test_import_metdata(temp_db):
    """Test that importing metadata adds rows to the metadata table"""
    temp_db.import_metadata()
    conn = temp_db.create_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM metadata")
    count = cur.fetchone()[0]
    conn.close()
    assert count > 0, "Now rows found in metadata table after import."


def test_import_commodities(temp_db):
    """Test that importing commodity data adds rows to the commodities table"""
    temp_db.import_commodities()
    conn = temp_db.create_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM commodities")
    count = cur.fetchone()[0]
    conn.close()
    assert count > 0, "Now rows found in commodities table after import."


def test_joiner(temp_db):
    temp_db.import_metadata()
    temp_db.import_commodities()

    joiner = PPIJoiner(db_path=temp_db.db_path)
    df = joiner.get_joined_data(series_id="WPS01220101")
    assert len(df) > 0
