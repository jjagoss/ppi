from pathlib import Path
from typing import Optional

from ppi.core.ppi_data_manager import PPIDataManager
from ppi.core.utils.download_metadata import download_ppi_metadata
from ppi.core.utils.download_series_data import download_ppi_commodity_data


def initialize_ppi_database(data_dir=None) -> PPIDataManager:
    """
    Initialize the PPI database with initial data download.

    Args:
        data_dir: Optional directory to store the database.
                 If None, uses the current working directory.

    Returns:
        Configured PPIDataManager instance
    """
    if data_dir is None:
        data_dir = Path.cwd() / "ppi_data"
    else:
        data_dir = Path(data_dir)

    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "ppi_data.db"

    manager = PPIDataManager(str(db_path))

    series_data = download_ppi_commodity_data()
    metadata = download_ppi_metadata()

    manager.update_data(series_data, metadata)

    return manager
