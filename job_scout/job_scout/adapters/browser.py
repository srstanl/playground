"""Browser-tab ingestion contract for Job Scout."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from job_scout.models import JobPostingInput


@dataclass(frozen=True)
class BrowserTabJobCapture:
    """Stable adapter contract for browser-driven job capture."""

    source_system: str
    page_url: str
    raw_description: str
    captured_at: datetime
    page_title: str | None = None
    company: str | None = None
    title: str | None = None
    location: str | None = None
    external_ids: dict[str, str] = field(default_factory=dict)
    browser_name: str = ""
    window_id: str = ""
    tab_id: str = ""
    capture_method: str = "current_tab_text"
    selected_text: str = ""

    def to_job_posting_input(self) -> JobPostingInput:
        """Normalize browser capture into the core ingest payload."""
        description = self.raw_description.strip()
        if not description:
            raise SystemExit("browser capture raw_description is required")
        return JobPostingInput(
            source_system=self.source_system.strip(),
            raw_description=description,
            source_url=self.page_url.strip() or None,
            company=_string_or_none(self.company),
            title=_string_or_none(self.title),
            location=_string_or_none(self.location),
            external_ids=_normalized_external_ids(self.external_ids),
        )

    def source_reference(self) -> str:
        """Return a stable non-browser-specific capture reference string."""
        metadata = [
            f"captured_at={self.captured_at.isoformat()}",
            f"capture_method={self.capture_method.strip() or 'current_tab_text'}",
        ]
        if self.browser_name.strip():
            metadata.append(f"browser={self.browser_name.strip()}")
        if self.window_id.strip():
            metadata.append(f"window_id={self.window_id.strip()}")
        if self.tab_id.strip():
            metadata.append(f"tab_id={self.tab_id.strip()}")
        return f"{self.page_url.strip()} | " + " ".join(metadata)


def _string_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _normalized_external_ids(external_ids: dict[str, str]) -> dict[str, str]:
    return {
        str(key).strip(): str(value).strip()
        for key, value in external_ids.items()
        if str(key).strip() and str(value).strip()
    }
