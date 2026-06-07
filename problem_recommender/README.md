# AI-Powered Problem Recommender

An intelligent system that recommends coding problems based on your needs, learns from your feedback, and generates new practice problems on-demand with **role-aware difficulty calibration**.

## Features

- 🤖 AI-powered problem matching using natural language queries
- ✨ **Problem Generation** - Create new coding problems dynamically with AI
- 🎯 **Role-Aware Generation** - Auto-calibrate to Junior/Mid/Senior/Principal level
- 🧪 **Automated Testing** - Auto-grade solutions with instant feedback
- 📊 Automatic problem analysis and categorization
- 📈 Progress tracking and performance analytics
- 🧠 **Self-improving system** - Learns from your feedback to improve recommendations
- 🎯 Personalized recommendations based on your skill level and learning progress
- 🧭 Rules engine for role- and language-aware recommendations (editable profile)
- 📝 Detailed insights into your strengths and improvement areas
- 🎓 Smart difficulty progression recommendations
- 🌍 Multi-language support: Java, Python, JavaScript, C#

## Features: Problem Generation

Generate new coding problems on demand:

- **AI-Powered**: Creates unique problems based on your descriptions
- **Multi-Language**: Generate problems for Java, Python, JavaScript, or C#
- **🎯 Role-Aware**: Automatically calibrate difficulty to your career level (Junior → Senior → Principal)
- **Natural Language Role Detection**: "staff swe problem" auto-detects Senior level
- **Adjustable Difficulty**: Choose easy, medium, or hard (or use role default)
- **Test Cases Included**: Each problem comes with test cases and hints
- **File Persistence**: Saves to organized directories with metadata
- **Feedback Integration**: Generated problems integrate with the learning system

See [PROBLEM_GENERATION.md](PROBLEM_GENERATION.md) for detailed documentation.

Architecture and surface-split plan:
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [SERVICE_SPLIT_PLAN.md](SERVICE_SPLIT_PLAN.md)

### Role-Aware Problem Generation

Generate problems tailored to your career level:

```bash
> generate
What problem? > staff swe palindrome checker in java
Detected: STAFF level problem
```

Problems auto-calibrate:
- **Junior**: Fundamentals, basic algorithms
- **Mid**: Design patterns, optimization
- **Senior/Staff**: System design, edge cases, scalability
- **Principal**: Advanced architecture, novel approaches

**Quick Start:** See [ROLE_QUICK_REFERENCE.md](ROLE_QUICK_REFERENCE.md) for quick examples and commands.

**Full Guide:** See [ROLE_AWARE_GENERATION.md](ROLE_AWARE_GENERATION.md) for complete documentation including all role keywords, workflows, and tips.

## Features: Automated Testing

Automatically test your solutions:

- **Multi-Language**: Run tests for Java, Python, JavaScript, C#
- **Instant Feedback**: Get detailed pass/fail results for each test case
- **Performance Tracking**: See execution time for each test
- **Auto-Grading**: 100% pass = completed, partial pass = attempted
- **Integration**: Test results feed into your learning insights
- **Error Details**: Shows exactly what your code produced vs expected

See [TEST_EXECUTION.md](TEST_EXECUTION.md) for detailed documentation.


## Features: Feedback & Self-Improvement

The system continuously learns from your interactions:

- **Collect Feedback**: Rate recommendations as helpful/unhelpful
- **Track Performance**: Log how long problems take and your success rate
- **Build Skill Profile**: System identifies your strengths and weaknesses
- **Adapt Recommendations**: Gets smarter every time you practice
- **Suggest Next Steps**: Recommends when to increase difficulty or focus on weak areas

See [FEEDBACK_SYSTEM.md](FEEDBACK_SYSTEM.md) for detailed documentation.


## Setup

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up GitHub Models access (free tier):
   - Create a GitHub token at https://github.com/settings/tokens
   - Set environment variable: `export GITHUB_TOKEN=your_token_here`

4. Run the recommender:
   ```bash
   python main.py
   ```

## Usage

### Interactive Mode
```bash
python main.py
```

Then ask questions like:
- "I need practice with arrays and loops"
- "Show me easy string manipulation problems"
- "What problems involve recursion?"
- "Targeting Staff SWE/SRE roles; I prefer C# and JavaScript"
- **"Generate a sorting problem in Python"** ← AI-Powered Problem Generation
- **"Create a binary search tree in Java"** ← Natural language generation

**Commands:**
- `stats` - View your progress statistics
- `insights` - View learning insights and improvement recommendations
- `rescan` - Rescan problem files
- `generate` - Create a new problem interactively
- `generated` - List all generated problems
- `test` - Auto-grade your solution with test execution
- `generated` - List all generated problems
- `exit` - Quit

### Command Line Mode
```bash
# Get recommendations
python main.py --query "problems about linked lists"

# Generate a new problem
python main.py --generate "merge sort algorithm in Python"

# List generated problems
python main.py --list-generated
```

## Project Structure

- `main.py` - Entry point and CLI interface
- `problem_generator.py` - AI-powered problem generation for multiple languages
- `feedback_engine.py` - Collects feedback and builds skill profiles
- `ai_agent.py` - AI-powered recommendation engine
- `rules_engine.py` - Rule-based recommendations with feedback integration
- `problem_analyzer.py` - Scans and analyzes the curated Java problem corpus
- `progress_tracker.py` - Tracks problem attempts and completions
- `config.py` - Configuration settings
- `java/` - Curated Java interview problems used by the recommender
- `data/` - Stores all user data (local only, no cloud sync)
- `generated_problems/` - AI-generated practice problems organized by language
- `progress_tracker.py` - Tracks your attempts and progress
- `config.py` - Configuration settings
- `data/` - Stores problem metadata and progress data

## Rules Profile (Optional)

If you want to fine-tune role/language priorities, create `data/rules_profile.json`
and override any defaults in `rules_engine.py`. Example overrides:

```json
{
  "default_roles": ["staff_swe", "sre"],
  "default_languages": ["csharp", "javascript"],
  "roles": {
    "staff_swe": {
      "difficulty_weights": { "easy": 0.6, "medium": 1.0, "hard": 1.4 }
    }
  },
  "language_match_bonus": 0.12
}
```

## License

AGPL-3.0. See `LICENSE`.
