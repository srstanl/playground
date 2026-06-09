# Quick Start: Feedback & Self-Improvement

## 30-Second Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set GitHub token** (optional, but recommended)
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

3. **Run the app**
   ```bash
   python3 cli/main.py
   ```

## Your First Session (5 minutes)

```bash
$ python3 cli/main.py
[System initializes with your problems]

What are you looking for?
> I need practice with arrays

[System recommends 5 array problems]

Select a problem: 1
Action: [attempted/completed/feedback/cancel]: completed

Did you successfully solve 'Java Arrays Basics'? [Y/n]: y
How many minutes did it take? (or press Enter to skip): 12

Rate this recommendation? [Y/n]: y
Was 'Java Arrays Basics' a helpful recommendation? [Y/n]: y
How difficult did you find it? [easy/medium/hard/skip]: medium

✓ Feedback recorded! The system just learned something about you!

What are you looking for?
> insights

[Shows your learning dashboard...]
```

## The Learning Flow

### First Few Sessions
- You provide feedback on recommendations
- System builds initial understanding of your level
- Insights might be limited ("building" velocity)

### After 10-15 problems
- System has solid data about your strengths
- Recommendations become more personalized
- Insights show clear patterns

### After 30+ problems
- System knows your weak areas
- Recommendations focus on those areas
- You see "increasing" learning velocity
- Difficulty recommendations appear

## Commands You'll Use

| Command | Purpose | When to Use |
|---------|---------|-----------|
| (ask question) | Get recommendations | You want to practice something |
| `stats` | View progress | Track completion rate |
| `insights` | See skill analysis | Understand your progress |
| `rescan` | Update problem list | After adding new problems |
| `feedback` | Rate a problem | When asked, or anytime |
| `exit` | Quit | When done |

## What Happens Behind the Scenes

```
Your Feedback
    ↓
feedback_history.json (logged)
    ↓
skill_profile.json (analyzed)
    ↓
Next Recommendations (smarter!)
```

## Pro Tips

1. **Be consistent with feedback**
   - Every time you complete something, log it
   - Takes 30 seconds, helps a ton

2. **Track your time**
   - Tells system which topics are harder for you
   - Helps identify areas needing more practice

3. **Rate recommendations honestly**
   - Even if they weren't helpful - that data is valuable!
   - System learns what works for you

4. **Check insights weekly**
   - See your progress visualized
   - Get recommended difficulty adjustments

5. **Follow the system's advice**
   - When it suggests harder problems, try them
   - When it suggests focusing on weak areas, do it
   - The recommendations get better as you practice

## Understanding Your Insights

```
📊 Learning Insights

💡 Recommendation: Time to challenge yourself with medium difficulty!
   ↑ This means: You're crushing easy problems, ready for more challenge

Arrays ████████░░ 80%
   ↑ Your strength area - you've mastered this topic

Recursion ██░░░░░░░░ 20%
   ↑ Your improvement area - more practice needed

Recommendation Helpfulness: 85%
   ↑ 85% of recommended problems have been helpful
```

## Data Stored Locally

Everything is on your machine in `data/`:
- Your feedback history
- Your skill profile
- Your progress tracking
- Your preferences

**Nothing goes to the cloud** (unless you use an AI API key, which is optional).

## Troubleshooting

**Q: Recommendations don't seem personalized yet**
A: You need 10+ feedback entries. The system learns from data!

**Q: How do I reset my profile?**
A: Delete the `data/` folder and restart. Fresh start!

**Q: Can I export my progress?**
A: Check `data/progress.json` and `data/feedback_history.json` - they're plain JSON.

**Q: Do I need the AI token?**
A: No! The rules engine works without it. AI just makes recommendations smarter.

## Next Level

Once you're comfortable with basic usage:

1. **Customize Rules**: Edit `data/rules_profile.json` to set default role/languages
2. **Analyze Patterns**: Look at `feedback_history.json` to see your learning patterns
3. **Set Goals**: Use insights to guide what to practice next

---

**That's it!** Start practicing, provide feedback, and watch the recommendations get smarter! 🚀
