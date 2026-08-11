"""
PITWALL Database Connection Helper.
"""

from typing import Optional
import duckdb
from backend.app.db.schema import get_db_connection


class DatabaseManager:
    """Singleton database manager for DuckDB connections."""

    _instance: Optional["DatabaseManager"] = None
    _conn: Optional[duckdb.DuckDBPyConnection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def connect(self, db_path: str = "data/pitwall.duckdb") -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = get_db_connection(db_path)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
