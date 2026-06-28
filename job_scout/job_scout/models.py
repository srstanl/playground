"""Domain models and schema placeholders for Job Scout."""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class JobPosting:
    """Initial job posting placeholder model."""

    company: Optional[str] = None
    title: Optional[str] = None
    source: str = "manual"
    raw_description: str = ""
