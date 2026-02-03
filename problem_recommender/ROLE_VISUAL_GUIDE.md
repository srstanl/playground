# Role-Aware Generation Feature - Visual Guide

## Feature Overview

```
┌─────────────────────────────────────────────────────────────────┐
│           ROLE-AWARE PROBLEM GENERATION WORKFLOW                │
└─────────────────────────────────────────────────────────────────┘

User Input
    │
    ├─ "staff swe palindrome checker in java"
    │
    ▼
Role Detection Engine
    │
    ├─ Scan for role keywords: "staff", "swe"
    ├─ Match against role_definitions
    └─ Return: (role="senior", clean_query="palindrome checker in java")
    │
    ▼
Role Configuration Lookup
    │
    ├─ role_definitions["senior"]
    ├─ difficulty: "hard"
    ├─ focus: "system design, optimization, edge cases, scalability"
    └─ context: "Staff/Senior engineer, expected deep expertise..."
    │
    ▼
Problem Generation
    │
    ├─ Use cleaned query: "palindrome checker in java"
    ├─ Language: java
    ├─ Difficulty: hard (from role config)
    ├─ AI Prompt includes: role context and expectations
    └─ Generate problem with role-appropriate scope
    │
    ▼
Output Display
    │
    ├─ Title: "Check for Palindrome"
    ├─ Badge: "👤 SENIOR"
    ├─ Difficulty: "HARD"
    ├─ Context: "Why this matters: Staff/Senior engineer..."
    └─ Problem description (Staff-level scope)
    │
    ▼
Metadata Saved
    │
    └─ {
         "title": "Check for Palindrome",
         "role": "senior",
         "role_context": "Staff/Senior engineer...",
         "difficulty": "hard",
         ...
       }
```

## Role Hierarchy

```
┌──────────────────────────────────────────────────────────────┐
│                    CAREER PROGRESSION                        │
└──────────────────────────────────────────────────────────────┘

  JUNIOR                MID                 SENIOR              PRINCIPAL
  ┌─────┐             ┌──────┐             ┌──────┐            ┌──────────┐
  │Entry│             │Balanced│           │Expert│            │Architect │
  │ ─── │             │ ──────│            │ ──── │            │ ───────  │
  │Easy │             │Medium │            │ Hard │            │  Hard    │
  │     │             │       │            │      │            │          │
  │Fund │             │Design │            │System│            │Advanced  │
  │ ─── │             │ ──── │            │ ──── │            │ ───────  │
  │ amentals        │Patterns            │Design              │Architecture
  └─────┘             └──────┘             └──────┘            └──────────┘
    │                   │                    │                   │
    └───────────────────┴────────────────────┴───────────────────┘
              Career Progression Path (with user input)
```

## Role Aliases Map

```
┌────────────────────────────────────────────────────────────────┐
│                    DETECTION KEYWORDS                          │
└────────────────────────────────────────────────────────────────┘

JUNIOR/ENTRY-LEVEL
├─ "junior"
├─ "entry"
├─ "entry-level"
├─ "jr"
└─ "graduate"
   └─ Detected as: JUNIOR → Easy difficulty

MID-LEVEL
├─ "mid"
├─ "mid-level"
├─ "intermediate"
└─ "senior-engineer" (mid-level senior-engineer)
   └─ Detected as: MID → Medium difficulty

SENIOR/STAFF
├─ "senior"
├─ "sr"
├─ "staff"
├─ "staff-level"
├─ "staff swe"
└─ "staff-swe"
   └─ Detected as: SENIOR → Hard difficulty

PRINCIPAL
├─ "principal"
├─ "principal engineer"
└─ "distinguished"
   └─ Detected as: PRINCIPAL → Hard difficulty
```

## Difficulty Calibration

```
┌──────────────────────────────────────────────────────┐
│           DIFFICULTY AUTO-ASSIGNMENT                 │
└──────────────────────────────────────────────────────┘

JUNIOR LEVEL
│
├─ Topics: Basics, fundamentals
├─ Complexity: Single concept per problem
├─ Focus: Core understanding
└─ Default: ⚡ EASY
   (Can override to Medium/Hard for challenge)

MID LEVEL
│
├─ Topics: Design patterns, optimization
├─ Complexity: Multiple related concepts
├─ Focus: Design decisions
└─ Default: ⚔️  MEDIUM
   (Can override to Easy/Hard for flexibility)

SENIOR LEVEL
│
├─ Topics: System design, edge cases, scalability
├─ Complexity: Complete system thinking
├─ Focus: Production-quality solutions
└─ Default: 🔥 HARD
   (Can override to Medium for foundation work)

PRINCIPAL LEVEL
│
├─ Topics: Advanced architecture, novel approaches
├─ Complexity: Architectural decisions
├─ Focus: Technical leadership
└─ Default: 🔥 HARD
   (Usually stay at Hard for consistency)
```

## Feature Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
└──────────────────────────────────────────────────────────────┘

        ┌─────────────────┐
        │  python3 main.py│
        └────────┬────────┘
                 │
        ┌────────▼─────────┐
        │   > generate     │
        └────────┬─────────┘
                 │
    ┌────────────▼──────────────┐
    │ What problem?             │
    │ > staff swe problem       │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Detected: STAFF level     │
    │ Keep this role? [Y/n]: y  │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Language [java]: java      │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │ Use default (hard)? [Y/n]: y      │
    └────────────┬─────────────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │  Generating problem...            │
    │  (AI receives role context)       │
    └────────────┬─────────────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │  ✨ Problem Generated!             │
    │  👤 SENIOR | HARD | JAVA          │
    │  Why this matters: [context]      │
    │  [Problem description...]         │
    └───────────────────────────────────┘
```

## Example Workflows

### Workflow 1: Interview Prep (Staff SWE)

```
Target: Get Staff-level problems for interview prep

> generate
> staff swe sorting in java          ← Role detected: senior
> staff swe caching in java          ← Role detected: senior  
> staff swe system design in python  ← Role detected: senior

Result: 3 Staff-level (hard) problems
        All generated with Staff context
        Can test each one and track progress
```

### Workflow 2: Learning Progression

```
Target: Progressively learn a topic

Step 1: Junior level (master fundamentals)
> generate
> junior binary search in python       ← Easy

Step 2: Mid level (add complexity)
> generate
> mid level binary search optimization ← Medium

Step 3: Senior level (production quality)
> generate
> senior binary search system in python ← Hard (scalability focus)

Result: Learned topic at all levels
        Progressed naturally from basics to expert
```

### Workflow 3: Mixed Interview Prep

```
Target: Comprehensive interview prep

Week 1: Junior Problems
  > junior sorting in java
  > junior arrays in python
  > junior strings in c#

Week 2: Mid Problems
  > mid tree problems in java
  > mid dynamic programming in python

Week 3: Senior Problems
  > senior system design in java
  > staff swe optimization in python

Result: Well-rounded preparation
        Covers all difficulty levels
        Tests against interview standards
```

## Role Context Examples

```
┌──────────────────────────────────────────────────────────────┐
│              WHAT EACH ROLE CONTEXT MEANS                    │
└──────────────────────────────────────────────────────────────┘

JUNIOR
├─ Context: "Entry-level position, focus on understanding 
│             core concepts and fundamentals"
├─ Expectation: You SHOULD understand basic algorithms
├─ Scope: Single concept problems
└─ Example Problem:
   "Implement a basic sorting algorithm"
   (No edge cases, standard implementation)

MID
├─ Context: "Mid-level engineer, expected to handle complexity
│            and make design decisions"
├─ Expectation: You CAN optimize and handle tradeoffs
├─ Scope: Multiple concepts, design choices
└─ Example Problem:
   "Design an efficient caching system"
   (Consider tradeoffs, design patterns)

SENIOR
├─ Context: "Staff/Senior engineer, expected deep expertise,
│            optimization, and system-level thinking"
├─ Expectation: You MUST handle scale, edge cases, production
├─ Scope: System design, optimization, edge cases
└─ Example Problem:
   "Design a distributed palindrome detection system at scale"
   (Scalability, edge cases, production concerns)

PRINCIPAL
├─ Context: "Principal engineer, expected to solve complex
│            architectural problems with nuance"
├─ Expectation: You can INVENT new approaches
├─ Scope: Advanced architecture, novel solutions
└─ Example Problem:
   "Design next-generation text processing with novel optimizations"
   (Architecture, innovation, leadership perspective)
```

## Testing & Validation

```
┌──────────────────────────────────────────────────────────────┐
│                   FEATURE TESTING                            │
└──────────────────────────────────────────────────────────────┘

Test Case 1: Role Detection
├─ Input: "staff swe problem"
├─ Expected: role="senior"
└─ Status: ✅ PASS

Test Case 2: Difficulty Mapping
├─ Input: role="senior"
├─ Expected: difficulty="hard"
└─ Status: ✅ PASS

Test Case 3: Edge Case (no role)
├─ Input: "sorting algorithm"
├─ Expected: role="mid" (default)
└─ Status: ✅ PASS

Test Case 4: Case Insensitive
├─ Input: "STAFF SWE problem"
├─ Expected: role="senior"
└─ Status: ✅ PASS

Test Case 5: Multiple Aliases
├─ Input: "staff-swe problem"
├─ Expected: role="senior" (staff-swe in aliases)
└─ Status: ✅ PASS

Overall Status: ✅ ALL TESTS PASSING
```

## Files & Documentation Map

```
┌──────────────────────────────────────────────────────────────┐
│                DOCUMENTATION ROADMAP                         │
└──────────────────────────────────────────────────────────────┘

START HERE
└─ README.md
   ├─ Quick overview
   └─ Links to all features

QUICK REFERENCE (3 min read)
└─ ROLE_QUICK_REFERENCE.md
   ├─ Role keywords table
   ├─ Difficulty mapping
   └─ Common example queries

COMPREHENSIVE GUIDE (30 min read)
└─ ROLE_AWARE_GENERATION.md
   ├─ Complete role feature guide
   ├─ Interview prep workflows
   ├─ Level progression path
   ├─ FAQ and tips
   └─ Role-specific examples

TECHNICAL DETAILS
├─ IMPLEMENTATION_SUMMARY.md
│  └─ Architecture and test results
│
└─ ROLE_FEATURE_CHANGELOG.md
   └─ Exact code changes and modifications

SYSTEM OVERVIEW
└─ DOCUMENTATION_INDEX.md
   ├─ All documents mapped
   ├─ Navigation guide
   └─ Component explanations
```

## Common Questions (Visual)

```
Q: "Should I use role-aware or difficulty override?"
A: 
   ┌─ Role-Aware (Recommended)
   │  └─ Auto-calibrates based on career level
   │     Ensures appropriate challenge
   │     Includes role context
   │
   └─ Manual Override (Flexibility)
      └─ For specific needs
         For practice at different levels
         Still available if role auto-select is wrong

Q: "How do roles relate to interview prep?"
A:
   ┌─ Interview Level
   │  └─ Match your target role
   │     Staff SWE? Use "staff swe problems"
   │     Senior? Use "senior problems"
   │
   └─ Difficulty Progression
      └─ Start at your level
         Progress upward as you improve
         Don't skip levels

Q: "Can I switch roles?"
A:
   Yes! The system allows:
   ├─ Detect role automatically
   ├─ Confirm or override the role
   ├─ Select different role if desired
   └─ Answer "No" when asked to keep role
```

---

## Quick Start (Visual Summary)

```
┌──────────────────────────────────────────────────────────────┐
│                    5-SECOND START                            │
└──────────────────────────────────────────────────────────────┘

1️⃣  Run the system:
    $ python3 main.py

2️⃣  Choose generate:
    > generate

3️⃣  Describe your problem with role:
    > staff swe palindrome checker in java

4️⃣  Confirm the detected role:
    Detected: STAFF level problem
    Keep this role? [Y/n]: y

5️⃣  Problem generates automatically:
    ✨ Problem Generated!
    👤 STAFF | Difficulty: HARD | Language: JAVA

Done! Your role-appropriate problem is ready! 🎉
```

---

**Ready to generate role-aware problems? Run `python3 main.py` now!**
