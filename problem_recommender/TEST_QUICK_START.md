# Quick Start: Automated Test Execution

Get your solutions auto-graded in seconds!

## 30-Second Quick Start

```bash
# 1. Start the recommender
python3 main.py

# 2. Type: test
> test

# 3. Provide your solution file path
Enter path to your solution file: ./solution.py

# 4. Choose language
Programming language: python

# 5. (Optional) Enter problem name
Problem name: palindrome checker

# 6. Done! See instant feedback
```

## Complete Example Workflow

### Step 1: Generate a Problem

```bash
python3 main.py
> generate

What kind of problem? > check if a string is a palindrome
Language: python
Difficulty: easy
✨ Problem Generated!
📁 Saved to: generated_problems/problem_001_palindrome/problem_001_palindrome.py
```

### Step 2: Write Your Solution

Edit the generated file and implement your solution:

```python
# generated_problems/problem_001_palindrome/problem_001_palindrome.py
def is_palindrome(s: str) -> bool:
    # Remove spaces and convert to lowercase
    clean = s.replace(" ", "").lower()
    # Check if it reads the same forwards and backwards
    return clean == clean[::-1]
```

### Step 3: Test Your Solution

```bash
python3 main.py
> test

Enter path to your solution file: generated_problems/problem_001_palindrome/problem_001_palindrome.py
Programming language: python
Problem name: palindrome checker

Running tests...

============================================================
Test Results: 3/3 passed (100.0%)
Total Time: 0.012s
============================================================

✅ Test 1:
   Input: "racecar"
   Expected: true
   Got: true
   Time: 0.008s
   Explanation: Correctly identified palindrome

✅ Test 2:
   Input: "hello"
   Expected: false
   Got: false
   Time: 0.002s

✅ Test 3:
   Input: "a man a plan a canal panama"
   Expected: true
   Got: true
   Time: 0.002s

🎉 All tests passed! Great job!

Mark as completed? [Y/n]: y
✓ Marked as completed
```

### Step 4: Check Your Progress

```bash
> insights

📊 Your Learning Profile
========================

📈 Strong Areas (4):
  - palindrome_checking (100%)
  - string_manipulation (85%)
  - algorithms (72%)
  - python (91%)

📉 Areas to Improve (2):
  - recursion (35%) ⬆️ up 15%
  - dynamic_programming (22%)

🎯 Recommended Next:
  - Recursion problem (currently weak)
  - Medium difficulty (you're ready)
```

## Different Scenarios

### Scenario 1: Testing Your Own File

```bash
python3 main.py
> test

Enter path: ./my_solutions/binary_search.py
Language: java
Problem name: binary search

No test cases found. Provide test cases:
Input (or 'done'): [1,3,5,6], target=5
Expected output: 2
Explanation: Target found at index 2
Input (or 'done'): [1,3,5,6], target=7
Expected output: 4
Explanation: Should insert at end
Input (or 'done'): done

Running tests...
[Test results shown]
```

### Scenario 2: Testing Generated Problem

```bash
python3 main.py
> generated

[List shows all your generated problems]

> test
Enter path: generated_problems/problem_003_sorting/solution.py
Language: python
Problem name: quick sort  # or auto-detected

[System finds test cases automatically]
Running tests...
[Results shown]
```

### Scenario 3: Testing in Different Language

```bash
python3 main.py
> test

Enter path: ./leetcode/Solution.java
Language: java  # Compiler needed!
Problem name: two sum

[Must have javac installed]
```

## What You'll See

### ✅ All Tests Pass
```
🎉 All tests passed! Great job!
Mark as completed? [Y/n]: y
```

### ⚠️ Some Tests Fail
```
📝 2 test(s) failed. Check the details above.

❌ Test 2:
   Input: [1,2,3]
   Expected: 6
   Got: 5
   Error: Off-by-one error?

Mark as attempted? [Y/n]: y
```

### 🔧 Compilation Error
```
❌ Compilation Error:
   error: class Solution is public, 
   should be declared in a file named Solution.java
```

### ⏱️ Timeout
```
❌ Test 3:
   Error: Timeout (>10s)
   Explanation: Likely infinite loop or inefficient algorithm
```

## Language Requirements

Before testing, ensure you have:

### Python
```bash
# Check
python3 --version

# Already have it if you're using venv
```

### Java
```bash
# Check
javac -version

# Install (macOS)
brew install openjdk

# Install (Linux)
sudo apt-get install openjdk-11-jdk
```

### JavaScript
```bash
# Check
node --version

# Install (macOS)
brew install node

# Install (Linux)
sudo apt-get install nodejs npm
```

### C#
```bash
# Check
csc --version

# Install (macOS)
brew install --cask dotnet

# Install (Linux/Windows)
# See microsoft.com/net
```

## Common Issues & Fixes

### "File not found"
- Use full path: `/Users/username/solution.py`
- Or relative: `./generated_problems/solution.py`

### "ModuleNotFoundError" (Python)
- Make sure you're in venv: `source venv/bin/activate`
- Or install missing package: `pip install package_name`

### "Class not found" (Java)
- Class must be public
- Filename must match class name
- Example: `public class Solution` in `Solution.java`

### Tests pass locally but fail here
- Check output format (case, spaces, newlines)
- Use `repr()` to see exact characters
- Example: `print(repr(output))`

## Tips for Success

✅ **Start with easy problems** - Build confidence  
✅ **Read test case explanations** - Understand requirements  
✅ **Run tests frequently** - Get quick feedback  
✅ **Check feedback insights** - See your progress  
✅ **Practice weak areas** - System recommends them  

## Next Steps

1. **Generate your first problem**: `python3 main.py > generate`
2. **Write a solution**: Edit the generated file
3. **Test it**: Type `test` and follow prompts
4. **Fix issues**: Use feedback to improve
5. **View progress**: Type `insights` to see improvements

---

**Ready to test?** Run `python3 main.py` and type `test`! 🧪
