"""Runtime configuration for Job Scout."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Local runtime settings."""

    app_name: str = "job-scout"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/job_scout.db")
    profile_path: Path = Path("profiles/user_profile.local.json")
    evaluation_model_path: Path = Path("profiles/evaluation_model.json")
    capability_model_path: Path = Path("profiles/capability_model.json")


def get_settings() -> Settings:
    """Return default local settings."""
    data_dir = Path(os.getenv("JOB_SCOUT_DATA_DIR", "data"))
    database_path = Path(
        os.getenv("JOB_SCOUT_DATABASE_PATH", str(data_dir / "job_scout.db"))
    )
    profile_path = Path(
        os.getenv("JOB_SCOUT_PROFILE_PATH", "profiles/user_profile.local.json")
    )
    evaluation_model_path = Path(
        os.getenv("JOB_SCOUT_EVALUATION_MODEL_PATH", "profiles/evaluation_model.json")
    )
    capability_model_path = Path(
        os.getenv("JOB_SCOUT_CAPABILITY_MODEL_PATH", "profiles/capability_model.json")
    )
    return Settings(
        data_dir=data_dir,
        database_path=database_path,
        profile_path=profile_path,
        evaluation_model_path=evaluation_model_path,
        capability_model_path=capability_model_path,
    )
