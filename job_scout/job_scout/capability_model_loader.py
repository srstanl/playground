"""Loader for the tracked Job Scout capability ontology."""

from __future__ import annotations

import json
from pathlib import Path

from job_scout.models import CapabilityDefinition, CapabilityModel


def load_capability_model(path: Path) -> CapabilityModel:
    """Load a capability model from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return CapabilityModel(
        model_version=payload.get("model_version", "v1"),
        capabilities=[
            CapabilityDefinition(
                name=item.get("name", ""),
                aliases=list(item.get("aliases", [])),
                tools=list(item.get("tools", [])),
            )
            for item in payload.get("capabilities", [])
        ],
    )
