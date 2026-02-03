"""
Feedback Engine for Self-Improvement
Collects feedback on recommendations and builds user skill profiles
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from config import DATA_DIR

FEEDBACK_FILE = DATA_DIR / "feedback_history.json"
SKILL_PROFILE_FILE = DATA_DIR / "skill_profile.json"


class FeedbackEngine:
    def __init__(self):
        self.feedback_history = self._load_feedback_history()
        self.skill_profile = self._load_skill_profile()
    
    def _load_feedback_history(self) -> List[Dict[str, Any]]:
        """Load feedback history from disk"""
        if FEEDBACK_FILE.exists():
            with open(FEEDBACK_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _load_skill_profile(self) -> Dict[str, Any]:
        """Load skill profile from disk"""
        if SKILL_PROFILE_FILE.exists():
            with open(SKILL_PROFILE_FILE, 'r') as f:
                return json.load(f)
        return {
            "topic_strengths": {},  # {topic: success_rate}
            "topic_weaknesses": {},  # {topic: success_rate}
            "difficulty_comfort": {"easy": 0.0, "medium": 0.0, "hard": 0.0},
            "total_feedback_count": 0,
            "recommendation_quality_score": 0.0
        }
    
    def _save_feedback_history(self):
        """Save feedback history to disk"""
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(self.feedback_history, f, indent=2)
    
    def _save_skill_profile(self):
        """Save skill profile to disk"""
        with open(SKILL_PROFILE_FILE, 'w') as f:
            json.dump(self.skill_profile, f, indent=2)
    
    def record_recommendation_feedback(self, problem_name: str, helpful: bool, 
                                     difficulty_felt: str = None, 
                                     time_spent_minutes: int = None) -> None:
        """
        Record feedback on a recommendation
        
        Args:
            problem_name: Name of the problem
            helpful: Whether the recommendation was helpful (True/False)
            difficulty_felt: How difficult the user found it ('easy', 'medium', 'hard')
            time_spent_minutes: How long they spent on it
        """
        feedback_entry = {
            "problem_name": problem_name,
            "timestamp": datetime.now().isoformat(),
            "helpful": helpful,
            "difficulty_felt": difficulty_felt,
            "time_spent_minutes": time_spent_minutes
        }
        
        self.feedback_history.append(feedback_entry)
        self._save_feedback_history()
        
        # Update skill profile based on this feedback
        self._update_skill_profile(problem_name, helpful, difficulty_felt)
    
    def record_problem_completion(self, problem_name: str, solved: bool, 
                                 time_spent_minutes: int, topics: List[str]) -> None:
        """
        Record that user completed a problem attempt
        
        Args:
            problem_name: Name of the problem
            solved: Whether they successfully solved it
            time_spent_minutes: Time spent
            topics: Associated topics
        """
        completion_entry = {
            "problem_name": problem_name,
            "timestamp": datetime.now().isoformat(),
            "solved": solved,
            "time_spent_minutes": time_spent_minutes,
            "topics": topics
        }
        
        self.feedback_history.append(completion_entry)
        self._save_feedback_history()
        
        # Update skill profile
        for topic in topics:
            if topic not in self.skill_profile["topic_strengths"]:
                self.skill_profile["topic_strengths"][topic] = 0.0
                self.skill_profile["topic_weaknesses"][topic] = 0.0
            
            if solved:
                # Increase success rate for this topic
                current = self.skill_profile["topic_strengths"][topic]
                self.skill_profile["topic_strengths"][topic] = (current * 0.7 + 1.0 * 0.3)
                self.skill_profile["topic_weaknesses"][topic] = max(0, 
                    self.skill_profile["topic_weaknesses"][topic] * 0.9)
            else:
                # Increase weakness indicator for this topic
                current = self.skill_profile["topic_weaknesses"][topic]
                self.skill_profile["topic_weaknesses"][topic] = (current * 0.7 + 1.0 * 0.3)
        
        self._save_skill_profile()
    
    def _update_skill_profile(self, problem_name: str, helpful: bool, difficulty_felt: str):
        """Update skill profile based on feedback"""
        # Increment total feedback count
        self.skill_profile["total_feedback_count"] += 1
        
        # Update recommendation quality score (moving average)
        current_quality = self.skill_profile["recommendation_quality_score"]
        helpful_value = 1.0 if helpful else 0.0
        self.skill_profile["recommendation_quality_score"] = (
            current_quality * 0.8 + helpful_value * 0.2
        )
        
        # Update difficulty comfort levels
        if difficulty_felt:
            if difficulty_felt == "easy":
                self.skill_profile["difficulty_comfort"]["easy"] += 0.1
            elif difficulty_felt == "medium":
                self.skill_profile["difficulty_comfort"]["medium"] += 0.1
            elif difficulty_felt == "hard":
                self.skill_profile["difficulty_comfort"]["hard"] += 0.1
            
            # Normalize to max 1.0
            for key in self.skill_profile["difficulty_comfort"]:
                self.skill_profile["difficulty_comfort"][key] = min(
                    self.skill_profile["difficulty_comfort"][key], 1.0
                )
        
        self._save_skill_profile()
    
    def get_strength_areas(self) -> List[Tuple[str, float]]:
        """Get user's strongest topic areas"""
        sorted_strengths = sorted(
            self.skill_profile["topic_strengths"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [(topic, score) for topic, score in sorted_strengths if score > 0.5]
    
    def get_weakness_areas(self) -> List[Tuple[str, float]]:
        """Get user's areas needing improvement"""
        sorted_weaknesses = sorted(
            self.skill_profile["topic_weaknesses"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [(topic, score) for topic, score in sorted_weaknesses if score > 0.4]
    
    def get_recommendation_adjustments(self) -> Dict[str, float]:
        """
        Get adjustments to apply to recommendations based on user history
        
        Returns:
            Dict mapping topics to adjustment multipliers (>1 means boost, <1 means reduce)
        """
        adjustments = {}
        
        # Boost weak areas to help user improve
        for topic, weakness_score in self.get_weakness_areas():
            adjustments[topic] = 1.0 + (weakness_score * 0.3)  # Up to 30% boost
        
        # Slightly reduce strong areas (user likely already knows them)
        for topic, strength_score in self.get_strength_areas():
            adjustments[topic] = max(0.7, 1.0 - (strength_score * 0.2))  # Min 30% reduction
        
        return adjustments
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate insights about user's learning progress"""
        strengths = self.get_strength_areas()
        weaknesses = self.get_weakness_areas()
        
        total_feedback = self.skill_profile["total_feedback_count"]
        quality_score = self.skill_profile["recommendation_quality_score"]
        
        return {
            "total_recommendations_rated": total_feedback,
            "recommendation_helpfulness": f"{quality_score * 100:.0f}%",
            "strength_areas": strengths,
            "improvement_areas": weaknesses,
            "comfort_levels": self.skill_profile["difficulty_comfort"],
            "learning_velocity": "increasing" if quality_score > 0.7 else "steady" if quality_score > 0.5 else "building"
        }
    
    def should_adjust_difficulty(self) -> str:
        """Recommend difficulty adjustment based on performance"""
        comfort = self.skill_profile["difficulty_comfort"]
        
        if comfort.get("easy", 0) > 0.8 and comfort.get("medium", 0) < 0.5:
            return "medium"
        elif comfort.get("medium", 0) > 0.7 and comfort.get("hard", 0) < 0.4:
            return "hard"
        elif comfort.get("hard", 0) > 0.6:
            return "stick"  # Stick with hard problems
        elif comfort.get("easy", 0) < 0.3:
            return "easy"  # Struggling, go back to basics
        
        return "mixed"  # Mix all difficulties


if __name__ == "__main__":
    engine = FeedbackEngine()
    print("Feedback Engine initialized")
    print(f"Total feedback entries: {len(engine.feedback_history)}")
    insights = engine.get_learning_insights()
    print(f"Insights: {insights}")
