# Testing Problem Generation

Quick test guide to verify the problem generation feature is working correctly.

## Pre-Test Checklist

✅ Virtual environment activated:
```bash
source venv/bin/activate
```

✅ Dependencies installed:
```bash
pip list | grep -E "openai|requests|rich"
```

✅ API key configured:
```bash
echo $GITHUB_TOKEN
# or
echo $OPENAI_API_KEY
```

## Test 1: Interactive Generation

```bash
python3 main.py
```

Then type:
```
generate

What kind of problem do you want to create? > binary search algorithm
Language [java/csharp/javascript/python]: > python
Difficulty [easy/medium/hard]: > medium
```

**Expected Result:**
- Problem is generated
- File is created in `generated_problems/`
- Metadata JSON file is created
- Display shows problem title, description, test cases, hints
- Option to mark as attempted appears

## Test 2: Natural Language Generation

```bash
python3 main.py
```

Then type:
```
create a fibonacci sequence generator in Java
```

**Expected Result:**
- System recognizes generation request
- Prompts for confirmation
- Generates problem in Java
- File saved to `generated_problems/problem_XXX_fibonacci_java/`

## Test 3: Command-Line Generation

```bash
python3 main.py --generate "linked list implementation with insert and delete in C#"
```

**Expected Result:**
```
🤖 Problem Generator

✓ Generated: Linked List Implementation
📁 File: generated_problems/problem_XXX_linked_list_csharp/problem_XXX_linked_list_csharp.cs
```

## Test 4: List Generated Problems

```bash
python3 main.py --list-generated
```

**Expected Result:**
Table showing:
- Title
- Difficulty
- Language
- Topics

## Test 5: Integration with Feedback System

1. Generate a problem
2. Mark as attempted
3. Run `insights` command
4. Generated problem should appear in topic frequency

## Expected Generated Files

For each generated problem, you should see:

```
generated_problems/
└── problem_001_binary_search_python/
    ├── problem_001_binary_search_python.json      # Metadata
    ├── problem_001_binary_search_python.py        # Python implementation
    └── solution_001_binary_search_python.py       # Reference solution
```

## Verification

Check that each generated problem JSON contains:

```json
{
  "id": "problem_XXX",
  "title": "...",
  "description": "...",
  "language": "python|java|javascript|csharp",
  "difficulty": "easy|medium|hard",
  "topics": ["topic1", "topic2"],
  "test_cases": [...],
  "hints": [...],
  "file_path": "...",
  "created_at": "..."
}
```

## Troubleshooting

### Problem generation fails
- Check API key: `echo $GITHUB_TOKEN` or `echo $OPENAI_API_KEY`
- Check internet connection
- Check logs in main.py output

### Files not created
- Verify `generated_problems/` directory exists
- Check file permissions: `ls -la generated_problems/`
- Ensure disk space available

### Metadata missing from JSON
- This indicates incomplete generation
- Check that API response was complete
- Try again with simpler description

## Performance Baseline

- Generation time: 15-30 seconds typical
- File creation: <1 second
- Interactive menu: Instant
- List generation: <1 second

## Next Steps

After successful testing:
1. ✅ Test different languages and difficulties
2. ✅ Test feedback integration
3. ✅ Check generated files manually
4. ✅ Try solving generated problems
5. ✅ Verify progress tracking works

---

**All tests passing?** The problem generation feature is ready to use! 🎉
