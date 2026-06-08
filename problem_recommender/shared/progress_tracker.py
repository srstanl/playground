"""
Progress Tracker Module
Tracks user attempts, completions, and performance
"""
import json
from datetime import datetime
from typing import Dict, Any
from shared.config import PROGRESS_FILE


class ProgressTracker:
    def __init__(self):
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file"""
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_progress(self):
        """Save progress to file"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def mark_attempted(self, problem_name: str):
        """Mark a problem as attempted"""
        if problem_name not in self.progress:
            self.progress[problem_name] = {
                "attempts": 0,
                "completed": False,
                "first_attempt": datetime.now().isoformat(),
                "last_attempt": None,
                "completion_date": None
            }
        
        self.progress[problem_name]["attempts"] += 1
        self.progress[problem_name]["last_attempt"] = datetime.now().isoformat()
        self._save_progress()
    
    def mark_completed(self, problem_name: str):
        """Mark a problem as completed"""
        if problem_name not in self.progress:
            self.mark_attempted(problem_name)
        
        self.progress[problem_name]["completed"] = True
        self.progress[problem_name]["completion_date"] = datetime.now().isoformat()
        self._save_progress()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall progress statistics"""
        total_problems = len(self.progress)
        completed = sum(1 for p in self.progress.values() if p.get("completed"))
        in_progress = sum(1 for p in self.progress.values() if p.get("attempts", 0) > 0 and not p.get("completed"))
        
        return {
            "total_attempted": total_problems,
            "completed": completed,
            "in_progress": in_progress,
            "completion_rate": (completed / total_problems * 100) if total_problems > 0 else 0
        }
    
    def get_problem_status(self, problem_name: str) -> Dict[str, Any]:
        """Get status of a specific problem"""
        return self.progress.get(problem_name, {
            "attempts": 0,
            "completed": False,
            "first_attempt": None,
            "last_attempt": None,
            "completion_date": None
        })
    
    def get_completed_problems(self) -> list:
        """Get list of completed problem names"""
        return [name for name, data in self.progress.items() if data.get("completed")]
    
    def get_in_progress_problems(self) -> list:
        """Get list of problems in progress"""
        return [name for name, data in self.progress.items() 
                if data.get("attempts", 0) > 0 and not data.get("completed")]


if __name__ == "__main__":
    tracker = ProgressTracker()
    stats = tracker.get_stats()
    print(f"Progress Stats: {stats}")
