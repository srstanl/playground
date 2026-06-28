"""Loader for the local Job Scout user profile."""

from __future__ import annotations

import json
from pathlib import Path

from job_scout.models import (
    ArtifactPreferences,
    CandidateConstraints,
    CompensationPreferences,
    EvaluationPreferences,
    ExperienceProfile,
    IdentityGuardrails,
    LocationPreferences,
    ProblemSpaces,
    SkillProfile,
    TargetingPreferences,
    UserIdentity,
    UserProfile,
    ValueProposition,
    WorkPreferences,
)


def load_user_profile(path: Path) -> UserProfile:
    """Load a user profile from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))

    return UserProfile(
        profile_version=payload.get("profile_version", "v1"),
        identity=_load_identity(payload.get("identity", {})),
        value_proposition=_load_value_proposition(payload.get("value_proposition", {})),
        problem_spaces=_load_problem_spaces(payload.get("problem_spaces", {})),
        targeting=_load_targeting(payload.get("targeting", {})),
        skills=_load_skills(payload.get("skills", {})),
        experience=_load_experience(payload.get("experience", {})),
        preferences=_load_preferences(payload.get("preferences", {})),
        constraints=_load_constraints(payload.get("constraints", {})),
        evaluation_preferences=_load_evaluation_preferences(
            payload.get("evaluation_preferences", {})
        ),
        identity_guardrails=_load_identity_guardrails(
            payload.get("identity_guardrails", {})
        ),
        artifact_preferences=_load_artifact_preferences(
            payload.get("artifact_preferences", {})
        ),
    )


def _load_identity(payload: dict[str, object]) -> UserIdentity:
    return UserIdentity(
        name=str(payload.get("name", "")),
        headline=str(payload.get("headline", "")),
        summary=str(payload.get("summary", "")),
    )


def _load_value_proposition(payload: dict[str, object]) -> ValueProposition:
    return ValueProposition(
        primary=str(payload.get("primary", "")),
        supporting=_string_list(payload.get("supporting")),
    )


def _load_problem_spaces(payload: dict[str, object]) -> ProblemSpaces:
    return ProblemSpaces(
        primary=_string_list(payload.get("primary")),
        secondary=_string_list(payload.get("secondary")),
        adjacent=_string_list(payload.get("adjacent")),
        avoid_primary=_string_list(payload.get("avoid_primary")),
    )


def _load_targeting(payload: dict[str, object]) -> TargetingPreferences:
    return TargetingPreferences(
        target_roles=_string_list(payload.get("target_roles")),
        acceptable_roles=_string_list(payload.get("acceptable_roles")),
        role_seniority=_string_list(payload.get("role_seniority")),
    )


def _load_skills(payload: dict[str, object]) -> SkillProfile:
    return SkillProfile(
        languages=_string_list(payload.get("languages")),
        frameworks=_string_list(payload.get("frameworks")),
        cloud=_string_list(payload.get("cloud")),
        delivery=_string_list(payload.get("delivery")),
        observability=_string_list(payload.get("observability")),
        security_compliance=_string_list(payload.get("security_compliance")),
    )


def _load_experience(payload: dict[str, object]) -> ExperienceProfile:
    return ExperienceProfile(
        years_total=_int_value(payload.get("years_total")),
        leadership_years=_int_value(payload.get("leadership_years")),
        management_years=_int_value(payload.get("management_years")),
        highlights=_string_list(payload.get("highlights")),
    )


def _load_preferences(payload: dict[str, object]) -> WorkPreferences:
    return WorkPreferences(
        work_mode=_string_list(payload.get("work_mode")),
        acceptable_work_mode=_string_list(payload.get("acceptable_work_mode")),
        locations=_load_locations(_dict_value(payload.get("locations"))),
        employment_types=_string_list(payload.get("employment_types")),
        compensation=_load_compensation(_dict_value(payload.get("compensation"))),
    )


def _load_locations(payload: dict[str, object]) -> LocationPreferences:
    return LocationPreferences(
        preferred=_string_list(payload.get("preferred")),
        acceptable=_string_list(payload.get("acceptable")),
        avoid=_string_list(payload.get("avoid")),
    )


def _load_compensation(payload: dict[str, object]) -> CompensationPreferences:
    return CompensationPreferences(
        currency=str(payload.get("currency", "USD")),
        minimum_base=_int_value(payload.get("minimum_base")),
        target_base=_int_value(payload.get("target_base")),
        hourly_target=_int_value(payload.get("hourly_target")),
    )


def _load_constraints(payload: dict[str, object]) -> CandidateConstraints:
    return CandidateConstraints(
        must_have=_string_list(payload.get("must_have")),
        nice_to_have=_string_list(payload.get("nice_to_have")),
        deal_breakers=_string_list(payload.get("deal_breakers")),
        work_authorization=str(payload.get("work_authorization", "")),
        requires_sponsorship=bool(payload.get("requires_sponsorship", False)),
        clearance_eligible=bool(payload.get("clearance_eligible", False)),
    )


def _load_evaluation_preferences(payload: dict[str, object]) -> EvaluationPreferences:
    weights_payload = _dict_value(payload.get("weights"))
    weights = {
        str(key): float(value)
        for key, value in weights_payload.items()
        if isinstance(value, (int, float))
    }
    return EvaluationPreferences(
        weights=weights,
        prioritize=_string_list(payload.get("prioritize")),
        downweight=_string_list(payload.get("downweight")),
        notes=str(payload.get("notes", "")),
    )


def _load_identity_guardrails(payload: dict[str, object]) -> IdentityGuardrails:
    return IdentityGuardrails(
        never_optimize_for=_string_list(payload.get("never_optimize_for")),
        always_preserve=_string_list(payload.get("always_preserve")),
    )


def _load_artifact_preferences(payload: dict[str, object]) -> ArtifactPreferences:
    return ArtifactPreferences(
        resume_style=str(payload.get("resume_style", "")),
        cover_letter_style=str(payload.get("cover_letter_style", "")),
        naming_convention=str(payload.get("naming_convention", "")),
        generate_pdf=bool(payload.get("generate_pdf", False)),
        validate_formatting=bool(payload.get("validate_formatting", False)),
    )


def _dict_value(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    return 0
