# Role-Aware Problem Generation

Generate interview problems tailored to your career level - from entry-level to principal engineer.

## Overview

Problems are now automatically calibrated to your role:
- **Junior/Entry**: Fundamentals, basic algorithms, simple data structures
- **Mid-Level**: Design patterns, optimization, balanced complexity
- **Senior/Staff**: System design, edge cases, scalability, leadership
- **Principal**: Advanced architecture, novel approaches, system-level thinking

## Quick Examples

### Auto-Detection from Natural Language
```bash
python3 cli/main.py
> generate

What problem? > staff swe palindrome checker in java
Detected: STAFF level problem
Use default difficulty (hard) for staff? [Y/n]: y

# Generates Staff-level problem automatically
```

### Different Role Levels
```
"junior sorting problem in python"
→ Easy difficulty, fundamentals focus

"mid level tree traversal in java"
→ Medium difficulty, design patterns

"senior binary search in c#"
→ Hard difficulty, optimization focus

"principal system design in javascript"
→ Hard difficulty, architecture focus
```

## Supported Roles

### Junior/Entry-Level
- **Aliases**: junior, entry, entry-level, jr, graduate
- **Default Difficulty**: Easy
- **Focus**: Fundamentals, basic algorithms, simple data structures
- **Context**: Entry-level position, focus on understanding core concepts
- **Example**: "Implement a basic sorting algorithm"

### Mid-Level
- **Aliases**: mid, mid-level, intermediate, senior-engineer
- **Default Difficulty**: Medium
- **Focus**: Design patterns, optimization, complex data structures
- **Context**: Mid-level engineer, expected to handle complexity and make design decisions
- **Example**: "Optimize a tree traversal with proper error handling"

### Senior/Staff
- **Aliases**: senior, sr, staff, staff-level, staff swe, staff-swe
- **Default Difficulty**: Hard
- **Focus**: System design, optimization, edge cases, scalability
- **Context**: Staff/Senior engineer, expected deep expertise, optimization, and system-level thinking
- **Example**: "Design a distributed palindrome detection system handling massive scale"

### Principal
- **Aliases**: principal, principal engineer, distinguished
- **Default Difficulty**: Hard
- **Focus**: Advanced system design, novel approaches, technical leadership
- **Context**: Principal engineer, expected to solve complex architectural problems with nuance
- **Example**: "Architect a next-generation text processing pipeline with novel optimizations"

## How Role Works

### 1. Auto-Detection
The system detects role keywords in your description:
```bash
"staff swe question about..." → Staff level detected
"junior sorting problem..." → Junior level detected
```

### 2. Difficulty Association
Role automatically suggests difficulty:
```
Junior → Easy
Mid → Medium
Senior/Staff → Hard
Principal → Hard
```

### 3. Problem Calibration
AI generates problems appropriate to the role:
- **Scope**: What's expected at that level
- **Complexity**: Edge cases and optimizations relevant to role
- **Context**: Why it matters at that career stage

### 4. Override Options
You can override both role and difficulty:
```bash
> generate
Role Detected: STAFF
Keep this role? [Y/n]: n
Select role: [junior/mid/senior/principal]: mid

Use default difficulty (medium) for mid? [Y/n]: n
Difficulty: [easy/medium/hard]: hard
```

## Usage Examples

### Example 1: Generate Staff-Level Problem
```bash
python3 cli/main.py
> generate

What problem? > staff swe palindrome detector in java
Detected: STAFF level problem
Keep this role? [Y/n]: y

Language: java
Use default difficulty (hard) for staff? [Y/n]: y

Generating problem...

✨ Problem Generated!

👤 STAFF | Difficulty: HARD | Language: JAVA

Palindrome Detection at Scale
Why this matters: Staff engineers are expected to design 
systems that handle massive scale and edge cases...
```

### Example 2: Entry-Level Practice
```bash
What problem? > junior binary search in python
Detected: JUNIOR level problem

Language: python
[Auto uses easy difficulty]

✨ Problem Generated!

👤 JUNIOR | Difficulty: EASY | Language: PYTHON

Binary Search Implementation
Why this matters: Understanding binary search is 
fundamental for junior engineers...
```

### Example 3: Mixed Interview Prep
```bash
> generate
What problem? > sorting algorithm

[No role detected - defaults to MID]
Detected: MID level problem

> generate
What problem? > staff swe system design for caching

[Automatically detects STAFF]
Detected: STAFF level problem
```

## Generated Problem Details

Each generated problem includes:
- **Title**: Clear problem name
- **Role**: Target role level
- **Role Context**: Why it matters at that career level
- **Description**: Clear problem statement
- **Difficulty**: Easy/Medium/Hard
- **Topics**: Related concepts (arrays, trees, etc.)
- **Test Cases**: Comprehensive test coverage
- **Hints**: Progressive hints
- **Complexity**: Time and space complexity info

## Viewing Generated Problems

List all problems with role context:
```bash
python3 cli/main.py
> generated

Generated Problems (5)

┌─────────────────────┬─────────┬────────────┬──────────┐
│ Title               │ Role    │ Difficulty │ Language │
├─────────────────────┼─────────┼────────────┼──────────┤
│ Palindrome Checker  │ STAFF   │ HARD       │ JAVA     │
│ Binary Search       │ JUNIOR  │ EASY       │ PYTHON   │
│ Tree Traversal      │ MID     │ MEDIUM     │ C#       │
│ Caching System      │ SENIOR  │ HARD       │ PYTHON   │
│ API Design          │ STAFF   │ HARD       │ JAVA     │
└─────────────────────┴─────────┴────────────┴──────────┘
```

## Interview Preparation Workflows

### Workflow 1: Target Specific Role
```bash
# Generate 5 Staff-level problems
> generate
> staff swe array manipulation in java

# Test your solution
> test

# See improvement
> insights

# Generate another
> generate
> staff swe system design in python

# Track progress across role level
```

### Workflow 2: Level Progression
```bash
# Start junior
> generate > junior string problem

# Test and master
> test

# Progress to mid
> generate > mid string problem

# Eventually reach senior
> generate > senior string problem
```

### Workflow 3: Role-Specific Interview Prep
```bash
# If targeting Staff SWE role
> generate > staff swe question in java
> generate > staff swe question in python
> generate > staff swe system design in java

# Get consistent difficulty and expectations
```

## AI Prompt Integration

The AI receives role context:
- **Role Level**: junior/mid/senior/principal
- **Focus Areas**: What's important at that level
- **Context**: Why this matters to that engineer
- **Difficulty**: Expected complexity level

This ensures generated problems:
- ✅ Match interview expectations for that role
- ✅ Have appropriate complexity
- ✅ Test relevant skills
- ✅ Include role-appropriate edge cases

## Tips for Best Use

✅ **DO:**
- Be explicit about role in description
- Start at your current level
- Progress upward as you improve
- Use role context to understand expectations
- Build a strong foundation at each level

❌ **DON'T:**
- Skip levels (go to staff without mastering mid)
- Ignore the role context explanation
- Only practice one role level
- Assume "hard = good" (hard for your level is right)

## Role Progression Path

```
Junior → Master basics
   ↓
Mid → Handle complexity
   ↓
Senior → Optimize & edge cases
   ↓
Staff → System design & scale
   ↓
Principal → Architecture & innovation
```

## Natural Language Examples

These all work and auto-detect roles:

**Junior/Entry**:
```
"junior sorting problem"
"entry level array question"
"jr palindrome checker"
"graduate coding challenge"
```

**Mid-Level**:
```
"mid level tree problem"
"intermediate system design"
"mid-level optimization"
```

**Senior/Staff**:
```
"senior sorting system"
"staff swe caching"
"staff-level scalability"
"senior engineer problem"
```

**Principal**:
```
"principal system design"
"principal engineer question"
"distinguished architecture"
```

## Integration with Learning System

When you generate and test role-aware problems:
1. Problem generated at your target role level
2. You test your solution (auto-graded)
3. Results recorded with role context
4. Learning profile updated by role
5. Insights show progress by career level
6. Recommendations adjusted per role

## Frequently Asked Questions

**Q: What if I don't specify a role?**  
A: System defaults to Mid-Level. Difficulty and problem scope will be balanced.

**Q: Can I change role after generating?**  
A: Yes, you can override during generation. Just answer "No" when asked to keep detected role.

**Q: Will higher role problems help me more?**  
A: Not necessarily. Start at your level. Staff-level problems are harder and require prerequisites.

**Q: Can I practice multiple role levels?**  
A: Yes! Generate problems at different levels to progress your skills.

**Q: Does role affect test execution?**  
A: No, test execution is the same. Only problem generation is role-aware.

## Next Steps

1. **Generate your first role-aware problem**:
   ```bash
   python3 cli/main.py
   > generate
   # Type: "staff swe [topic] in [language]"
   ```

2. **Notice the difference**: Staff problems have more scope and complexity

3. **Test and see results**: How does auto-grading work?

4. **Track progress**: Use insights to see which roles you're strong in

5. **Target growth**: Generate more in weaker roles

---

**Ready to generate role-tailored problems?** Run `python3 cli/main.py` and type `generate`! 🚀
