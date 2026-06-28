"""Deterministic evaluation helpers for Job Scout."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from functools import lru_cache
import json
import re

from job_scout.capability_model_loader import load_capability_model
from job_scout.config import get_settings
from job_scout.evaluation_model_loader import load_evaluation_model
from job_scout.profile_loader import load_user_profile
from job_scout.models import (
    CapabilityModel,
    CompensationBand,
    CompensationRange,
    EvaluationModel,
    EvaluationProvenance,
    EvaluationSummary,
    EvidenceItem,
    ExtractionResult,
    JobEvaluation,
    JobPosting,
    ScoreDimension,
    ScoringResult,
    UserProfile,
)


@lru_cache(maxsize=1)
def get_default_evaluation_model() -> EvaluationModel:
    """Load the tracked repository evaluation model once per process."""
    return load_evaluation_model(get_settings().evaluation_model_path)


@lru_cache(maxsize=1)
def get_default_user_profile() -> UserProfile:
    """Load the local user profile once per process."""
    return load_user_profile(get_settings().profile_path)


@lru_cache(maxsize=1)
def get_default_capability_model() -> CapabilityModel:
    """Load the tracked capability ontology once per process."""
    return load_capability_model(get_settings().capability_model_path)


def evaluate_job_posting(
    job_posting: JobPosting,
    evaluation_model: EvaluationModel | None = None,
    user_profile: UserProfile | None = None,
    capability_model: CapabilityModel | None = None,
) -> JobEvaluation:
    """Evaluate a stored job posting with deterministic heuristics."""
    model = evaluation_model or get_default_evaluation_model()
    profile = user_profile or get_default_user_profile()
    capabilities = capability_model or get_default_capability_model()
    extraction = extract_job_posting(job_posting, model, capabilities)
    scoring = score_extraction(extraction, model, profile)
    overall_score = _compute_overall_score(scoring.dimensions)
    confidence_score = _compute_confidence_score(extraction, scoring.dimensions)
    recommendation = _recommendation_for(
        overall_score,
        confidence_score,
        scoring.blocking_concerns,
        model,
    )
    headline = _headline_for(extraction, recommendation, overall_score)
    narrative = _build_narrative(extraction, scoring, recommendation)

    return JobEvaluation(
        job_posting_id=job_posting.id,
        summary=EvaluationSummary(
            headline=headline,
            recommendation=recommendation,
            overall_score=overall_score,
            confidence_score=confidence_score,
            narrative=narrative,
        ),
        extraction=extraction,
        scoring=scoring,
        provenance=EvaluationProvenance(
            source_system=job_posting.source_system,
            source_url=job_posting.source_url,
            evaluated_at=datetime.now(UTC),
        ),
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
    required_experience = _extract_experience(text, preferred=False, evaluation_model=evaluation_model)
    preferred_experience = _extract_experience(text, preferred=True, evaluation_model=evaluation_model)
    evidence = [
        EvidenceItem(topic="title", snippet=title),
        EvidenceItem(topic="seniority", snippet=seniority, is_inference=True),
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


def score_extraction(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoringResult:
    """Apply the profile-aware rubric to an extraction result."""
    dimensions = [
        _problem_shape_alignment_dimension(extraction, evaluation_model, user_profile),
        _role_scope_alignment_dimension(extraction, evaluation_model, user_profile),
        _tool_adjacency_dimension(extraction, evaluation_model, user_profile),
        _domain_alignment_dimension(extraction, evaluation_model, user_profile),
        _compensation_alignment_dimension(extraction, evaluation_model, user_profile),
        _location_alignment_dimension(extraction, evaluation_model, user_profile),
        _risk_alignment_dimension(extraction, evaluation_model, user_profile),
        _identity_drift_dimension(extraction, evaluation_model, user_profile),
    ]

    strengths: list[str] = []
    gaps: list[str] = []
    blocking_concerns: list[str] = []
    review_flags: list[str] = []
    risk_categories = _build_risk_categories(extraction)

    for dimension in dimensions:
        if dimension.score >= 4:
            strengths.append(f"{dimension.name}: {dimension.rationale}")
        elif dimension.score <= 2:
            gaps.append(f"{dimension.name}: {dimension.rationale}")

    if risk_categories.get("blocker"):
        blocking_concerns.append("Posting includes blocking constraints.")
    elif risk_categories.get("onboarding") or risk_categories.get("moderate"):
        review_flags.append("Clarify clearance or public trust expectations.")
    if any("travel" in risk for risk in extraction.risks):
        review_flags.append("Clarify travel expectations.")
    if extraction.work_mode == "onsite" and not extraction.location_text:
        blocking_concerns.append("Onsite requirement is present without clear location detail.")

    return ScoringResult(
        dimensions=dimensions,
        strengths=strengths,
        gaps=gaps,
        blocking_concerns=blocking_concerns,
        review_flags=sorted(set(review_flags)),
        risk_categories=risk_categories,
    )


def evaluation_to_pretty_json(evaluation: JobEvaluation) -> str:
    """Serialize an evaluation result as stable pretty JSON."""
    payload = asdict(evaluation)
    return json.dumps(payload, indent=2, default=_json_default, sort_keys=True)


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"unsupported type: {type(value)!r}")


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
    if any(token in title_lowered for token in ["mid"]) or any(token in lowered for token in ["3+ years", "4+ years"]):
        return "mid"
    if any(token in title_lowered for token in ["junior", "entry"]) or any(token in lowered for token in ["1+ years", "2+ years"]):
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
    all_terms = [pattern for patterns in evaluation_model.work_mode_terms.values() for pattern in patterns]
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
    return any(marker in lowered and keyword in lowered for marker in evaluation_model.preferred_skill_markers)


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
    if any(token in lowered for token in ["hour", "hourly", "/hr"]):
        interval = "hourly"
    else:
        interval = "annual"
    if not bands:
        return CompensationRange(interval=interval)
    minimum = min(band.minimum for band in bands if band.minimum is not None)
    maximum = max(band.maximum for band in bands if band.maximum is not None)
    return CompensationRange(currency="USD", minimum=minimum, maximum=maximum, interval=interval, bands=bands)


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
        token in lowered for token in ["may be required", "ability to obtain", "eligible to obtain"]
    )
    if "public trust" in lowered and any(token in lowered for token in ["may be required", "ability to obtain", "eligible to obtain"]):
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
                    "public trust" in lowered
                    or tentative_clearance
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


def _dimension_weight(evaluation_model: EvaluationModel, name: str, default: float) -> float:
    return evaluation_model.dimensions.get(name, default)


def _problem_shape_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    positive_terms = _lowered_strings(
        user_profile.problem_spaces.primary
        + user_profile.problem_spaces.secondary
        + user_profile.value_proposition.supporting
        + [user_profile.value_proposition.primary]
        + user_profile.evaluation_preferences.prioritize
        + user_profile.identity_guardrails.always_preserve
    )
    summary_text = _extraction_text(extraction)
    matched = _matching_terms(summary_text, positive_terms)
    capability_bonus = len(extraction.detected_capabilities)
    semantic_bonus = max(extraction.semantic_shapes.values(), default=0) // 2
    score = min(
        5,
        _score_from_match_count(len(matched) + min(capability_bonus, 2) + min(semantic_bonus, 2), strong_threshold=6, medium_threshold=3),
    )
    rationale = (
        f"Posting aligns with {len(matched)} preferred problem-shape signals and {len(extraction.detected_capabilities)} capability signals."
        if matched
        else "Posting does not strongly signal the preferred problem shape."
    )
    evidence = [EvidenceItem(topic="problem_shape", snippet=term, is_inference=True) for term in matched[:2]]
    evidence.extend(
        EvidenceItem(topic="capability", snippet=capability, is_inference=True)
        for capability in extraction.detected_capabilities[:2]
    )
    return ScoreDimension(
        name="problem_shape_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "problem_shape_alignment", 0.40),
        rationale=rationale,
        evidence=evidence,
    )


def _role_scope_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    summary_text = _extraction_text(extraction)
    preferred_roles = _lowered_strings(
        user_profile.targeting.target_roles + user_profile.targeting.acceptable_roles
    )
    avoid_terms = _lowered_strings(
        user_profile.problem_spaces.avoid_primary + user_profile.constraints.deal_breakers
    )
    matched_roles = _matching_terms(summary_text, preferred_roles)
    matched_avoid = _matching_terms(summary_text, avoid_terms)
    if matched_avoid:
        score = 1
        rationale = f"Posting signals avoided role scope: {', '.join(matched_avoid[:2])}."
    elif matched_roles:
        score = 5 if any(role in matched_roles for role in _lowered_strings(user_profile.targeting.target_roles)) else 4
        rationale = f"Posting scope matches preferred roles: {', '.join(matched_roles[:2])}."
    else:
        score = 3
        rationale = "Posting scope is not clearly aligned or misaligned."
    evidence = [EvidenceItem(topic="role_scope", snippet=item, is_inference=True) for item in (matched_roles or matched_avoid)[:3]]
    return ScoreDimension(
        name="role_scope_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "role_scope_alignment", 0.20),
        rationale=rationale,
        evidence=evidence,
    )


def _tool_adjacency_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    extracted_skills = {skill.lower() for skill in extraction.required_skills + extraction.preferred_skills}
    extracted_tools = set(extraction.detected_tools)
    profile_skills = {
        skill.lower()
        for skill in (
            user_profile.skills.languages
            + user_profile.skills.frameworks
            + user_profile.skills.cloud
            + user_profile.skills.delivery
            + user_profile.skills.observability
            + user_profile.skills.security_compliance
        )
    }
    matched = sorted((extracted_skills | extracted_tools) & profile_skills)
    capability_overlap = _capability_overlap_count(extraction, user_profile)
    score = _score_from_match_count(len(matched) + capability_overlap, strong_threshold=6, medium_threshold=3)
    rationale = (
        f"Posting shares {len(matched)} tool adjacencies and {capability_overlap} capability adjacencies with the profile."
        if matched
        else "Posting shows little direct tool adjacency, but capability adjacency is preferred over exact tooling."
    )
    evidence = [EvidenceItem(topic="tool_adjacency", snippet=skill, is_inference=True) for skill in matched[:2]]
    evidence.extend(
        EvidenceItem(topic="capability", snippet=capability, is_inference=True)
        for capability in extraction.detected_capabilities[:2]
    )
    return ScoreDimension(
        name="tool_adjacency",
        score=score,
        weight=_dimension_weight(evaluation_model, "tool_adjacency", 0.10),
        rationale=rationale,
        evidence=evidence,
    )


def _domain_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    summary_text = _extraction_text(extraction)
    preferred_terms = _lowered_strings(
        user_profile.problem_spaces.secondary
        + user_profile.constraints.nice_to_have
        + user_profile.identity_guardrails.always_preserve
    )
    matched = _matching_terms(summary_text, preferred_terms)
    environment_signals = _environment_signals(extraction)
    score = _score_from_match_count(
        len(matched) + min(len(extraction.detected_capabilities), 1) + min(len(environment_signals), 2),
        strong_threshold=4,
        medium_threshold=2,
    )
    rationale = (
        f"Posting aligns with environment signals in {', '.join(environment_signals[:3])}."
        if environment_signals
        else f"Posting aligns with {len(matched)} preferred domain or environment signals."
        if matched
        else "Posting has limited domain/environment overlap with the profile."
    )
    evidence = [EvidenceItem(topic="environment_alignment", snippet=term, is_inference=True) for term in matched[:2]]
    evidence.extend(
        EvidenceItem(topic="environment_alignment", snippet=signal, is_inference=True)
        for signal in environment_signals[:2]
    )
    return ScoreDimension(
        name="environment_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "environment_alignment", 0.10),
        rationale=rationale,
        evidence=evidence,
    )


def _compensation_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    has_comp = extraction.compensation.minimum is not None or extraction.compensation.maximum is not None
    minimum_target = user_profile.preferences.compensation.minimum_base
    score = 3
    rationale = "Compensation is not disclosed; keeping neutral."
    if has_comp:
        compensation_floor = _relevant_compensation_floor(extraction.compensation, extraction.seniority)
        if compensation_floor >= minimum_target > 0:
            score = 5
            rationale = "Compensation meets or exceeds the profile minimum."
        elif minimum_target > 0 and compensation_floor < minimum_target:
            score = 1
            rationale = "Compensation appears below the profile minimum."
        else:
            score = 4
            rationale = "Compensation is disclosed but no minimum preference is configured."
    return ScoreDimension(
        name="compensation_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "compensation_alignment", 0.10),
        rationale=rationale,
        evidence=[item for item in extraction.evidence if item.topic == "compensation"][:1],
    )


def _location_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    preferred_modes = {value.lower() for value in user_profile.preferences.work_mode}
    acceptable_modes = {value.lower() for value in user_profile.preferences.acceptable_work_mode}
    location_text = extraction.location_text.lower()
    if extraction.work_mode in preferred_modes:
        score = 5
        rationale = f"Work mode matches preferred mode: {extraction.work_mode}."
    elif extraction.work_mode in acceptable_modes:
        score = 4
        rationale = f"Work mode matches acceptable mode: {extraction.work_mode}."
    elif any(term.lower() in location_text for term in user_profile.preferences.locations.avoid):
        score = 1
        rationale = "Location text contains an avoided location or arrangement."
    elif extraction.work_mode == "onsite":
        score = 1
        rationale = "Onsite work conflicts with the preferred remote-first profile."
    elif extraction.work_mode == "unknown":
        score = 3
        rationale = "Work mode is unclear; keeping this neutral."
    else:
        score = 2
        rationale = f"Work mode {extraction.work_mode} is outside the preferred arrangements."
    return ScoreDimension(
        name="location_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "location_alignment", 0.05),
        rationale=rationale,
        evidence=[item for item in extraction.evidence if item.topic == "work_mode"][:1],
    )


def _risk_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    summary_text = _extraction_text(extraction)
    blockers = _matching_terms(summary_text, _lowered_strings(user_profile.constraints.deal_breakers))
    must_haves = _matching_terms(summary_text, _lowered_strings(user_profile.constraints.must_have))
    risk_categories = _build_risk_categories(extraction)
    blocker_count = len(risk_categories.get("blocker", []))
    moderate_count = len(risk_categories.get("moderate", []))
    onboarding_count = len(risk_categories.get("onboarding", []))
    raw_risk_count = blocker_count + moderate_count + onboarding_count + len(blockers)
    if blockers or blocker_count:
        score = 1
        rationale = f"Posting hits deal-breaker or blocker signals: {', '.join((blockers or extraction.risks)[:2])}."
    else:
        score = max(1, min(5, 4 + (1 if must_haves else 0) - moderate_count - min(onboarding_count, 1)))
        rationale = (
            "Few blocking constraints detected and at least one must-have signal is present."
            if must_haves and raw_risk_count == 0
            else "Risk is low, with only informational or onboarding friction."
            if moderate_count == 0 and blocker_count == 0
            else f"Detected {moderate_count} moderate and {blocker_count} blocker-level risks."
        )
    evidence = [EvidenceItem(topic="risk_alignment", snippet=value, is_inference=True) for value in (blockers or extraction.risks or must_haves)[:3]]
    return ScoreDimension(
        name="risk_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "risk_alignment", 0.05),
        rationale=rationale,
        evidence=evidence,
    )


def _identity_drift_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    summary_text = _extraction_text(extraction)
    preserve_terms = _lowered_strings(
        user_profile.identity_guardrails.always_preserve
        + user_profile.problem_spaces.primary
        + user_profile.targeting.target_roles
    )
    drift_terms = _lowered_strings(
        user_profile.identity_guardrails.never_optimize_for
        + user_profile.problem_spaces.avoid_primary
        + user_profile.constraints.deal_breakers
    )
    preserved = _matching_terms(summary_text, preserve_terms)
    drifted = _matching_terms(summary_text, drift_terms)
    top_shapes = {name for name, score in extraction.semantic_shapes.items() if score >= 4}
    preferred_shapes = {
        "engineering_enablement",
        "platform_engineering",
        "delivery_systems",
        "compliance_regulated_delivery",
    }
    shape_bonus = len(top_shapes & preferred_shapes)
    if drifted:
        score = 1
        rationale = f"Posting pulls toward avoided identity signals: {', '.join(drifted[:2])}."
    else:
        score = max(2, min(5, 2 + min(len(preserved), 2) + min(shape_bonus, 1)))
        rationale = (
            "Role is identity-consistent with platform, delivery, and enablement work."
            if score >= 4
            else "Role fit is plausible, but identity consistency is not yet strong."
        )
    evidence = [EvidenceItem(topic="identity_drift", snippet=value, is_inference=True) for value in (preserved or drifted)[:3]]
    return ScoreDimension(
        name="identity_drift",
        score=score,
        weight=_dimension_weight(evaluation_model, "identity_drift", 0.05),
        rationale=rationale,
        evidence=evidence,
    )


def _compute_overall_score(dimensions: list[ScoreDimension]) -> int:
    total = sum((dimension.score / 5.0) * dimension.weight for dimension in dimensions)
    return round(total * 100)


def _compute_confidence_score(extraction: ExtractionResult, dimensions: list[ScoreDimension]) -> int:
    evidence_points = min(len(extraction.evidence) * 6, 36)
    structure_points = 0
    if extraction.role_title_normalized != "unknown":
        structure_points += 16
    if extraction.required_skills:
        structure_points += 16
    if extraction.responsibilities:
        structure_points += 10
    if extraction.location_text or extraction.work_mode != "unknown":
        structure_points += 10
    if extraction.compensation.minimum is not None or extraction.compensation.maximum is not None:
        structure_points += 6
    dimension_points = 12 if len(dimensions) >= 8 else 0
    return min(100, evidence_points + structure_points + dimension_points)


def _lowered_strings(values: list[str]) -> list[str]:
    return [value.lower() for value in values if value]


def _matching_terms(text: str, terms: list[str]) -> list[str]:
    matches: list[str] = []
    for term in terms:
        normalized = term.strip().lower()
        if normalized and normalized in text:
            matches.append(normalized)
    return sorted(set(matches))


def _extraction_text(extraction: ExtractionResult) -> str:
    return " ".join(
        [
            extraction.role_title_normalized,
            extraction.role_summary.lower(),
            extraction.work_mode.lower(),
            extraction.employment_type.lower(),
            extraction.location_text.lower(),
            " ".join(f"{key} {value}" for key, value in extraction.semantic_shapes.items()).lower(),
            " ".join(extraction.detected_tools).lower(),
            " ".join(extraction.detected_capabilities).lower(),
            " ".join(extraction.required_skills).lower(),
            " ".join(extraction.preferred_skills).lower(),
            " ".join(extraction.responsibilities).lower(),
            " ".join(extraction.domain_signals).lower(),
            " ".join(extraction.risks).lower(),
        ]
    )


def _score_from_match_count(match_count: int, strong_threshold: int, medium_threshold: int) -> int:
    if match_count >= strong_threshold:
        return 5
    if match_count >= medium_threshold:
        return 4
    if match_count >= 1:
        return 3
    return 2


def _classify_semantic_shapes(text: str, detected_capabilities: list[str]) -> dict[str, int]:
    lowered = text.lower()
    capability_set = set(detected_capabilities)
    shapes: dict[str, int] = {}

    engineering_enablement = 0
    if any(
        term in lowered
        for term in [
            "enablement",
            "developer experience",
            "coach",
            "mentoring",
            "guardrails",
            "knowledge sharing",
            "developer productivity",
            "engineering capacity",
        ]
    ):
        engineering_enablement += 3
    if "continuous_delivery" in capability_set or "observability" in capability_set:
        engineering_enablement += 2
    shapes["engineering_enablement"] = min(5, max(1, engineering_enablement))

    platform_engineering = 0
    if any(term in lowered for term in ["platform", "internal developer platform", "developer platform"]):
        platform_engineering += 3
    if "cloud_enablement" in capability_set or "infrastructure_automation" in capability_set:
        platform_engineering += 2
    if "continuous_delivery" in capability_set:
        platform_engineering += 1
    if any(term in lowered for term in ["cloud infrastructure", "infrastructure automation", "deployment standardization"]):
        platform_engineering += 1
    shapes["platform_engineering"] = min(5, max(1, platform_engineering))

    delivery_systems = 0
    if any(term in lowered for term in ["release", "delivery pipeline", "deployment", "ci/cd"]):
        delivery_systems += 3
    if "continuous_delivery" in capability_set:
        delivery_systems += 2
    shapes["delivery_systems"] = min(5, max(1, delivery_systems))

    compliance_delivery = 0
    if any(term in lowered for term in ["compliance", "audit", "regulated", "security controls", "public sector", "federal"]):
        compliance_delivery += 3
    if any(term in lowered for term in ["sensitive data", "governance", "quality gates"]):
        compliance_delivery += 2
    shapes["compliance_regulated_delivery"] = min(5, max(1, compliance_delivery))

    professional_services = 1
    if any(term in lowered for term in ["client", "customers", "professional services", "consulting"]):
        professional_services += 2
    if any(term in lowered for term in ["travel", "engagements"]):
        professional_services += 1
    shapes["professional_services"] = min(5, professional_services)

    return shapes


def _relevant_compensation_floor(compensation: CompensationRange, seniority: str) -> float:
    if compensation.bands:
        preferred_levels: list[str] = []
        if seniority == "senior_staff":
            preferred_levels = ["staff", "senior"]
        elif seniority == "staff":
            preferred_levels = ["staff"]
        elif seniority == "principal":
            preferred_levels = ["principal"]
        elif seniority == "senior":
            preferred_levels = ["senior"]
        for level in preferred_levels:
            for band in compensation.bands:
                if band.level == level and band.maximum is not None:
                    return band.maximum
        for band in compensation.bands:
            if band.maximum is not None:
                return band.maximum
    return compensation.maximum or compensation.minimum or 0


def _build_narrative(
    extraction: ExtractionResult,
    scoring: ScoringResult,
    recommendation: str,
) -> str:
    top_shapes = [name.replace("_", " ") for name, score in sorted(extraction.semantic_shapes.items(), key=lambda item: item[1], reverse=True) if score >= 4][:3]
    top_dimensions = {dimension.name: dimension for dimension in scoring.dimensions}
    fit_bits: list[str] = []
    if top_shapes:
        fit_bits.append(f"it is shaped around {', '.join(top_shapes)}")
    if top_dimensions.get("identity_drift") and top_dimensions["identity_drift"].score >= 4:
        fit_bits.append("it stays close to your platform and enablement identity")
    if top_dimensions.get("environment_alignment") and top_dimensions["environment_alignment"].score >= 4:
        fit_bits.append("the operating environment looks consistent with your preferred enterprise and regulated work")
    fit_text = "; ".join(fit_bits) if fit_bits else "the role shows some adjacency to your preferred work, but the shape is not definitive"

    concern_bits = scoring.blocking_concerns[:2] + scoring.review_flags[:2]
    if not concern_bits and scoring.gaps:
        concern_bits = scoring.gaps[:2]
    concern_text = "; ".join(concern_bits) if concern_bits else "no major structural concerns stand out from the posting"
    recommendation_map = {
        "apply": "applying",
        "consider": "considering",
        "needs_review": "reviewing further",
        "skip": "skipping",
    }
    recommendation_text = recommendation_map.get(recommendation, recommendation.replace("_", " "))
    return (
        f"This role is worth {recommendation_text} because {fit_text}. "
        f"The main follow-up is {concern_text}."
    )


def _environment_signals(extraction: ExtractionResult) -> list[str]:
    text = _extraction_text(extraction)
    signals: list[str] = []
    signal_terms = {
        "enterprise_scale": ["enterprise", "large-scale", "distributed systems"],
        "regulated_environment": ["regulated", "audit", "security controls", "governance"],
        "sensitive_data": ["sensitive data", "pci", "hipaa", "sox"],
        "compliance": ["compliance", "compliant", "quality gates"],
        "public_sector": ["public sector", "federal", "government"],
        "professional_services": ["professional services", "consulting", "client-facing"],
    }
    for label, terms in signal_terms.items():
        if any(term in text for term in terms):
            signals.append(label)
    return signals


def _build_risk_categories(extraction: ExtractionResult) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {
        "informational": [],
        "onboarding": [],
        "moderate": [],
        "blocker": [],
    }
    for risk in extraction.risks:
        if risk.endswith("_blocker") or risk in {"work_authorization_constraint"}:
            categories["blocker"].append(_format_risk_label(risk))
        elif risk in {"public_trust_possible_medium", "clearance_review"}:
            categories["onboarding"].append(_format_risk_label(risk))
        elif risk in {"clearance_required"}:
            categories["moderate"].append(_format_risk_label(risk))
        elif "travel" in risk:
            categories["moderate"].append(_format_risk_label(risk))
        else:
            categories["informational"].append(_format_risk_label(risk))
    return {key: value for key, value in categories.items() if value}


def _format_risk_label(risk: str) -> str:
    replacements = {
        "public_trust_possible_medium": "Public trust eligibility may be required",
        "clearance_review": "Clearance language should be clarified",
        "clearance_existing_blocker": "Existing clearance appears required",
        "clearance_required": "Security clearance requirement detected",
        "work_authorization_constraint": "Work authorization constraint detected",
        "travel_blocker": "Travel requirement appears substantial",
        "travel_requirement": "Travel requirement detected",
    }
    return replacements.get(risk, risk.replace("_", " "))


def _capability_overlap_count(extraction: ExtractionResult, user_profile: UserProfile) -> int:
    capability_text = " ".join(extraction.detected_capabilities)
    preferred_terms = _lowered_strings(
        user_profile.problem_spaces.primary
        + user_profile.problem_spaces.secondary
        + user_profile.constraints.nice_to_have
    )
    return len(_matching_terms(capability_text, preferred_terms))


def _recommendation_for(
    overall_score: int,
    confidence_score: int,
    blocking_concerns: list[str],
    evaluation_model: EvaluationModel,
) -> str:
    thresholds = evaluation_model.thresholds
    if blocking_concerns and overall_score < thresholds.consider:
        return "skip"
    if confidence_score < thresholds.minimum_confidence:
        return "needs_review"
    if overall_score >= thresholds.apply:
        return "apply"
    if overall_score >= thresholds.consider:
        return "consider"
    if overall_score >= thresholds.needs_review:
        return "needs_review"
    return "skip"


def _headline_for(extraction: ExtractionResult, recommendation: str, overall_score: int) -> str:
    role = extraction.role_title_normalized if extraction.role_title_normalized != "unknown" else "job posting"
    return f"{role}: {recommendation.replace('_', ' ')} ({overall_score}/100)"
