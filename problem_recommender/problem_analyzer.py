"""
Problem Analyzer Module
Scans Java files and extracts problem metadata
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from config import JAVA_PROBLEMS_DIR, PROBLEMS_DB_FILE


class ProblemAnalyzer:
    def __init__(self):
        self.problems = []
        
    def scan_problems(self) -> List[Dict[str, Any]]:
        """Scan all Java files and extract problem information"""
        self.problems = []
        
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_path = JAVA_PROBLEMS_DIR / difficulty
            if not difficulty_path.exists():
                continue
                
            for java_file in difficulty_path.glob("*.java"):
                problem_data = self._analyze_file(java_file, difficulty)
                if problem_data:
                    self.problems.append(problem_data)
        
        # Save to database
        self._save_problems_db()
        return self.problems
    
    def _analyze_file(self, file_path: Path, difficulty: str) -> Dict[str, Any]:
        """Analyze a single Java file and extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract problem name from filename
            name = file_path.stem.replace('_', ' ')
            
            # Extract topics/keywords from filename and content
            topics = self._extract_topics(name, content)
            
            # Extract comments/description
            description = self._extract_description(content)
            
            return {
                "name": name,
                "file_path": str(file_path),
                "difficulty": difficulty,
                "language": file_path.suffix.lstrip('.').lower(),
                "topics": topics,
                "description": description,
                "code_snippet": content[:500]  # First 500 chars for context
            }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _extract_topics(self, filename: str, content: str) -> List[str]:
        """Extract relevant topics from filename and code"""
        topics = []
        
        # Common programming topics
        topic_keywords = {
            "array": ["array", "list"],
            "string": ["string", "char"],
            "loop": ["loop", "for", "while", "iteration"],
            "recursion": ["recursion", "recursive"],
            "sorting": ["sort", "bubble", "quick", "merge"],
            "searching": ["search", "binary", "linear"],
            "data structures": ["stack", "queue", "tree", "graph", "linked", "hash"],
            "math": ["math", "arithmetic", "calculation"],
            "conditionals": ["if", "else", "switch", "condition"],
            "input/output": ["input", "output", "stdin", "stdout", "scanner"],
            "formatting": ["format", "printf", "currency", "date"],
            "oop": ["class", "object", "inheritance", "polymorphism"],
            "collections": ["collection", "map", "set", "arraylist"],
        }
        
        text = (filename + " " + content).lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _extract_description(self, content: str) -> str:
        """Extract problem description from comments"""
        # Look for multi-line comments
        comment_pattern = r'/\*\*(.*?)\*/'
        matches = re.findall(comment_pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Look for single-line comments at the beginning
        lines = content.split('\n')
        description_lines = []
        for line in lines[:20]:  # Check first 20 lines
            if line.strip().startswith('//'):
                description_lines.append(line.strip()[2:].strip())
            elif description_lines:
                break
        
        return ' '.join(description_lines) if description_lines else "No description available"
    
    def _save_problems_db(self):
        """Save problems to JSON database"""
        with open(PROBLEMS_DB_FILE, 'w') as f:
            json.dump(self.problems, f, indent=2)
    
    def load_problems(self) -> List[Dict[str, Any]]:
        """Load problems from database"""
        if PROBLEMS_DB_FILE.exists():
            with open(PROBLEMS_DB_FILE, 'r') as f:
                self.problems = json.load(f)
            for problem in self.problems:
                if "language" not in problem:
                    file_path = Path(problem.get("file_path", ""))
                    problem["language"] = file_path.suffix.lstrip('.').lower()
        else:
            # If no database exists, scan the problems
            self.scan_problems()
        return self.problems


if __name__ == "__main__":
    analyzer = ProblemAnalyzer()
    problems = analyzer.scan_problems()
    print(f"Found {len(problems)} problems")
    for p in problems:
        print(f"- {p['name']} ({p['difficulty']}): {', '.join(p['topics'])}")
