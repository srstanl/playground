"""Job posting extraction and signal detection."""

from __future__ import annotations

from collections.abc import Iterable
import re

from job_scout.domain.models import (
    CapabilityModel,
    CompensationBand,
    CompensationRange,
    EvaluationModel,
    EvidenceItem,
    ExtractionResult,
    JobPosting,
)


def extract_job_posting(
    job_posting: JobPosting,
    evaluation_model: EvaluationModel,
    capability_model: CapabilityModel,
) -> ExtractionResult:
    """Normalize a job posting into structured evaluation fields."""
    text = job_posting.raw_description
    lowered = text.lower()
    title = (job_posting.title or _first_non_empty_line(text) or "unknown").strip()
    normalized_title = _normalize_role_title(title)
    seniority = _detect_seniority(title, text)
    employment_type = _detect_employment_type(title, text)
    work_mode = _detect_work_mode(lowered, evaluation_model)
    location_text = job_posting.location or _extract_location_text(text, evaluation_model)
    detected_tools, detected_capabilities = _extract_capability_signals(text, capability_model)
    engineering_persona, engineering_persona_scores, persona_evidence = _detect_engineering_persona(
        text,
        detected_capabilities,
        evaluation_model,
    )
    required_skills, preferred_skills, skill_evidence = _extract_skills(
        text,
        evaluation_model,
        detected_tools,
    )
    responsibilities = _extract_bullets(text)
    compensation = _extract_compensation(text)
    risks = _extract_risks(lowered, evaluation_model)
    semantic_shapes = _classify_semantic_shapes(text, detected_capabilities)
    domain_signals = [keyword for keyword in evaluation_model.domain_keywords if keyword in lowered]
    visa_or_clearance_requirements = _extract_requirement_matches(
        lowered,
        evaluation_model.authorization_patterns,
    )
    required_experience = _extract_experience(
        text,
        preferred=False,
        evaluation_model=evaluation_model,
    )
    preferred_experience = _extract_experience(
        text,
        preferred=True,
        evaluation_model=evaluation_model,
    )
    evidence = [
        EvidenceItem(topic="title", snippet=title),
        EvidenceItem(topic="seniority", snippet=seniority, is_inference=True),
        *persona_evidence,
        *skill_evidence,
    ]

    if work_mode != "unknown":
        evidence.append(EvidenceItem(topic="work_mode", snippet=work_mode, is_inference=True))
    if compensation.minimum is not None or compensation.maximum is not None:
        evidence.append(
            EvidenceItem(
                topic="compensation",
                snippet=_format_compensation(compensation),
                is_inference=True,
            )
        )

    return ExtractionResult(
        role_title_normalized=normalized_title,
        role_summary=_summarize_text(text),
        seniority=seniority,
        employment_type=employment_type,
        location_text=location_text,
        work_mode=work_mode,
        engineering_persona=engineering_persona,
        engineering_persona_scores=engineering_persona_scores,
        semantic_shapes=semantic_shapes,
        detected_tools=detected_tools,
        detected_capabilities=detected_capabilities,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        required_experience=required_experience,
        preferred_experience=preferred_experience,
        responsibilities=responsibilities,
        compensation=compensation,
        visa_or_clearance_requirements=visa_or_clearance_requirements,
        domain_signals=domain_signals,
        risks=risks,
        evidence=evidence,
    )


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        candidate = line.strip()
        if candidate:
            return candidate
    return ""


def _normalize_role_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9+.#/ -]", "", title.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or "unknown"


def _detect_seniority(title: str, text: str) -> str:
    title_lowered = title.lower()
    if "senior" in title_lowered and "staff" in title_lowered:
        return "senior_staff"
    if any(token in title_lowered for token in ["principal", "distinguished"]):
        return "principal"
    if any(token in title_lowered for token in ["staff", "lead"]):
        return "staff"
    if "senior" in title_lowered:
        return "senior"
    lowered = text.lower()
    if re.search(r"\b[5-9]\+?\s+years\b", lowered):
        return "senior"
    if any(token in title_lowered for token in ["mid"]) or any(
        token in lowered for token in ["3+ years", "4+ years"]
    ):
        return "mid"
    if any(token in title_lowered for token in ["junior", "entry"]) or any(
        token in lowered for token in ["1+ years", "2+ years"]
    ):
        return "junior"
    return "unknown"


def _detect_employment_type(title: str, text: str) -> str:
    lowered = f"{title}\n{text}".lower()
    if "full-time" in lowered or "full time" in lowered or "exempt position" in lowered:
        return "full_time"
    if "part-time" in lowered or "part time" in lowered:
        return "part_time"
    if "intern" in lowered or "internship" in lowered:
        return "intern"
    if re.search(r"\bcontract(or)?\b", lowered) and "full-time" not in lowered and "full time" not in lowered:
        return "contract"
    return "unknown"


def _detect_work_mode(lowered: str, evaluation_model: EvaluationModel) -> str:
    for label, patterns in evaluation_model.work_mode_terms.items():
        if any(pattern in lowered for pattern in patterns):
            return label
    return "unknown"


def _extract_location_text(text: str, evaluation_model: EvaluationModel) -> str:
    all_terms = [
        pattern
        for patterns in evaluation_model.work_mode_terms.values()
        for pattern in patterns
    ]
    for line in text.splitlines():
        stripped = line.strip()
        if any(term in stripped.lower() for term in all_terms):
            return stripped
    return ""


def _extract_skills(
    text: str,
    evaluation_model: EvaluationModel,
    detected_tools: list[str],
) -> tuple[list[str], list[str], list[EvidenceItem]]:
    lowered = text.lower()
    required: list[str] = []
    preferred: list[str] = []
    evidence: list[EvidenceItem] = []

    for keyword in evaluation_model.skill_keywords:
        if keyword not in lowered and keyword not in detected_tools:
            continue
        snippet = _find_snippet(text, keyword)
        evidence.append(EvidenceItem(topic="skill", snippet=snippet or keyword))
        if _is_preferred_skill(lowered, keyword, evaluation_model):
            preferred.append(keyword)
        else:
            required.append(keyword)

    return sorted(set(required)), sorted(set(preferred) - set(required)), evidence


def _extract_capability_signals(
    text: str,
    capability_model: CapabilityModel,
) -> tuple[list[str], list[str]]:
    lowered = text.lower()
    detected_tools: list[str] = []
    detected_capabilities: list[str] = []

    for capability in capability_model.capabilities:
        alias_matched = any(alias.lower() in lowered for alias in capability.aliases)
        tool_matches = [tool.lower() for tool in capability.tools if tool.lower() in lowered]
        if alias_matched or tool_matches:
            detected_capabilities.append(capability.name)
            detected_tools.extend(tool_matches)

    return sorted(set(detected_tools)), sorted(set(detected_capabilities))


def _is_preferred_skill(lowered: str, keyword: str, evaluation_model: EvaluationModel) -> bool:
    return any(
        marker in lowered and keyword in lowered
        for marker in evaluation_model.preferred_skill_markers
    )


def _extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")):
            bullets.append(stripped[1:].strip())
    return bullets[:8]


def _extract_compensation(text: str) -> CompensationRange:
    bands: list[CompensationBand] = []
    band_pattern = re.compile(
        r"(?P<level>senior|staff|principal)?[^\n$]{0,40}?\$?\s?(?P<min>\d{2,3}(?:,\d{3})+|\d{2,3}k)\s*[–-]\s*\$?\s?(?P<max>\d{2,3}(?:,\d{3})+|\d{2,3}k)",
        re.IGNORECASE,
    )
    for match in band_pattern.finditer(text):
        level = (match.group("level") or "").lower()
        bands.append(
            CompensationBand(
                level=level,
                minimum=_parse_money(match.group("min")),
                maximum=_parse_money(match.group("max")),
            )
        )
    lowered = text.lower()
    interval = "hourly" if any(token in lowered for token in ["hour", "hourly", "/hr"]) else "annual"
    if not bands:
        return CompensationRange(interval=interval)
    minimum = min(band.minimum for band in bands if band.minimum is not None)
    maximum = max(band.maximum for band in bands if band.maximum is not None)
    return CompensationRange(
        currency="USD",
        minimum=minimum,
        maximum=maximum,
        interval=interval,
        bands=bands,
    )


def _parse_money(value: str) -> float:
    normalized = value.lower().replace(",", "").strip()
    if normalized.endswith("k"):
        return float(normalized[:-1]) * 1000
    return float(normalized)


def _extract_requirement_matches(lowered: str, patterns: list[str]) -> list[str]:
    return [pattern for pattern in patterns if pattern in lowered]


def _extract_experience(text: str, preferred: bool, evaluation_model: EvaluationModel) -> list[str]:
    results: list[str] = []
    markers = tuple(evaluation_model.preferred_skill_markers)
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if "year" not in lowered:
            continue
        is_preferred_line = any(marker in lowered for marker in markers)
        if is_preferred_line == preferred:
            results.append(stripped)
    return results[:5]


def _extract_risks(lowered: str, evaluation_model: EvaluationModel) -> list[str]:
    risks: list[str] = []
    tentative_clearance = any(
        token in lowered
        for token in ["may be required", "ability to obtain", "eligible to obtain"]
    )
    if "public trust" in lowered and tentative_clearance:
        risks.append("public_trust_possible_medium")
    if "security clearance" in lowered and tentative_clearance:
        risks.append("clearance_review")
    if "active ts/sci" in lowered or "existing clearance required" in lowered:
        risks.append("clearance_existing_blocker")
    for rule in evaluation_model.risk_rules:
        percentage_patterns = [pattern for pattern in rule.patterns if pattern.endswith("%")]
        text_patterns = [pattern for pattern in rule.patterns if not pattern.endswith("%")]
        if percentage_patterns and all(pattern in lowered for pattern in percentage_patterns) and any(
            pattern in lowered for pattern in text_patterns
        ):
            risks.append(rule.label)
            continue
        if any(pattern in lowered for pattern in rule.patterns):
            if rule.label == "travel_requirement":
                if "travel" in lowered and any(token in lowered for token in ["25%", "50%", "75%"]):
                    risks.append("travel_blocker")
            else:
                if rule.label == "clearance_required" and (
                    "public trust" in lowered or tentative_clearance
                ):
                    continue
                risks.append(rule.label)
    return sorted(set(risks))


def _summarize_text(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    summary = " ".join(sentences[:2]).strip()
    return summary[:280]


def _find_snippet(text: str, keyword: str) -> str:
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    start = max(0, match.start() - 40)
    end = min(len(text), match.end() + 60)
    return " ".join(text[start:end].split())


def _format_compensation(compensation: CompensationRange) -> str:
    if compensation.bands:
        return "; ".join(
            f"{band.level or 'band'}:{int(band.minimum or 0)}-{int(band.maximum or 0)}"
            for band in compensation.bands
        )
    parts: list[str] = []
    if compensation.minimum is not None:
        parts.append(str(int(compensation.minimum)))
    if compensation.maximum is not None:
        parts.append(str(int(compensation.maximum)))
    return " - ".join(parts)


def _detect_engineering_persona(
    text: str,
    detected_capabilities: list[str],
    evaluation_model: EvaluationModel,
) -> tuple[str, dict[str, int], list[EvidenceItem]]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    evidence_terms: dict[str, list[str]] = {}

    for persona, terms in evaluation_model.engineering_persona_signals.items():
        matches = [term for term in terms if term.lower() in lowered]
        if matches:
            scores[persona] = min(5, len(matches))
            evidence_terms[persona] = matches[:2]

    capability_bonus_map = {
        "delivery_enablement": {"continuous_delivery", "observability"},
        "platform_delivery": {"continuous_delivery", "observability"},
        "platform_infrastructure": {
            "cloud_enablement",
            "infrastructure_automation",
            "container_orchestration",
        },
        "infrastructure_ownership": {"observability", "container_orchestration"},
        "operations": {"observability", "container_orchestration"},
        "security": {"identity_access"},
    }
    capability_set = set(detected_capabilities)
    for persona, capability_names in capability_bonus_map.items():
        overlap = capability_set & capability_names
        if overlap:
            scores[persona] = min(5, scores.get(persona, 0) + len(overlap))
            evidence_terms.setdefault(persona, []).extend(sorted(overlap))

    if not scores:
        return "unknown", {}, []

    best_persona, _best_score = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )[0]
    evidence = [
        EvidenceItem(topic="engineering_persona", snippet=term, is_inference=True)
        for term in evidence_terms.get(best_persona, [])[:2]
    ]
    return best_persona, {key: min(5, value) for key, value in scores.items()}, evidence


def _classify_semantic_shapes(text: str, detected_capabilities: list[str]) -> dict[str, int]:
    lowered = text.lower()
    capability_set = set(detected_capabilities)
    shapes: dict[str, int] = {}

    engineering_enablement = 0
    if _contains_any(
        lowered,
        [
            "enablement",
            "developer experience",
            "coach",
            "mentoring",
            "guardrails",
            "knowledge sharing",
            "developer productivity",
            "engineering capacity",
        ],
    ):
        engineering_enablement += 3
    if "continuous_delivery" in capability_set or "observability" in capability_set:
        engineering_enablement += 2
    shapes["engineering_enablement"] = min(5, max(1, engineering_enablement))

    platform_engineering = 0
    if _contains_any(lowered, ["platform", "internal developer platform", "developer platform"]):
        platform_engineering += 3
    if "cloud_enablement" in capability_set or "infrastructure_automation" in capability_set:
        platform_engineering += 2
    if "continuous_delivery" in capability_set:
        platform_engineering += 1
    if _contains_any(
        lowered,
        ["cloud infrastructure", "infrastructure automation", "deployment standardization"],
    ):
        platform_engineering += 1
    shapes["platform_engineering"] = min(5, max(1, platform_engineering))

    delivery_systems = 0
    if _contains_any(lowered, ["release", "delivery pipeline", "deployment", "ci/cd"]):
        delivery_systems += 3
    if "continuous_delivery" in capability_set:
        delivery_systems += 2
    shapes["delivery_systems"] = min(5, max(1, delivery_systems))

    compliance_delivery = 0
    if _contains_any(
        lowered,
        ["compliance", "audit", "regulated", "security controls", "public sector", "federal"],
    ):
        compliance_delivery += 3
    if _contains_any(lowered, ["sensitive data", "governance", "quality gates"]):
        compliance_delivery += 2
    shapes["compliance_regulated_delivery"] = min(5, max(1, compliance_delivery))

    professional_services = 1
    if _contains_any(lowered, ["client", "customers", "professional services", "consulting"]):
        professional_services += 2
    if _contains_any(lowered, ["travel", "engagements"]):
        professional_services += 1
    shapes["professional_services"] = min(5, professional_services)

    return shapes


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)
