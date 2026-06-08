# Problem Generation Setup Guide

This guide walks you through setting up the AI-powered problem generation feature.

## Prerequisites

✅ Python 3.8 or higher  
✅ Virtual environment activated (`source venv/bin/activate`)  
✅ Dependencies installed (`pip install -r requirements.txt`)

## API Setup Options

You have two options for AI provider:

### Option 1: GitHub Models (Recommended - FREE)

GitHub Models offers free tier access to GPT-4o-mini - perfect for this project!

1. **Get a GitHub Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a name: "Problem Generator"
   - Select scopes:
     - ✅ `read:user`
     - ✅ `read:org` (if applicable)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Set the environment variable**:

   **Temporary (current session only)**:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

   **Permanent (recommended)**:
   ```bash
   # Add to ~/.zshrc (macOS) or ~/.bashrc (Linux)
   echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Verify**:
   ```bash
   echo $GITHUB_TOKEN
   ```
   Should print your token.

### Option 2: OpenAI API (Paid)

If you prefer using OpenAI directly:

1. **Get an API key**:
   - Go to: https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key

2. **Set the environment variable**:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. **Update config.py**:
   Uncomment these lines in `config.py`:
   ```python
   # Alternative: OpenAI API (if you have access)
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   ```

4. **Update problem_generator.py**:
   Modify the initialization to use OpenAI:
   ```python
   # In ProblemGenerator.__init__()
   if OPENAI_API_KEY:
       self.client = OpenAI(api_key=OPENAI_API_KEY)
   elif GITHUB_TOKEN:
       self.client = OpenAI(
           base_url=MODEL_ENDPOINT,
           api_key=GITHUB_TOKEN
       )
   ```

## Quick Test

After setting up your API:

```bash
# Activate virtual environment
source venv/bin/activate

# Run integration tests
python3 tests/test_integration.py

# If tests pass, try generating a problem
python3 cli/main.py
```

In interactive mode, type:
```
generate
```

## Troubleshooting

### "Client should be initialized" error
- Check that your API key is set: `echo $GITHUB_TOKEN` or `echo $OPENAI_API_KEY`
- Verify you're in the correct shell (zsh vs bash)
- Restart your terminal after adding to ~/.zshrc

### API returns 401/403 errors
- Verify your token has correct permissions
- Check if token has expired (regenerate if needed)
- Ensure you're using the correct endpoint

### Generation times out
- Check your internet connection
- GitHub Models may have rate limits - wait a few seconds and retry
- Consider switching to OpenAI API for faster responses

### "Module not found" errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Costs

### GitHub Models (Option 1)
- **FREE** for personal use
- Rate limited to prevent abuse
- Recommended for development and learning

### OpenAI API (Option 2)
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Typical problem generation: ~2,000 tokens (~$0.002 per problem)
- Budget-friendly for occasional use

## Security Best Practices

🔒 **Never commit API keys to Git**:
```bash
# Already in .gitignore:
.env
*.env
```

🔒 **Use environment variables** (not hardcoded keys)

🔒 **Rotate tokens periodically** (every 90 days recommended)

🔒 **Use minimal permissions** needed for the task

## Next Steps

Once API is configured:

1. ✅ Run `python3 tests/test_integration.py` - Should pass all tests
2. ✅ Run `python3 cli/main.py` - Start interactive mode
3. ✅ Type `generate` - Create your first problem
4. ✅ Check `generated_questions/<language>/` - Verify files were created
5. ✅ Type `generated` - List all generated problems
6. ✅ Type `insights` - See your learning progress

## Need Help?

- Check the [cli/docs/PROBLEM_GENERATION.md](cli/docs/PROBLEM_GENERATION.md) for detailed usage guide
- Review [cli/docs/TESTING_GENERATION.md](cli/docs/TESTING_GENERATION.md) for test scenarios
- See [README.md](README.md) for overall project documentation

---

**Ready to generate problems?** Run `python3 cli/main.py` and type `generate`! 🚀
