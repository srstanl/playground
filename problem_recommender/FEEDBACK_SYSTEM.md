# Feedback & Self-Improvement System Guide

## Overview

The Problem Recommender now has a sophisticated feedback and self-improvement system that learns from your interactions and adapts recommendations over time.

## How It Works

### 1. **Feedback Collection**

After each recommendation, the system can collect feedback:

```
Was 'Java Loops 1' a helpful recommendation? [Y/n]:
How difficult did you find it? [easy/medium/hard/skip]:
```

### 2. **Performance Tracking**

When you mark a problem as completed, provide timing info:

```
Did you successfully solve 'Java Loops 1'? [Y/n]:
How many minutes did it take? (or press Enter to skip): 15
```

### 3. **Skill Profile Building**

The system builds a profile with:
- **Topic Strengths**: Areas where you perform well
- **Topic Weaknesses**: Areas needing improvement
- **Difficulty Comfort**: How comfortable you are with easy/medium/hard problems
- **Recommendation Quality**: How helpful recommendations have been overall

### 4. **Adaptive Recommendations**

Based on your feedback, the system:
- **Boosts weak areas**: Recommends more problems in topics you struggle with
- **Reduces strong areas**: Recommends fewer problems in topics you already master
- **Adjusts difficulty**: Suggests moving to harder/easier problems based on comfort level

## Commands

### `stats` - View Progress
Shows your completion statistics:
- Total problems attempted
- Completed vs in-progress
- Completion rate

### `insights` - View Learning Insights
Shows detailed analysis:
```
📊 Learning Insights
├─ Recommendation Helpfulness: 85%
├─ Learning Velocity: increasing
├─ Strength Areas: [data structures, recursion]
├─ Areas to Improve: [sorting, searching]
└─ Difficulty Comfort Levels
   ├─ Easy: ████████░░ 80%
   ├─ Medium: ██████░░░░ 60%
   └─ Hard: ████░░░░░░ 40%
```

### `rescan` - Update Problem Database
Rescans all Java files and rebuilds the problem database.

## Data Files

The system stores all feedback and profiles locally:

```
data/
├─ problems_db.json          # All scanned problems
├─ progress.json             # Your completion history
├─ feedback_history.json     # All feedback entries
├─ skill_profile.json        # Your skill analysis
└─ rules_profile.json        # Your preference rules
```

All data is stored locally on your machine - nothing is sent to external servers.

## Example Usage Flow

```bash
# 1. Start the recommender
python main.py

# 2. Ask for recommendations
What are you looking for? I need practice with arrays

# 3. System provides recommendations
[Shows 5 recommended problems]

# 4. Mark one as attempted
Select a problem: 1
Action: [attempted/completed/feedback/cancel]: attempted

# 5. Provide feedback
Rate this recommendation? [Y/n]: y
Was 'Java Arrays 1' a helpful recommendation? [Y/n]: y
How difficult did you find it? [easy/medium/hard/skip]: medium

# 6. Continue practicing
What are you looking for? Show me more on recursion

# 7. Check your progress
What are you looking for? insights
[System shows your learning analysis and recommendations]
```

## Self-Improvement in Action

### Example: Learning Data Structures

**Day 1:**
- Complete 3 array problems (solved all)
- Complete 2 linked list problems (struggled)
- Feedback: array problems felt "easy", linked list felt "hard"

**Day 2:**
- System now recommends MORE linked list problems (area needing improvement)
- System REDUCES array recommendations (you've mastered it)
- When you complete a linked list problem, it boosts future linked list recommendations

### Example: Difficulty Progression

**Week 1:**
- Complete 5 easy problems (100% success)
- Comfort level: Easy → 80%

**Week 2:**
- System recommends medium problems
- You complete 3 (80% success)
- Comfort level: Medium → 60%

**Week 3:**
- System suggests "Time to challenge yourself with harder problems!"
- Comfort level: Hard → starts tracking

## Tips for Best Results

1. **Be consistent with feedback** - The more feedback you provide, the better recommendations become
2. **Track timing** - Helps the system understand which topics take you longer (might indicate need for more practice)
3. **Provide honest ratings** - Mark recommendations as helpful/unhelpful for accurate learning
4. **Review insights regularly** - Check `insights` command to see your progress and improvement areas
5. **Follow recommendations** - If the system suggests moving to harder problems, give it a try!

## Advanced: Customizing Rules

You can customize the recommendation engine by editing `data/rules_profile.json`:

```json
{
  "roles": {
    "staff_swe": {
      "difficulty_weights": {"easy": 0.7, "medium": 1.0, "hard": 1.3},
      "topic_weights": {
        "data structures": 1.2,
        "recursion": 1.1
      }
    }
  },
  "languages": {
    "csharp": ["c#", "c sharp"],
    "javascript": ["javascript", "js"]
  },
  "default_roles": ["staff_swe"],
  "default_languages": ["csharp"]
}
```

## Privacy

All data is stored locally in the `data/` directory. No information is sent to external services except:
- GitHub Models API (if using AI recommendations with GitHub token)
- OpenAI API (if you choose to use that instead)

You control what data is collected and can delete the `data/` directory anytime to reset.
