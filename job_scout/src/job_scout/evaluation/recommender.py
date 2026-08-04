"""Recommendation and narrative assembly."""

from __future__ import annotations

from job_scout.domain.models import (
    EvaluationModel,
    ExtractionResult,
    ScoreDimension,
    ScoringResult,
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


def recommendation_for(
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


def headline_for(extraction: ExtractionResult, recommendation: str, overall_score: int) -> str:
    role = extraction.role_title_normalized if extraction.role_title_normalized != "unknown" else "job posting"
    return f"{role}: {recommendation.replace('_', ' ')} ({overall_score}/100)"


def build_narrative(
    extraction: ExtractionResult,
    scoring: ScoringResult,
    recommendation: str,
) -> str:
    top_shapes = [
        name.replace("_", " ")
        for name, score in sorted(
            extraction.semantic_shapes.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        if score >= 4
    ][:3]
    top_dimensions = {dimension.name: dimension for dimension in scoring.dimensions}
    fit_bits: list[str] = []
    if top_shapes:
        fit_bits.append(f"it is shaped around {', '.join(top_shapes)}")
    if extraction.engineering_persona != "unknown" and top_dimensions.get(
        "engineering_persona_alignment"
    ):
        persona_text = extraction.engineering_persona.replace("_", " ")
        if top_dimensions["engineering_persona_alignment"].score >= 4:
            fit_bits.append(f"the team appears to create value through {persona_text}")
        elif top_dimensions["engineering_persona_alignment"].score <= 2:
            fit_bits.append(f"the role leans toward {persona_text}, which may be a poor persona match")
    if top_dimensions.get("identity_drift") and top_dimensions["identity_drift"].score >= 4:
        fit_bits.append("it stays close to your platform and enablement identity")
    if top_dimensions.get("environment_alignment") and top_dimensions["environment_alignment"].score >= 4:
        fit_bits.append(
            "the operating environment looks consistent with your preferred enterprise and regulated work"
        )
    fit_text = (
        "; ".join(fit_bits)
        if fit_bits
        else "the role shows some adjacency to your preferred work, but the shape is not definitive"
    )

    concern_bits = scoring.blocking_concerns[:2] + scoring.review_flags[:2]
    if not concern_bits and scoring.gaps:
        concern_bits = scoring.gaps[:2]
    concern_text = (
        "; ".join(concern_bits)
        if concern_bits
        else "no major structural concerns stand out from the posting"
    )
    recommendation_map = {
        "apply": "applying",
        "consider": "considering",
        "needs_review": "reviewing further",
        "skip": "skipping",
    }
    recommendation_text = recommendation_map.get(
        recommendation,
        recommendation.replace("_", " "),
    )
    return (
        f"This role is worth {recommendation_text} because {fit_text}. "
        f"The main follow-up is {concern_text}."
    )
