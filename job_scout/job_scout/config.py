"""Runtime configuration for Job Scout."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Local runtime settings."""

    app_name: str = "job-scout"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/job_scout.db")


def get_settings() -> Settings:
    """Return default local settings."""
    return Settings()
