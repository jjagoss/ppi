import os
import tempfile

import pytest

from ppi_toolkit.database import PPIDataBase


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, 'test_ppi.db')
        pdb = PPIDataBase()
        pdb.db_path = db_path
        pdb.create_tables()
        yield pdb
