"""Runtime configuration for Job Scout."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Local runtime settings."""

    app_name: str = "job-scout"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/db/job_scout.db")
    profile_path: Path = Path("data/profiles/user_profile.json")
    evaluation_model_path: Path = Path("config/evaluation_model.json")
    capability_model_path: Path = Path("config/capability_model.json")


def get_settings() -> Settings:
    """Return default local settings."""
    data_dir = Path(os.getenv("JOB_SCOUT_DATA_DIR", "data"))
    database_path = Path(
        os.getenv("JOB_SCOUT_DATABASE_PATH", str(data_dir / "db" / "job_scout.db"))
    )
    profile_path = Path(
        os.getenv("JOB_SCOUT_PROFILE_PATH", str(data_dir / "profiles" / "user_profile.json"))
    )
    evaluation_model_path = Path(
        os.getenv("JOB_SCOUT_EVALUATION_MODEL_PATH", "config/evaluation_model.json")
    )
    capability_model_path = Path(
        os.getenv("JOB_SCOUT_CAPABILITY_MODEL_PATH", "config/capability_model.json")
    )
    return Settings(
        data_dir=data_dir,
        database_path=database_path,
        profile_path=profile_path,
        evaluation_model_path=evaluation_model_path,
        capability_model_path=capability_model_path,
    )
