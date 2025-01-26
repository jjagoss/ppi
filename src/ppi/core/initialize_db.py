from pathlib import Path
from typing import Optional

from src.ppi.core.ppi_data_manager import PPIDataManager


def initialize_ppi_database(data_dir: Optional[str]) -> PPIDataManager:
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

    series_data = download_series_data()
    metadata = download_metadata()

    manager.update_data(series_data, metadata)

    return manager