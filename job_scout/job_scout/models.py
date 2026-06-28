"""Domain models for Job Scout."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class JobPostingCreate:
    """Input payload for a new job posting."""

    raw_description: str
    source_type: str = "manual_text"
    source_system: str = "unknown"
    source_url: Optional[str] = None
    source_reference: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None


@dataclass
class JobPosting:
    """Persisted job posting record."""

    id: int
    source_type: str
    source_system: str
    source_url: Optional[str]
    source_reference: Optional[str]
    company: Optional[str]
    title: Optional[str]
    location: Optional[str]
    status: str
    raw_description: str
    created_at: datetime


@dataclass
class CompensationRange:
    """Structured compensation information extracted from a posting."""

    currency: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    interval: Optional[str] = None
    bands: list["CompensationBand"] = field(default_factory=list)


@dataclass
class CompensationBand:
    """A compensation band tied to a level or context."""

    level: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None


@dataclass
class EvidenceItem:
    """Evidence supporting an extracted field or score."""

    topic: str
    snippet: str
    source: str = "job_posting"
    is_inference: bool = False


@dataclass
class ExtractionResult:
    """Normalized job-posting structure used for scoring."""

    role_title_normalized: str = "unknown"
    role_summary: str = ""
    seniority: str = "unknown"
    employment_type: str = "unknown"
    location_text: str = ""
    work_mode: str = "unknown"
    semantic_shapes: dict[str, int] = field(default_factory=dict)
    detected_tools: list[str] = field(default_factory=list)
    detected_capabilities: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    required_experience: list[str] = field(default_factory=list)
    preferred_experience: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    compensation: CompensationRange = field(default_factory=CompensationRange)
    visa_or_clearance_requirements: list[str] = field(default_factory=list)
    domain_signals: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class ScoreDimension:
    """One rubric dimension and its supporting rationale."""

    name: str
    score: int
    weight: float
    rationale: str
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class EvaluationSummary:
    """Top-level evaluation summary for quick review."""

    headline: str
    recommendation: str
    overall_score: int
    confidence_score: int
    narrative: str = ""


@dataclass
class ScoringResult:
    """Detailed scoring breakdown for a job evaluation."""

    dimensions: list[ScoreDimension] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    blocking_concerns: list[str] = field(default_factory=list)
    review_flags: list[str] = field(default_factory=list)
    risk_categories: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class EvaluationProvenance:
    """Where and when an evaluation was produced."""

    source_system: str
    source_url: Optional[str]
    evaluated_at: datetime


@dataclass
class JobEvaluation:
    """Structured evaluation result for one job posting."""

    job_posting_id: int
    summary: EvaluationSummary
    extraction: ExtractionResult = field(default_factory=ExtractionResult)
    scoring: ScoringResult = field(default_factory=ScoringResult)
    provenance: Optional[EvaluationProvenance] = None
    contract_version: str = "v1"


@dataclass
class RiskRule:
    """A configurable risk rule used during extraction and scoring."""

    label: str
    patterns: list[str] = field(default_factory=list)


@dataclass
class RecommendationThresholds:
    """Thresholds for mapping evaluation scores to recommendations."""

    apply: int = 75
    consider: int = 55
    needs_review: int = 40
    minimum_confidence: int = 45


@dataclass
class EvaluationModel:
    """Tracked repository configuration for evaluation behavior."""

    model_version: str = "v1"
    skill_keywords: list[str] = field(default_factory=list)
    domain_keywords: list[str] = field(default_factory=list)
    authorization_patterns: list[str] = field(default_factory=list)
    preferred_skill_markers: list[str] = field(default_factory=list)
    work_mode_terms: dict[str, list[str]] = field(default_factory=dict)
    dimensions: dict[str, float] = field(default_factory=dict)
    thresholds: RecommendationThresholds = field(default_factory=RecommendationThresholds)
    risk_rules: list[RiskRule] = field(default_factory=list)


@dataclass
class CapabilityDefinition:
    """A capability, its aliases, and the tools that may express it."""

    name: str
    aliases: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class CapabilityModel:
    """Tracked repository capability ontology for higher-level reasoning."""

    model_version: str = "v1"
    capabilities: list[CapabilityDefinition] = field(default_factory=list)


@dataclass
class UserIdentity:
    """Stable identity summary for evaluation and artifact generation."""

    name: str = ""
    headline: str = ""
    summary: str = ""


@dataclass
class ValueProposition:
    """Primary and supporting value created by the candidate."""

    primary: str = ""
    supporting: list[str] = field(default_factory=list)


@dataclass
class ProblemSpaces:
    """Preferred and avoided problem spaces."""

    primary: list[str] = field(default_factory=list)
    secondary: list[str] = field(default_factory=list)
    adjacent: list[str] = field(default_factory=list)
    avoid_primary: list[str] = field(default_factory=list)


@dataclass
class TargetingPreferences:
    """Role targeting preferences for evaluation."""

    target_roles: list[str] = field(default_factory=list)
    acceptable_roles: list[str] = field(default_factory=list)
    role_seniority: list[str] = field(default_factory=list)


@dataclass
class SkillProfile:
    """Skills grouped by concern rather than flattened into one list."""

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    cloud: list[str] = field(default_factory=list)
    delivery: list[str] = field(default_factory=list)
    observability: list[str] = field(default_factory=list)
    security_compliance: list[str] = field(default_factory=list)


@dataclass
class ExperienceProfile:
    """Experience summary and notable outcomes."""

    years_total: int = 0
    leadership_years: int = 0
    management_years: int = 0
    highlights: list[str] = field(default_factory=list)


@dataclass
class LocationPreferences:
    """Location preferences and exclusions."""

    preferred: list[str] = field(default_factory=list)
    acceptable: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)


@dataclass
class CompensationPreferences:
    """Compensation expectations."""

    currency: str = "USD"
    minimum_base: int = 0
    target_base: int = 0
    hourly_target: int = 0


@dataclass
class WorkPreferences:
    """Work arrangement and compensation preferences."""

    work_mode: list[str] = field(default_factory=list)
    acceptable_work_mode: list[str] = field(default_factory=list)
    locations: LocationPreferences = field(default_factory=LocationPreferences)
    employment_types: list[str] = field(default_factory=list)
    compensation: CompensationPreferences = field(default_factory=CompensationPreferences)


@dataclass
class CandidateConstraints:
    """Must-haves, nice-to-haves, and deal-breakers."""

    must_have: list[str] = field(default_factory=list)
    nice_to_have: list[str] = field(default_factory=list)
    deal_breakers: list[str] = field(default_factory=list)
    work_authorization: str = ""
    requires_sponsorship: bool = False
    clearance_eligible: bool = False


@dataclass
class EvaluationPreferences:
    """How the user wants fit to be judged."""

    weights: dict[str, float] = field(default_factory=dict)
    prioritize: list[str] = field(default_factory=list)
    downweight: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class IdentityGuardrails:
    """Things the system should never distort or optimize away."""

    never_optimize_for: list[str] = field(default_factory=list)
    always_preserve: list[str] = field(default_factory=list)


@dataclass
class ArtifactPreferences:
    """Output preferences for generated job-application artifacts."""

    resume_style: str = ""
    cover_letter_style: str = ""
    naming_convention: str = ""
    generate_pdf: bool = False
    validate_formatting: bool = False


@dataclass
class UserProfile:
    """Local user profile used to personalize job evaluation."""

    profile_version: str = "v1"
    identity: UserIdentity = field(default_factory=UserIdentity)
    value_proposition: ValueProposition = field(default_factory=ValueProposition)
    problem_spaces: ProblemSpaces = field(default_factory=ProblemSpaces)
    targeting: TargetingPreferences = field(default_factory=TargetingPreferences)
    skills: SkillProfile = field(default_factory=SkillProfile)
    experience: ExperienceProfile = field(default_factory=ExperienceProfile)
    preferences: WorkPreferences = field(default_factory=WorkPreferences)
    constraints: CandidateConstraints = field(default_factory=CandidateConstraints)
    evaluation_preferences: EvaluationPreferences = field(default_factory=EvaluationPreferences)
    identity_guardrails: IdentityGuardrails = field(default_factory=IdentityGuardrails)
    artifact_preferences: ArtifactPreferences = field(default_factory=ArtifactPreferences)
