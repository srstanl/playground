"""
Problem Analyzer Module
Scans Java files and extracts problem metadata
"""
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

        for java_file in sorted(JAVA_PROBLEMS_DIR.glob('*.java')):
            if java_file.name.endswith('-test.java'):
                continue

            difficulty = self._infer_difficulty(java_file)
            problem_data = self._analyze_file(java_file, difficulty)
            if problem_data:
                self.problems.append(problem_data)

        self._save_problems_db()
        return self.problems

    def _infer_difficulty(self, file_path: Path) -> str:
        name = file_path.stem.lower()
        for difficulty in ['easy', 'medium', 'hard']:
            if f'-{difficulty}' in name or name.endswith(difficulty):
                return difficulty
        return 'unknown'

    def _analyze_file(self, file_path: Path, difficulty: str) -> Dict[str, Any]:
        """Analyze a single Java file and extract metadata"""
        try:
            content = file_path.read_text(encoding='utf-8')

            name = file_path.stem.replace('_', ' ')
            topics = self._extract_topics(name, content)
            description = self._extract_description(content)

            return {
                'name': name,
                'file_path': str(file_path),
                'difficulty': difficulty,
                'language': file_path.suffix.lstrip('.').lower(),
                'topics': topics,
                'description': description,
                'code_snippet': content[:500]
            }
        except Exception as exc:
            print(f'Error analyzing {file_path}: {exc}')
            return None

    def _extract_topics(self, filename: str, content: str) -> List[str]:
        """Extract relevant topics from filename and code"""
        topics = []

        topic_keywords = {
            'array': ['array', 'list'],
            'string': ['string', 'char'],
            'loop': ['loop', 'for', 'while', 'iteration'],
            'recursion': ['recursion', 'recursive'],
            'sorting': ['sort', 'bubble', 'quick', 'merge'],
            'searching': ['search', 'binary', 'linear'],
            'data structures': ['stack', 'queue', 'tree', 'graph', 'linked', 'hash'],
            'math': ['math', 'arithmetic', 'calculation'],
            'conditionals': ['if', 'else', 'switch', 'condition'],
            'input/output': ['input', 'output', 'stdin', 'stdout', 'scanner'],
            'formatting': ['format', 'printf', 'currency', 'date'],
            'oop': ['class', 'object', 'inheritance', 'polymorphism'],
            'collections': ['collection', 'map', 'set', 'arraylist'],
        }

        text = (filename + ' ' + content).lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['general']

    def _extract_description(self, content: str) -> str:
        """Extract problem description from comments"""
        comment_pattern = r'/\*\*(.*?)\*/'
        matches = re.findall(comment_pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()

        lines = content.split('\n')
        description_lines = []
        for line in lines[:20]:
            if line.strip().startswith('//'):
                description_lines.append(line.strip()[2:].strip())
            elif description_lines:
                break

        return ' '.join(description_lines) if description_lines else 'No description available'

    def _save_problems_db(self):
        """Save problems to JSON database"""
        PROBLEMS_DB_FILE.write_text(json.dumps(self.problems, indent=2))

    def load_problems(self) -> List[Dict[str, Any]]:
        """Load problems from database"""
        if PROBLEMS_DB_FILE.exists():
            self.problems = json.loads(PROBLEMS_DB_FILE.read_text())
            for problem in self.problems:
                if 'language' not in problem:
                    file_path = Path(problem.get('file_path', ''))
                    problem['language'] = file_path.suffix.lstrip('.').lower()
        else:
            self.scan_problems()
        return self.problems


if __name__ == '__main__':
    analyzer = ProblemAnalyzer()
    problems = analyzer.scan_problems()
    print(f'Found {len(problems)} problems')
    for problem in problems:
        print(f"- {problem['name']} ({problem['difficulty']}): {', '.join(problem['topics'])}")
