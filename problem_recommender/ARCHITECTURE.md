# 🎯 Problem Recommender System Overview

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
│                      (cli/main.py - CLI)                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────────────┬──────────────────────┐
             ▼                      ▼                      ▼
        ┌─────────────┐      ┌──────────────┐      ┌────────────┐
        │ AI Agent    │      │ Rules Engine │      │Feedback    │
        │ (OpenAI/GH) │      │ (Adaptive)   │      │Engine      │
        └─────────────┘      └──────────────┘      └────────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    ▼
                        ┌─────────────────────┐
                        │ Problem Analyzer    │
                        │ (Scans Java Files)  │
                        └─────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐  ┌────────────┐  ┌────────────┐
            │ Feedback    │  │ Progress   │  │ Skill      │
            │ History     │  │ Tracker    │  │ Profile    │
            │ (JSON)      │  │ (JSON)     │  │ (JSON)     │
            └─────────────┘  └────────────┘  └────────────┘
```

## Data Flow: How the System Learns

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Extract Preferences      │
│ (roles, languages, etc)  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Score Problems                       │
│ • AI agent: semantic understanding   │
│ • Rules: role/language/topic match   │
│ • Feedback: boost weak areas         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Rank & Recommend Top 5               │
│ (combined scores + feedback weights) │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Display Recommendations              │
│ with difficulty, topics, reasons     │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Collect Feedback                     │
│ • Was it helpful?                    │
│ • How difficult felt?                │
│ • How long did it take?              │
│ • Did you solve it?                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Update Skill Profile                 │
│ • Topic strengths/weaknesses         │
│ • Difficulty comfort levels          │
│ • Success rates                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Adjust Recommendation Weights        │
│ for NEXT iteration ↻                 │
└──────────────────────────────────────┘
```

## Files You Need to Know

### Core System
- **cli/main.py** - CLI surface only
- **api/** - HTTP surface only
- **services/** - shared orchestration used by both surfaces
- **shared/** - shared runtime modules used by CLI, API, and services
- **shared/config.py** - shared runtime configuration and paths
- **shared/rules_engine.py** - shared recommendation scoring logic
- **shared/feedback_engine.py** - shared feedback and skill-profile persistence
- **shared/progress_tracker.py** - shared progress persistence and stats
- **shared/problem_analyzer.py** - transitional filesystem adapter for curated problem corpus
- **shared/problem_generator.py** - transitional generation adapter and persistence logic
- **shared/ai_agent.py** - transitional AI ranking adapter
- **shared/test_executor.py** - transitional test runner adapter

### Data Files (auto-created in `data/`)
- **problems_db.json** - All scanned problems with metadata
- **progress.json** - Your completion history
- **feedback_history.json** - All feedback entries (what the system learns from)
- **skill_profile.json** - Your skill analysis and learning metrics
- **rules_profile.json** - Your preferences (roles, languages, weights)

### Documentation
- **README.md** - Overview and setup
- **cli/docs/FEEDBACK_SYSTEM.md** - Detailed guide on feedback system
- **cli/docs/QUICK_START.md** - 5-minute onboarding
- **cli/docs/archive/SELF_IMPROVEMENT_IMPLEMENTATION.md** - Technical details

## Key Components Explained

### 1. AI Agent (Optional but Smart)
- Understands natural language queries using LLMs
- Finds semantic matches between your question and problems
- Falls back to rules engine if no API key available

### 2. Rules Engine (Always Works)
- Parses your query for preferences (roles, languages, topics)
- Scores problems based on:
  - **Keyword matching** (60% weight by default)
  - **Role-topic match** (40% weight by default)
  - **Difficulty adjustment** based on target role
  - **Language bonus/penalty**
  - **Feedback adjustments** (boosts weak areas)

### 3. Feedback Engine (The Brain)
- Collects what works and what doesn't
- Builds a profile of your learning
- Identifies:
  - **Strong topics**: Areas you've mastered
  - **Weak topics**: Areas needing practice
  - **Difficulty comfort**: Your sweet spot
  - **Recommendation quality**: How helpful suggestions are
- Provides insights and progression recommendations

## The Self-Improvement Loop

```
Practice Problems
    ↓
Provide Feedback (30 seconds)
    ↓
System Updates Your Profile
    ↓
Next Recommendations are Smarter
    ↓
Practice Better Problems (closer to your needs)
    ↓
[Loop continues, system improves]
```

## Example: A User's Week

```
Day 1:
├─ Start fresh (no skill profile yet)
├─ Get generic recommendations
└─ Solve 2 problems, provide feedback

Day 2:
├─ System identifies: "User is good with arrays"
├─ Recommendations now include more advanced array problems
└─ User gets feedback: "You mastered arrays, try recursion"

Day 3:
├─ User gets 3 recursion problems
├─ Completes 1 (helpful feedback)
├─ Skill profile: recursion weakness = 0.6
└─ Progress tracking: recursion in "weak areas"

Day 4:
├─ Recommendations heavily favor recursion (+30% boost)
├─ User completes 2 more recursion problems
├─ Weakness score drops to 0.4
└─ System recommends: "Time to try medium difficulty!"

Day 5:
├─ Recommendations shift to medium difficulty
├─ User successfully solves medium problems
├─ System detects: "difficulty comfort increasing"
└─ New insight: "Learning velocity: increasing ✅"
```

## Feature Breakdown

### Recommendation Quality
- **Without feedback**: Generic, role/language-aware
- **With 10 feedback entries**: Personalized, weak-area focused
- **With 30+ feedback entries**: Highly tuned to your learning

### Intelligence
- **Keywords**: Matches problem names/topics to your query (100% works)
- **Semantics**: Understands meaning (needs API, +20% better matches)
- **Feedback**: Learns from every interaction (gets better with use)

### Customization
- **Editable Rules**: Change `rules_profile.json` to set defaults
- **Role Profiles**: Different weights for Staff SWE vs SRE
- **Language Focus**: Prioritize certain languages in recommendations

## Privacy & Performance

```
Local Storage:
✅ All data in data/ folder
✅ No cloud sync (except optional AI API)
✅ User controls everything
✅ Can delete anytime

Performance:
✅ Instant keyword matching
✅ Fast rule-based scoring
✅ Optional AI (slower but smarter)
✅ Works offline (without API)
```

## Success Metrics

As you use the system, you'll see:

1. **Completion Rate** ↗️
   - Track: `stats` command
   - More problems completed = better practice

2. **Recommendation Quality** ↗️
   - Track: `insights` command → "Recommendation Helpfulness"
   - Higher % = system understanding you better

3. **Learning Velocity** ↗️
   - Track: `insights` command → "Learning Velocity"
   - "increasing" = you're progressing faster

4. **Skill Profile Clarity** ↗️
   - Track: `insights` command → Strengths/Improvement Areas
   - Clear profile = system knows how to help

---

**The goal:** Every time you practice, provide feedback, and run insights, you're training the system to recommend exactly what you need to improve! 🚀
