# Automated Test Execution & Feedback

The problem recommender now includes automated test execution to automatically grade your solutions across multiple programming languages.

## Features

✅ **Multi-Language Support**: Java, Python, JavaScript, C#  
✅ **Automatic Grading**: Run your code against test cases automatically  
✅ **Detailed Feedback**: See pass/fail for each test with explanations  
✅ **Performance Tracking**: Execution time measured for each test  
✅ **Integrated Feedback**: Test results feed into your learning profile  
✅ **Easy Setup**: Works with code files you already have

## Quick Start

### 1. Generate or Create a Problem

```bash
python3 main.py
> generate
# Follow prompts to create a problem with test cases
```

### 2. Write Your Solution

Create your solution file (e.g., `solution.py`, `Solution.java`, etc.)

### 3. Test Your Solution

```bash
python3 main.py
> test

Enter path to your solution file: /path/to/solution.py
Programming language: python
Problem name: palindrome checker
# System automatically finds test cases or prompts for them
```

## Interactive Test Command

```
What are you looking for? > test

Enter path to your solution file: ./generated_problems/Check_Palindrome/check_palindrome.py
Programming language [java/python/javascript/csharp/c#]: python
Problem name (or enter to skip): palindrome checker

Running tests...

============================================================
Test Results: 3/3 passed (100.0%)
Total Time: 0.023s
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
   Time: 0.007s
   Explanation: Correctly identified non-palindrome

✅ Test 3:
   Input: ""
   Expected: true
   Got: true
   Time: 0.008s
   Explanation: Empty string is palindrome by definition

🎉 All tests passed! Great job!

Mark as completed? [Y/n]: y
```

## Command-Line Usage

Test a solution directly from the command line:

```bash
# Interactive test (recommended)
python3 main.py

# Then type: test
```

## Supported Languages

### Python
- Extensions: `.py`
- Requirements: Python 3.8+ installed
- Will use same Python interpreter as your environment
- Supports any valid Python code

### Java
- Extensions: `.java`
- Requirements: Java Development Kit (JDK) installed
- Requires public class definition
- Compiled to bytecode before execution

### JavaScript
- Extensions: `.js`
- Requirements: Node.js installed
- Supports ES6+ syntax
- Can use async/await

### C#
- Extensions: `.cs`
- Requirements: .NET SDK installed
- Compiles to executable before running
- Supports .NET Framework features

## Test Case Format

Test cases should include:

```json
{
  "input": "value to pass to stdin",
  "expected_output": "what your program should print",
  "explanation": "why this test matters"
}
```

### Examples

**Array Sorting Problem**:
```json
{
  "input": "5 2 8 1 9",
  "expected_output": "1 2 5 8 9",
  "explanation": "Should sort array in ascending order"
}
```

**String Manipulation**:
```json
{
  "input": "hello",
  "expected_output": "HELLO",
  "explanation": "Should convert to uppercase"
}
```

**Multiple Lines**:
```json
{
  "input": "3\n1\n2\n3",
  "expected_output": "6",
  "explanation": "Should sum all numbers (1+2+3=6)"
}
```

## Test Results Explained

### ✅ Test Passed
- Your output exactly matches expected output
- Execution completed within timeout (10s)
- Time shows how long your code took

### ❌ Test Failed
- Output doesn't match expected
- Shows what you got vs what was expected
- Check the explanation for hints

### ⏱️ Timeout
- Your code took longer than 10 seconds
- Likely infinite loop or inefficient algorithm
- Optimize your solution

### 🔧 Compilation Error
- Your code won't compile (Java/C#)
- Check syntax and class definitions
- Make sure all imports are available

### 💥 Runtime Error
- Code compiles but crashes during execution
- Check for null pointer exceptions, type errors
- Review error message for details

## Integration with Feedback System

Test results automatically integrate with your learning system:

1. **Test Results Recorded**: Pass/fail for each problem
2. **Success Rate Tracked**: How many tests you pass
3. **Learning Profile Updated**: Topics you practice appear in insights
4. **Recommendations Adjusted**: System learns from your performance

### Example Flow

```
Generate Problem (topic: binary search)
    ↓
Write Solution (solution.py)
    ↓
Run Tests (3/3 passed)
    ↓
Feedback Recorded (binary search: strong)
    ↓
Next Recommendation (boost weak areas, maintain strong areas)
```

## Troubleshooting

### "File not found" Error

**Problem**: Can't locate solution file  
**Solution**: Provide full path or relative path from current directory
```bash
# Good
/Users/username/solutions/binary_search.py
./generated_problems/problem_001/solution.py

# Less reliable  
solution.py
```

### "Compiler not found" Error

**For Java**:
```bash
# Install Java Development Kit
# macOS: brew install openjdk
# Ubuntu: sudo apt-get install openjdk-11-jdk
# Windows: Download from oracle.com/java
```

**For C#**:
```bash
# Install .NET SDK
# macOS: brew install --cask dotnet
# Ubuntu: Follow microsoft.com/net/download
# Windows: Download from microsoft.com
```

**For JavaScript**:
```bash
# Install Node.js
# macOS: brew install node
# Ubuntu: sudo apt-get install nodejs npm
# Windows: Download from nodejs.org
```

### "No main method" (Java)

Your Java class needs a main method:
```java
public class Solution {
    public static void main(String[] args) {
        // Your code here
        System.out.println("output");
    }
}
```

### Tests Pass Locally But Fail in System

**Common Issues**:
- Output format differs (extra spaces, different line breaks)
- Case sensitivity (`true` vs `True`)
- Floating point precision
- Off-by-one errors in output

**Debug Tips**:
1. Print exact input/output: `print(repr(output))`
2. Strip whitespace: `output.strip()`
3. Compare character by character
4. Check for trailing newlines

## Performance Benchmarks

Expected execution times per test:

| Language | Typical | Timeout |
|----------|---------|---------|
| Python | 5-50ms | 10s |
| Java | 100-500ms | 10s |
| JavaScript | 10-100ms | 10s |
| C# | 50-200ms | 10s |

*First run slower due to compilation/startup overhead*

## Advanced Usage

### Manual Test Cases

If generated problem has no test cases, you can add them manually:

```
Enter path to your solution file: ./solution.py
Programming language: python
Problem name: custom problem
No test cases found. Provide test cases:
Format: input | expected_output | explanation

Input (or 'done' to finish): hello world
Expected output: HELLO WORLD
Explanation: Should uppercase all characters
Input (or 'done' to finish): done
```

### Testing Generated Problems

Generated problems automatically include test cases:

```bash
python3 main.py
> generated

# Select a problem, copy its path
> test
# Paste the path
# System finds test cases automatically
```

## Best Practices

✅ **DO**:
- Test multiple edge cases
- Check for off-by-one errors
- Test with empty inputs
- Test with maximum constraints
- Review explanation for each test

❌ **DON'T**:
- Hardcode test outputs
- Ignore timeout warnings
- Skip failed tests without reviewing
- Assume input format without checking
- Skip feedback step

## Example Workflows

### Workflow 1: Generated Problem
```
1. python3 main.py
2. > generate
3. Create "quick sort in Python"
4. Edit the generated file
5. > test
6. System runs automatically
7. Fix failures
8. Test again until 100% pass
9. > insights  (view progress)
```

### Workflow 2: Custom Problem
```
1. Create your own solution file
2. python3 main.py
3. > test
4. Provide file path
5. Manually add test cases
6. Get feedback
7. Improve solution
8. Test again
```

### Workflow 3: LeetCode Practice
```
1. Copy problem to generated_problems/
2. Write solution locally
3. python3 main.py
4. > test
5. Paste test cases from LeetCode
6. Get detailed feedback
7. Track progress in insights
```

## Limitations

- **Timeout**: 10 seconds per test (prevent infinite loops)
- **Memory**: No explicit limit (system dependent)
- **I/O**: Only stdin/stdout supported (not file I/O)
- **Network**: No network access in tests
- **Installation**: Requires language compilers/runtimes

## Next Steps

1. ✅ Generate a problem
2. ✅ Write a solution
3. ✅ Run tests with `test` command
4. ✅ Review feedback
5. ✅ Fix failures
6. ✅ Check your insights

---

**Ready to test your solutions?** Run `python3 main.py` and type `test`! 🚀
