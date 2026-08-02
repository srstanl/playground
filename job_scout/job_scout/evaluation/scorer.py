"""Profile-aware evaluation scoring."""

from __future__ import annotations

from job_scout.models import (
    CompensationRange,
    EvaluationModel,
    EvidenceItem,
    ExtractionResult,
    ScoreDimension,
    ScoringResult,
    UserProfile,
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
        _engineering_persona_alignment_dimension(extraction, evaluation_model, user_profile),
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
        _score_from_match_count(
            len(matched) + min(capability_bonus, 2) + min(semantic_bonus, 2),
            strong_threshold=6,
            medium_threshold=3,
        ),
    )
    rationale = (
        f"Posting aligns with {len(matched)} preferred problem-shape signals and {len(extraction.detected_capabilities)} capability signals."
        if matched
        else "Posting does not strongly signal the preferred problem shape."
    )
    evidence = [
        EvidenceItem(topic="problem_shape", snippet=term, is_inference=True)
        for term in matched[:2]
    ]
    evidence.extend(
        EvidenceItem(topic="capability", snippet=capability, is_inference=True)
        for capability in extraction.detected_capabilities[:2]
    )
    return ScoreDimension(
        name="problem_shape_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "problem_shape_alignment", 0.30),
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
        score = (
            5
            if any(role in matched_roles for role in _lowered_strings(user_profile.targeting.target_roles))
            else 4
        )
        rationale = f"Posting scope matches preferred roles: {', '.join(matched_roles[:2])}."
    else:
        score = 3
        rationale = "Posting scope is not clearly aligned or misaligned."
    evidence = [
        EvidenceItem(topic="role_scope", snippet=item, is_inference=True)
        for item in (matched_roles or matched_avoid)[:3]
    ]
    return ScoreDimension(
        name="role_scope_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "role_scope_alignment", 0.15),
        rationale=rationale,
        evidence=evidence,
    )


def _engineering_persona_alignment_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    persona = extraction.engineering_persona
    preferred = {value.lower() for value in user_profile.targeting.preferred_personas}
    acceptable = {value.lower() for value in user_profile.targeting.acceptable_personas}
    avoided = {value.lower() for value in user_profile.targeting.avoid_personas}

    if persona in avoided:
        score = 1
        rationale = f"Role creates value mainly through an avoided engineering persona: {persona}."
    elif persona in preferred:
        score = 5
        rationale = f"Role creates value through a preferred engineering persona: {persona}."
    elif persona in acceptable:
        score = 4
        rationale = f"Role creates value through an acceptable adjacent engineering persona: {persona}."
    elif persona == "unknown":
        score = 3
        rationale = "Posting does not clearly signal where the team expects engineering value to be created."
    else:
        score = 2
        rationale = f"Role persona {persona} is outside the preferred engineering value lanes."

    evidence = [item for item in extraction.evidence if item.topic == "engineering_persona"][:2]
    if not evidence and persona != "unknown":
        evidence = [EvidenceItem(topic="engineering_persona", snippet=persona, is_inference=True)]
    return ScoreDimension(
        name="engineering_persona_alignment",
        score=score,
        weight=_dimension_weight(evaluation_model, "engineering_persona_alignment", 0.10),
        rationale=rationale,
        evidence=evidence,
    )


def _tool_adjacency_dimension(
    extraction: ExtractionResult,
    evaluation_model: EvaluationModel,
    user_profile: UserProfile,
) -> ScoreDimension:
    extracted_skills = {
        skill.lower() for skill in extraction.required_skills + extraction.preferred_skills
    }
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
    score = _score_from_match_count(
        len(matched) + capability_overlap,
        strong_threshold=6,
        medium_threshold=3,
    )
    rationale = (
        f"Posting shares {len(matched)} tool adjacencies and {capability_overlap} capability adjacencies with the profile."
        if matched
        else "Posting shows little direct tool adjacency, but capability adjacency is preferred over exact tooling."
    )
    evidence = [
        EvidenceItem(topic="tool_adjacency", snippet=skill, is_inference=True)
        for skill in matched[:2]
    ]
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
    evidence = [
        EvidenceItem(topic="environment_alignment", snippet=term, is_inference=True)
        for term in matched[:2]
    ]
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
        compensation_floor = _relevant_compensation_floor(
            extraction.compensation,
            extraction.seniority,
        )
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
        score = max(
            1,
            min(5, 4 + (1 if must_haves else 0) - moderate_count - min(onboarding_count, 1)),
        )
        rationale = (
            "Few blocking constraints detected and at least one must-have signal is present."
            if must_haves and raw_risk_count == 0
            else "Risk is low, with only informational or onboarding friction."
            if moderate_count == 0 and blocker_count == 0
            else f"Detected {moderate_count} moderate and {blocker_count} blocker-level risks."
        )
    evidence = [
        EvidenceItem(topic="risk_alignment", snippet=value, is_inference=True)
        for value in (blockers or extraction.risks or must_haves)[:3]
    ]
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
    evidence = [
        EvidenceItem(topic="identity_drift", snippet=value, is_inference=True)
        for value in (preserved or drifted)[:3]
    ]
    return ScoreDimension(
        name="identity_drift",
        score=score,
        weight=_dimension_weight(evaluation_model, "identity_drift", 0.05),
        rationale=rationale,
        evidence=evidence,
    )


def compute_overall_score(dimensions: list[ScoreDimension]) -> int:
    total = sum((dimension.score / 5.0) * dimension.weight for dimension in dimensions)
    return round(total * 100)


def compute_confidence_score(extraction: ExtractionResult, dimensions: list[ScoreDimension]) -> int:
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
            extraction.engineering_persona.lower(),
            " ".join(
                f"{key} {value}" for key, value in extraction.engineering_persona_scores.items()
            ).lower(),
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
