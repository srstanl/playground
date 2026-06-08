import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
JAVA_PROBLEMS_DIR = BASE_DIR / "java"
GENERATED_PROBLEMS_DIR = BASE_DIR / "generated_problems"
DATA_DIR = BASE_DIR / "data"
PROBLEMS_DB_FILE = DATA_DIR / "problems_db.json"
PROGRESS_FILE = DATA_DIR / "progress.json"
RULES_PROFILE_FILE = DATA_DIR / "rules_profile.json"

# AI Model Configuration
# GitHub Models (free tier) - using GPT-4o-mini
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o-mini"

# Alternative: OpenAI API (if you have access)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL_NAME = "gpt-4o-mini"

# Problem Analysis Settings
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
MAX_RECOMMENDATIONS = 5

# Ensure local writable directories exist
JAVA_PROBLEMS_DIR.mkdir(exist_ok=True)
GENERATED_PROBLEMS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
