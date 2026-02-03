"""
Rules Engine for Problem Recommendation
Provides configurable, role- and language-aware scoring with feedback integration.
"""
import json
import re
from typing import Dict, Any, List, Tuple, Optional
from config import RULES_PROFILE_FILE


class RulesEngine:
    DEFAULT_PROFILE: Dict[str, Any] = {
        "roles": {
            "staff_swe": {
                "aliases": ["staff", "staff swe", "staff software engineer"],
                "difficulty_weights": {"easy": 0.7, "medium": 1.0, "hard": 1.3},
                "topic_weights": {
                    "data structures": 1.2,
                    "searching": 1.1,
                    "sorting": 1.1,
                    "recursion": 1.1,
                    "collections": 1.0,
                    "oop": 1.0,
                },
            },
            "sre": {
                "aliases": ["sre", "site reliability", "site reliability engineer"],
                "difficulty_weights": {"easy": 0.8, "medium": 1.1, "hard": 1.2},
                "topic_weights": {
                    "data structures": 1.1,
                    "searching": 1.0,
                    "sorting": 1.0,
                    "recursion": 1.0,
                    "input/output": 1.1,
                    "conditionals": 1.0,
                    "math": 1.0,
                },
            },
        },
        "languages": {
            "csharp": ["c#", "c sharp", "csharp"],
            "javascript": ["javascript", "js", "node", "nodejs"],
        },
        "default_roles": [],
        "default_languages": [],
        "language_match_bonus": 0.08,
        "language_mismatch_penalty": -0.03,
        "role_topic_score_normalizer": 3.0,
        "keyword_weight": 0.6,
        "role_weight": 0.4,
    }

    def __init__(self, problems: List[Dict[str, Any]], feedback_engine: Optional[Any] = None):
        self.problems = problems
        self.profile = self._load_profile()
        self.feedback_engine = feedback_engine
        self.feedback_adjustments = feedback_engine.get_recommendation_adjustments() if feedback_engine else {}

    def _load_profile(self) -> Dict[str, Any]:
        """Load a user profile from disk, overriding defaults if present."""
        profile = json.loads(json.dumps(self.DEFAULT_PROFILE))
        if RULES_PROFILE_FILE.exists():
            try:
                with open(RULES_PROFILE_FILE, "r") as f:
                    user_profile = json.load(f)
                self._deep_merge(profile, user_profile)
            except Exception:
                pass
        return profile

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge override into base (in-place)."""
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _extract_preferences(self, query: str) -> Tuple[List[str], List[str]]:
        """Extract role and language preferences from query text."""
        query_lower = query.lower()
        roles = []
        for role, config in self.profile["roles"].items():
            aliases = config.get("aliases", [])
            if any(alias in query_lower for alias in aliases):
                roles.append(role)

        languages = []
        for lang, aliases in self.profile["languages"].items():
            if any(alias in query_lower for alias in aliases):
                languages.append(lang)

        if not roles:
            roles = list(self.profile.get("default_roles", []))
        if not languages:
            languages = list(self.profile.get("default_languages", []))

        return roles, languages

    def _keyword_score(self, query: str, problem: Dict[str, Any]) -> float:
        """Compute a simple keyword overlap score in [0, 1]."""
        query_words = re.findall(r"[a-z0-9#]+", query.lower())
        if not query_words:
            return 0.0

        text = " ".join([
            problem.get("name", ""),
            " ".join(problem.get("topics", [])),
            problem.get("description", ""),
        ]).lower()

        matches = sum(1 for word in query_words if word in text)
        return min(matches / max(len(query_words), 1), 1.0)

    def _role_topic_score(self, roles: List[str], problem: Dict[str, Any]) -> float:
        """Score how well problem topics match role-specific priorities."""
        topics = problem.get("topics", [])
        score = 0.0
        for role in roles:
            role_cfg = self.profile["roles"].get(role, {})
            topic_weights = role_cfg.get("topic_weights", {})
            for topic in topics:
                base_weight = topic_weights.get(topic, 0.0)
                # Apply feedback adjustments to boost weak areas
                feedback_multiplier = self.feedback_adjustments.get(topic, 1.0)
                score += base_weight * feedback_multiplier

        normalizer = self.profile.get("role_topic_score_normalizer", 3.0)
        return min(score / max(normalizer, 1.0), 1.0)

    def _difficulty_weight(self, roles: List[str], difficulty: str) -> float:
        """Compute a difficulty multiplier based on role preferences."""
        if not roles:
            return 1.0

        total = 0.0
        for role in roles:
            role_cfg = self.profile["roles"].get(role, {})
            weights = role_cfg.get("difficulty_weights", {})
            total += weights.get(difficulty, 1.0)
        return total / max(len(roles), 1)

    def _language_adjustment(self, languages: List[str], problem: Dict[str, Any]) -> Tuple[float, str]:
        """Apply a small adjustment based on language preferences."""
        if not languages:
            return 0.0, ""

        problem_language = (problem.get("language") or "").lower()
        if problem_language and problem_language in languages:
            bonus = self.profile.get("language_match_bonus", 0.0)
            return bonus, f"Language match: {problem_language}"

        penalty = self.profile.get("language_mismatch_penalty", 0.0)
        if penalty < 0:
            return penalty, "Language mismatch; problem is transferable"
        return 0.0, ""

    def _build_reason(self, roles: List[str], languages: List[str], problem: Dict[str, Any], role_score: float, keyword_score: float, lang_note: str) -> str:
        reasons = []
        if roles:
            roles_label = ", ".join(roles)
            reasons.append(f"Role focus: {roles_label}")
        if role_score > 0:
            reasons.append("Aligns with role-priority topics")
        if keyword_score > 0:
            reasons.append("Keyword overlap with your query")
        if lang_note:
            reasons.append(lang_note)
        return "; ".join(reasons) if reasons else "Rules-based match"

    def recommend(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Recommend problems using rule-based scoring."""
        roles, languages = self._extract_preferences(query)

        keyword_weight = self.profile.get("keyword_weight", 0.6)
        role_weight = self.profile.get("role_weight", 0.4)

        scored = []
        for problem in self.problems:
            keyword_score = self._keyword_score(query, problem)
            role_score = self._role_topic_score(roles, problem)
            difficulty_weight = self._difficulty_weight(roles, problem.get("difficulty", ""))
            lang_adjust, lang_note = self._language_adjustment(languages, problem)

            base_score = (keyword_weight * keyword_score) + (role_weight * role_score)
            score = (base_score * difficulty_weight) + lang_adjust
            score = max(min(score, 1.0), 0.0)

            scored.append({
                **problem,
                "relevance_score": score,
                "recommendation_reason": self._build_reason(
                    roles, languages, problem, role_score, keyword_score, lang_note
                ),
            })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:max_results]

    def apply_rules(self, recommendations: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Re-score existing recommendations using rules and re-rank them."""
        roles, languages = self._extract_preferences(query)

        keyword_weight = self.profile.get("keyword_weight", 0.6)
        role_weight = self.profile.get("role_weight", 0.4)

        rescored = []
        for rec in recommendations:
            keyword_score = self._keyword_score(query, rec)
            role_score = self._role_topic_score(roles, rec)
            difficulty_weight = self._difficulty_weight(roles, rec.get("difficulty", ""))
            lang_adjust, lang_note = self._language_adjustment(languages, rec)

            base_score = (keyword_weight * keyword_score) + (role_weight * role_score)
            rules_score = (base_score * difficulty_weight) + lang_adjust
            rules_score = max(min(rules_score, 1.0), 0.0)

            rec = {
                **rec,
                "rules_score": rules_score,
                "recommendation_reason": rec.get("recommendation_reason") or self._build_reason(
                    roles, languages, rec, role_score, keyword_score, lang_note
                ),
            }
            rescored.append(rec)

        rescored.sort(key=lambda x: x.get("rules_score", 0.0), reverse=True)
        return rescored
