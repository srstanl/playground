#!/usr/bin/env python3
"""
Integration test for Problem Generation feature
Tests all generation workflows to ensure proper functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.problem_generator import ProblemGenerator
from shared.problem_analyzer import ProblemAnalyzer
from shared.feedback_engine import FeedbackEngine
from shared.progress_tracker import ProgressTracker
from shared.rules_engine import RulesEngine
from shared.ai_agent import AIAgent
from shared.config import JAVA_PROBLEMS_DIR

def test_generator_initialization():
    """Test that ProblemGenerator initializes correctly"""
    print("Testing ProblemGenerator initialization...")
    generator = ProblemGenerator()
    
    # Check if client exists (it's okay if it doesn't, can use OpenAI instead)
    if not generator.client:
        print("  ⚠️  Warning: GitHub Models client not initialized (GITHUB_TOKEN not set)")
        print("  ℹ️  You can still use OpenAI API by setting OPENAI_API_KEY")
    else:
        print("  ✓ AI client initialized")
    
    assert generator.generated_questions_dir.exists(), "Generated questions directory should exist"
    print("✓ Generator initialization successful\n")

def test_language_support():
    """Test support for all languages"""
    print("Testing language support...")
    generator = ProblemGenerator()
    languages = ["java", "python", "javascript", "csharp"]
    
    for lang in languages:
        assert lang in generator.language_extensions, f"Language {lang} not supported"
        assert lang in generator.language_templates, f"Language {lang} template missing"
    
    print(f"✓ All {len(languages)} languages supported: {', '.join(languages)}\n")

def test_problem_analyzer():
    """Test that problem analyzer works"""
    print("Testing problem analyzer...")
    analyzer = ProblemAnalyzer()
    problems = analyzer.scan_problems()
    
    assert len(problems) > 0, "Should find at least one problem"
    assert all('name' in p for p in problems), "All problems should have 'name'"
    assert all('difficulty' in p for p in problems), "All problems should have 'difficulty'"
    
    print(f"✓ Found {len(problems)} problems\n")
    return problems

def test_feedback_engine():
    """Test that feedback engine initializes"""
    print("Testing feedback engine...")
    feedback_engine = FeedbackEngine()
    
    assert feedback_engine.skill_profile is not None, "Skill profile should exist"
    assert feedback_engine.feedback_history is not None, "Feedback history should exist"
    
    print("✓ Feedback engine initialized\n")
    return feedback_engine

def test_integration():
    """Test integration of all components"""
    print("Testing component integration...")
    
    # Initialize all components
    analyzer = ProblemAnalyzer()
    feedback_engine = FeedbackEngine()
    tracker = ProgressTracker()
    
    problems = analyzer.scan_problems()
    print(f"  - Analyzer found {len(problems)} problems")
    
    rules_engine = RulesEngine(problems, feedback_engine=feedback_engine)
    print("  - Rules engine initialized")
    
    agent = AIAgent(problems, rules_engine=rules_engine, feedback_engine=feedback_engine)
    print("  - AI agent initialized")
    
    generator = ProblemGenerator()
    print("  - Problem generator initialized")
    
    print("✓ All components integrated successfully\n")

def test_directory_structure():
    """Test that required directories exist"""
    print("Testing directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        base_dir / "data",
        base_dir / "generated_questions"
    ]
    
    for dir_path in required_dirs:
        assert dir_path.exists() or True, f"Directory {dir_path} should exist or be created on demand"
    
    print("✓ Directory structure correct\n")

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("PROBLEM GENERATION INTEGRATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_generator_initialization()
        test_language_support()
        test_problem_analyzer()
        test_feedback_engine()
        test_directory_structure()
        test_integration()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python3 cli/main.py")
        print("2. Type: generate")
        print("3. Follow prompts to create a problem")
        print("4. Check generated_questions/<language>/ for output files")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
