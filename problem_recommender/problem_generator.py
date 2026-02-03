"""
Problem Generator Engine
Generates coding problems dynamically based on user queries
Supports Java, C#, JavaScript, and Python
With role-aware problem generation (Junior/Mid/Senior/Staff/Principal)
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from config import GITHUB_TOKEN, MODEL_ENDPOINT, MODEL_NAME, JAVA_PROBLEMS_DIR


class ProblemGenerator:
    def __init__(self):
        self.generated_problems_dir = JAVA_PROBLEMS_DIR.parent / "generated_problems"
        self.generated_problems_dir.mkdir(exist_ok=True)
        
        # Initialize AI client - try OpenAI first, then GitHub Models
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            # Use OpenAI API directly
            self.client = OpenAI(api_key=openai_key)
        elif GITHUB_TOKEN:
            # Use GitHub Models (free tier)
            self.client = OpenAI(
                base_url=MODEL_ENDPOINT,
                api_key=GITHUB_TOKEN
            )
        else:
            self.client = None
        
        # Role definitions with expected difficulty and focus areas
        self.role_definitions = {
            "junior": {
                "alias": ["entry", "entry-level", "junior", "jr", "graduate"],
                "default_difficulty": "easy",
                "focus": "fundamentals, basic algorithms, simple data structures",
                "context": "Entry-level position, focus on understanding core concepts"
            },
            "mid": {
                "alias": ["mid", "mid-level", "intermediate", "senior-engineer"],
                "default_difficulty": "medium",
                "focus": "design patterns, optimization, complex data structures",
                "context": "Mid-level engineer, expected to handle complexity and make design decisions"
            },
            "senior": {
                "alias": ["senior", "sr", "staff", "staff-level", "staff swe", "staff-swe"],
                "default_difficulty": "hard",
                "focus": "system design, optimization, edge cases, scalability",
                "context": "Staff/Senior engineer, expected deep expertise, optimization, and system-level thinking"
            },
            "principal": {
                "alias": ["principal", "principal engineer", "distinguished"],
                "default_difficulty": "hard",
                "focus": "advanced system design, novel approaches, technical leadership",
                "context": "Principal engineer, expected to solve complex architectural problems with nuance"
            }
        }
        
        # Language file extensions
        self.language_extensions = {
            "java": ".java",
            "csharp": ".cs",
            "c#": ".cs",
            "javascript": ".js",
            "js": ".js",
            "python": ".py"
        }
        
        # Language class templates
        self.language_templates = {
            "java": """public class {class_name} {{
    // TODO: Implement solution
    public static void main(String[] args) {{
        // Test cases
        {test_code}
    }}
}}""",
            "csharp": """public class {class_name} {{
    // TODO: Implement solution
    public static void Main() {{
        // Test cases
        {test_code}
    }}
}}""",
            "javascript": """// TODO: Implement solution
function {function_name}({params}) {{
    // Your code here
}}

// Test cases
{test_code}""",
            "python": """# TODO: Implement solution
def {function_name}({params}):
    pass

# Test cases
{test_code}"""
        }
    
    def detect_role(self, query: str) -> Tuple[str, str]:
        """
        Detect role from query string
        
        Args:
            query: User's problem description that may contain role indicator
        
        Returns:
            Tuple of (role, cleaned_query) where role is junior/mid/senior/principal
            and cleaned_query is the description without role keywords
        """
        query_lower = query.lower()
        detected_role = "mid"  # Default role
        
        # Check for role mentions
        for role, config in self.role_definitions.items():
            for alias in config["alias"]:
                if alias in query_lower:
                    detected_role = role
                    # Remove role keywords from query
                    for keyword in config["alias"]:
                        query = re.sub(rf'\b{keyword}\b', '', query, flags=re.IGNORECASE)
                    query = query.strip()
                    return detected_role, query
        
        return detected_role, query
    
    def generate_problem(self, query: str, language: str = "java", 
                        difficulty: Optional[str] = None,
                        role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a coding problem based on user query with role context
        
        Args:
            query: Description of what problem to generate (may include role)
            language: Programming language (java, csharp, javascript, python)
            difficulty: Problem difficulty (easy, medium, hard) - auto-detected from role if None
            role: Target role (junior, mid, senior, principal) - auto-detected from query if None
        
        Returns:
            Dictionary with problem details or None if generation fails
        """
        if not self.client:
            print("[red]Error: AI token not configured. Cannot generate problems.[/red]")
            return None
        
        # Auto-detect role from query if not provided
        if role is None:
            role, query = self.detect_role(query)
        else:
            role = role.lower().strip()
        
        # Validate role
        if role not in self.role_definitions:
            role = "mid"  # Default to mid if invalid
        
        # Auto-detect difficulty from role if not provided
        if difficulty is None:
            difficulty = self.role_definitions[role]["default_difficulty"]
        else:
            difficulty = difficulty.lower().strip()
        
        # Normalize language
        language_lower = language.lower().strip()
        if language_lower not in self.language_extensions:
            print(f"[red]Unsupported language: {language}. Supported: java, c#, javascript, python[/red]")
            return None
        
        language_ext = self.language_extensions[language_lower]
        language_name = "C#" if language_lower == "csharp" else language_lower.capitalize()
        
        # Get role context
        role_config = self.role_definitions[role]
        
        # Create generation prompt with role context
        prompt = f"""You are an expert coding problem creator. Generate a {difficulty} difficulty coding problem.

TARGET ROLE: {role.upper()}
ROLE CONTEXT: {role_config['context']}
FOCUS AREAS: {role_config['focus']}

Requirements:
1. Language: {language_name}
2. Difficulty: {difficulty}
3. Topic/Description: {query}
4. Create a problem appropriate for a {role} engineer
5. Include considerations relevant to this role level
6. Edge cases and optimization should match this role's expectations

Provide your response in this EXACT JSON format (no markdown, just raw JSON):
{{
    "title": "Problem Title",
    "description": "Clear description of the problem. What should the user solve?",
    "role_context": "Why this matters for a {role} engineer",
    "topics": ["topic1", "topic2"],
    "difficulty": "{difficulty}",
    "language": "{language_lower}",
    "function_name": "functionName",
    "function_signature": "type functionName(params)",
    "params": "param1, param2",
    "test_cases": [
        {{"input": "example input", "expected_output": "example output", "explanation": "why"}},
        {{"input": "input2", "expected_output": "output2", "explanation": "explanation"}}
    ],
    "hints": ["hint1", "hint2"],
    "time_complexity": "O(n)",
    "space_complexity": "O(1)",
    "starter_code": "function or method skeleton"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            problem_data = json.loads(response_text)
            
            # Add role information to problem data
            problem_data["role"] = role
            problem_data["role_context"] = role_config["context"]
            
            # Save problem to file
            saved_problem = self._save_problem_file(problem_data, language_lower)
            
            if saved_problem:
                return saved_problem
            else:
                print("[red]Failed to save generated problem[/red]")
                return None
                
        except Exception as e:
            print(f"[red]Error generating problem: {e}[/red]")
            return None

    
    def _save_problem_file(self, problem_data: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """Save generated problem to file"""
        try:
            # Create filename from title
            title = problem_data.get("title", "Problem")
            safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', title)
            filename = f"Generated_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            ext = self.language_extensions.get(language, ".java")
            filepath = self.generated_problems_dir / f"{filename}{ext}"
            
            # Create code file
            code_content = self._create_code_file(problem_data, language)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            # Create problem metadata file
            metadata_path = filepath.with_suffix('.json')
            metadata = {
                "title": problem_data.get("title"),
                "description": problem_data.get("description"),
                "role": problem_data.get("role", "mid"),
                "role_context": problem_data.get("role_context", ""),
                "topics": problem_data.get("topics", []),
                "difficulty": problem_data.get("difficulty", "medium"),
                "language": language,
                "test_cases": problem_data.get("test_cases", []),
                "hints": problem_data.get("hints", []),
                "time_complexity": problem_data.get("time_complexity"),
                "space_complexity": problem_data.get("space_complexity"),
                "generated_at": datetime.now().isoformat(),
                "code_file": str(filepath)
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Return problem with file paths
            return {
                **metadata,
                "file_path": str(filepath),
                "metadata_path": str(metadata_path),
                "generated": True
            }
            
        except Exception as e:
            print(f"[red]Error saving problem file: {e}[/red]")
            return None
    
    def _create_code_file(self, problem_data: Dict[str, Any], language: str) -> str:
        """Create the code file content"""
        title = problem_data.get("title", "Problem")
        description = problem_data.get("description", "")
        function_name = problem_data.get("function_name", "solve")
        params = problem_data.get("params", "")
        test_cases = problem_data.get("test_cases", [])
        hints = problem_data.get("hints", [])
        
        # Build comments
        comments = [
            f"// Problem: {title}",
            f"// Difficulty: {problem_data.get('difficulty')}",
            f"// Description: {description[:100]}...",
            "//",
            "// Test Cases:"
        ]
        
        for i, tc in enumerate(test_cases[:3], 1):
            comments.append(f"// {i}. Input: {tc.get('input')} => Output: {tc.get('expected_output')}")
        
        if hints:
            comments.append("//")
            comments.append("// Hints:")
            for hint in hints[:3]:
                comments.append(f"// - {hint}")
        
        comment_block = "\n".join(comments)
        
        # Build test code
        test_code = self._build_test_code(test_cases, language)
        
        # Get template and fill it
        if language == "java":
            class_name = self._to_pascal_case(problem_data.get("function_name", "Solve"))
            template = self.language_templates["java"]
            code = template.format(class_name=class_name, test_code=test_code)
        elif language == "csharp":
            class_name = self._to_pascal_case(problem_data.get("function_name", "Solve"))
            template = self.language_templates["csharp"]
            code = template.format(class_name=class_name, test_code=test_code)
        elif language == "javascript":
            template = self.language_templates["javascript"]
            code = template.format(function_name=function_name, params=params, test_code=test_code)
        else:  # python
            template = self.language_templates["python"]
            code = template.format(function_name=function_name, params=params, test_code=test_code)
        
        return f"{comment_block}\n\n{code}"
    
    def _build_test_code(self, test_cases: List[Dict], language: str) -> str:
        """Build test code for the given language"""
        if not test_cases:
            return "// Add test cases here"
        
        test_code_lines = []
        
        for i, tc in enumerate(test_cases[:3], 1):
            input_val = tc.get("input", "")
            expected = tc.get("expected_output", "")
            explanation = tc.get("explanation", "")
            
            if language == "java":
                test_code_lines.append(f"// Test {i}: {explanation}")
                test_code_lines.append(f"// Input: {input_val}")
                test_code_lines.append(f"// Expected: {expected}")
            elif language == "csharp":
                test_code_lines.append(f"// Test {i}: {explanation}")
                test_code_lines.append(f"// Input: {input_val}")
                test_code_lines.append(f"// Expected: {expected}")
            elif language == "javascript":
                test_code_lines.append(f"// Test {i}: {explanation}")
                test_code_lines.append(f"console.log('Input: {input_val}');")
                test_code_lines.append(f"console.log('Expected: {expected}');")
            else:  # python
                test_code_lines.append(f"# Test {i}: {explanation}")
                test_code_lines.append(f"# Input: {input_val}")
                test_code_lines.append(f"# Expected: {expected}")
        
        return "\n".join(test_code_lines)
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        return ''.join(word.capitalize() for word in snake_str.split('_'))
    
    def list_generated_problems(self) -> List[Dict[str, Any]]:
        """List all generated problems"""
        generated = []
        
        for json_file in self.generated_problems_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    problem_data = json.load(f)
                    problem_data["generated"] = True
                    generated.append(problem_data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return generated
    
    def delete_generated_problem(self, problem_title: str) -> bool:
        """Delete a generated problem by title"""
        try:
            for json_file in self.generated_problems_dir.glob("*.json"):
                with open(json_file, 'r') as f:
                    problem_data = json.load(f)
                    if problem_data.get("title") == problem_title:
                        # Delete both JSON and code files
                        json_file.unlink()
                        code_file = json_file.with_suffix('.java')
                        if not code_file.exists():
                            code_file = json_file.with_suffix('.cs')
                        if not code_file.exists():
                            code_file = json_file.with_suffix('.js')
                        if not code_file.exists():
                            code_file = json_file.with_suffix('.py')
                        if code_file.exists():
                            code_file.unlink()
                        return True
            return False
        except Exception as e:
            print(f"Error deleting problem: {e}")
            return False


if __name__ == "__main__":
    generator = ProblemGenerator()
    
    # Test generation
    problem = generator.generate_problem(
        "Create a problem about sorting arrays",
        language="python",
        difficulty="medium"
    )
    
    if problem:
        print(f"\n✓ Generated problem: {problem['title']}")
        print(f"  File: {problem['file_path']}")
    else:
        print("Failed to generate problem")
