"""Database boundary for Job Scout."""

from pathlib import Path
import sqlite3


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection for the configured path."""
    return sqlite3.connect(database_path)
