# Problem Generation System

The Problem Generation Engine allows you to dynamically create new coding problems using AI, save them to files, and access them through your problem recommender system.

## Features

✨ **AI-Powered Generation**: Creates unique problems based on natural language descriptions
📁 **Multi-Language Support**: Generate problems for Java, C#, JavaScript, and Python
🎯 **Difficulty Levels**: Choose from easy, medium, and hard
💾 **File Persistence**: Saves problems as both code files and metadata JSON
🧪 **Built-in Test Cases**: Each problem includes test cases and hints
📊 **Integration**: Generated problems integrate with feedback and tracking systems

## Usage

### Interactive Mode

1. **Start the application**:
   ```bash
   python3 main.py
   ```

2. **Generate a new problem** (option 1 - Simple):
   ```
   What are you looking for? > generate
   What kind of problem do you want to create? > sorting algorithm problem
   Language [java/csharp/javascript/python]: > python
   Difficulty [easy/medium/hard]: > medium
   ```

3. **Generate a new problem** (option 2 - Natural language):
   ```
   What are you looking for? > create a palindrome checker in Java
   Generate a new problem? [Y/n]: > y
   ```

4. **View generated problems**:
   ```
   What are you looking for? > generated
   ```

### Command Line Mode

Generate a problem from the terminal:

```bash
# Generate a specific problem
python3 main.py --generate "merge sort implementation in Python"

# List all generated problems
python3 main.py --list-generated
```

## Generated Problem Structure

### File Organization

```
generated_problems/
├── problem_001_merge_sort_python/
│   ├── problem_001_merge_sort_python.json    # Metadata and test cases
│   ├── problem_001_merge_sort_python.py      # Python code file
│   ├── problem_001_merge_sort_python.java    # Java implementation (if requested)
│   └── solution_001_merge_sort_python.py     # Reference solution
└── problem_002_tree_traversal_java/
    ├── problem_002_tree_traversal_java.json
    ├── problem_002_tree_traversal_java.java
    └── solution_002_tree_traversal_java.java
```

### Metadata JSON Format

Each generated problem includes a JSON file with:

```json
{
  "id": "problem_001",
  "title": "Merge Sort Implementation",
  "description": "Implement the merge sort algorithm...",
  "language": "python",
  "difficulty": "medium",
  "topics": ["sorting", "divide-and-conquer", "arrays"],
  "estimated_time_minutes": 45,
  "solution_approach": "Use divide-and-conquer...",
  "test_cases": [
    {
      "input": "[5, 2, 8, 1, 9]",
      "expected_output": "[1, 2, 5, 8, 9]",
      "explanation": "Sorts in ascending order"
    }
  ],
  "hints": [
    "Start by dividing the array in half",
    "Merge two sorted arrays efficiently"
  ],
  "file_path": "/path/to/problem_001_merge_sort_python.py",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Supported Languages

### Java
- File extension: `.java`
- Class-based structure
- Includes public methods for solutions

### Python
- File extension: `.py`
- Function-based approach
- Uses type hints

### JavaScript
- File extension: `.js`
- ES6+ syntax
- Includes async examples when appropriate

### C#
- File extension: `.cs`
- Class-based with methods
- Includes LINQ examples where applicable

## Integration with Feedback System

Generated problems automatically integrate with your feedback system:

1. **Track Attempts**: Mark generated problems as attempted
   ```
   Mark this as attempted? [Y/n]: > y
   ✓ Marked as attempted
   ```

2. **Record Completion**: Mark as completed with performance feedback
   - Time spent
   - Difficulty experienced
   - Topics mastered

3. **Learning Insights**: Generated problem data feeds into skill profiling
   - Topics you generate problems for appear in learning insights
   - Completion patterns help identify growth areas

## Advanced Features

### Bulk Generation

Generate multiple problems at once:

```python
from problem_generator import ProblemGenerator

generator = ProblemGenerator()

problems = [
    ("binary search in Java", "java", "medium"),
    ("hash map implementation in Python", "python", "hard"),
    ("linked list reversal in JavaScript", "javascript", "easy"),
]

for description, language, difficulty in problems:
    problem = generator.generate_problem(description, language, difficulty)
    print(f"Generated: {problem['title']}")
```

### Custom Problem Templates

Edit the problem generator to add custom templates for specific domains (algorithms, web development, databases, etc.).

## Performance Tips

1. **Language Selection**: Choose the language you want to practice most
2. **Difficulty Progression**: Start with easy, progress to hard
3. **Variety**: Generate problems across different topics
4. **Feedback**: Rate problems to help the system learn your preferences

## Troubleshooting

### Problem generation times out
- Check your internet connection
- Verify your API keys are valid
- Try a simpler problem description

### Files not saving
- Ensure `generated_problems/` directory has write permissions
- Check available disk space
- Verify the application has write access to the directory

### Generated problems don't appear in list
- Run `python3 main.py --list-generated` to verify location
- Check `generated_problems/` directory manually
- Restart the application

## Configuration

Edit `config.py` to customize:

```python
# Location where generated problems are saved
GENERATED_PROBLEMS_DIR = "generated_problems"

# Maximum problems to keep (0 = unlimited)
MAX_GENERATED_PROBLEMS = 0

# API endpoint for generation
GENERATION_MODEL = "gpt-4o-mini"
```

## Best Practices

✅ **DO**:
- Generate problems that match your learning goals
- Rate and complete generated problems
- Start with easy, progress gradually
- Create problems in languages you want to master
- Use the hints if you get stuck

❌ **DON'T**:
- Generate too many problems without practicing them
- Skip providing problem descriptions (be specific!)
- Ignore the difficulty recommendations
- Delete problems before completing them
- Skip the feedback process

## Examples

### Example 1: Learn Python Data Structures
```
What are you looking for? > create a binary search tree in Python with insert and search methods
Language: python
Difficulty: medium
→ Generated problem with test cases for insert/search operations
```

### Example 2: Practice Java Algorithms
```
python3 main.py --generate "quicksort algorithm with random pivot selection in Java"
→ Creates Java implementation with multiple test cases
```

### Example 3: JavaScript Web Development
```
What are you looking for? > generate a function to validate email addresses in JavaScript
Language: javascript
Difficulty: easy
→ Quick problem to practice regex in JavaScript
```

## Next Steps

1. ✅ Generate your first problem
2. 📝 Work through the problem and test cases
3. ⭐ Rate the problem difficulty
4. 🎯 Check learning insights to see what topics you're practicing
5. 📈 Use insights to guide future generation

---

**Need help?** Check `QUICK_START.md` or `README.md` for additional guidance!
