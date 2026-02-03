#!/usr/bin/env python3
"""
AI-Powered Problem Recommender
Main entry point and interactive interface with feedback and self-improvement
"""
import argparse
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from problem_analyzer import ProblemAnalyzer
from ai_agent import AIAgent
from progress_tracker import ProgressTracker
from rules_engine import RulesEngine
from feedback_engine import FeedbackEngine
from problem_generator import ProblemGenerator
from test_executor import TestExecutor


console = Console()


class ProblemRecommender:
    def __init__(self):
        console.print("[bold blue]Initializing Problem Recommender...[/bold blue]")
        
        # Initialize components
        self.analyzer = ProblemAnalyzer()
        self.tracker = ProgressTracker()
        self.feedback_engine = FeedbackEngine()
        self.generator = ProblemGenerator()
        self.test_executor = TestExecutor()
        
        # Load or scan problems
        console.print("📚 Loading problems database...")
        self.problems = self.analyzer.load_problems()
        console.print(f"✓ Found {len(self.problems)} problems\n")
        
        # Initialize rules engine with feedback
        self.rules_engine = RulesEngine(self.problems, feedback_engine=self.feedback_engine)
        try:
            self.agent = AIAgent(self.problems, rules_engine=self.rules_engine, feedback_engine=self.feedback_engine)
            if self.agent.client:
                console.print("✓ AI agent initialized (rules & feedback-enhanced)\n")
            else:
                console.print("[yellow]AI token not found; using rules engine only.[/yellow]\n")
        except Exception as e:
            console.print(f"[red]AI agent disabled: {e}[/red]")
            console.print("[yellow]Falling back to rules engine only.[/yellow]\n")
            self.agent = None
    
    def show_welcome(self):
        """Display welcome message"""
        welcome = """
# 🎯 AI-Powered Problem Recommender with Self-Improvement & Generation

Ask me anything like:
- "I need practice with arrays and loops"
- "Show me easy string problems"
- "What problems involve recursion?"
- "Problems similar to two sum"
- "Targeting Staff SWE/SRE roles; I prefer C# and JavaScript"

Generate New Problems:
- "Generate a hard sorting problem in C#"
- "Create a medium graph problem in Python"
- "Generate easy JavaScript problem about arrays"

Commands:
- `generate` - Generate a new problem
- `generated` - View generated problems
- `test` - Run tests on your solution
- `stats` - View your progress statistics
- `insights` - View your learning insights & improvement areas
- `rescan` - Rescan problem files
- `exit` - Quit the program

💡 The more you use it and provide feedback, the smarter it gets!
💻 Use `test` command to automatically grade your solutions!
"""
        console.print(Panel(Markdown(welcome), border_style="blue"))
    
    def interactive_mode(self):
        """Run in interactive mode"""
        self.show_welcome()
        
        while True:
            try:
                query = Prompt.ask("\n[bold cyan]What are you looking for?[/bold cyan]")
                
                if not query:
                    continue
                
                query_lower = query.lower().strip()
                
                # Handle commands
                if query_lower in ["exit", "quit", "q"]:
                    console.print("[green]Happy coding! 👋[/green]")
                    break
                elif query_lower == "stats":
                    self.show_stats()
                    continue
                elif query_lower == "insights":
                    self.show_insights()
                    continue
                elif query_lower == "rescan":
                    self.rescan_problems()
                    continue
                elif query_lower == "generate":
                    self.generate_problem_interactive()
                    continue
                elif query_lower == "generated":
                    self.show_generated_problems()
                    continue
                elif query_lower == "test":
                    self.run_test_interactive()
                    continue
                
                # Check if user is asking to generate
                if any(word in query_lower for word in ["generate", "create", "make", "new problem"]):
                    if Confirm.ask("[cyan]Generate a new problem?[/cyan]", default=True):
                        self.generate_problem_interactive(query)
                        continue
                
                # Get AI recommendations
                self.get_and_display_recommendations(query)
                
            except KeyboardInterrupt:
                console.print("\n[green]Goodbye! 👋[/green]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def get_and_display_recommendations(self, query: str):
        """Get recommendations and display them"""
        console.print("\n[yellow]🤔 Thinking...[/yellow]")
        
        # Get recommendations from AI
        if self.agent:
            recommendations = self.agent.get_recommendations(
                query,
                self.tracker.progress,
                max_results=5
            )
        else:
            recommendations = self.rules_engine.recommend(query, max_results=5)
        
        if not recommendations:
            console.print("[red]No matching problems found. Try a different query.[/red]")
            return
        
        # Display recommendations
        console.print(f"\n[bold green]✨ Found {len(recommendations)} recommendations:[/bold green]\n")
        
        for i, rec in enumerate(recommendations, 1):
            status = self.tracker.get_problem_status(rec['name'])
            status_icon = "✅" if status.get('completed') else "🔄" if status.get('attempts', 0) > 0 else "⭐"
            
            # Create problem card
            header = f"{status_icon} {i}. {rec['name']}"
            
            content = []
            content.append(f"[bold]Difficulty:[/bold] {rec['difficulty'].capitalize()}")
            content.append(f"[bold]Topics:[/bold] {', '.join(rec.get('topics', []))}")
            content.append(f"[bold]Relevance:[/bold] {rec.get('relevance_score', 0):.0%}")
            content.append(f"\n[italic]{rec.get('recommendation_reason', '')}[/italic]")
            content.append(f"\n[dim]File: {rec['file_path']}[/dim]")
            
            if status.get('attempts', 0) > 0:
                content.append(f"[dim]Attempts: {status['attempts']}[/dim]")
            
            console.print(Panel(
                "\n".join(content),
                title=header,
                border_style="green" if status.get('completed') else "yellow" if status.get('attempts', 0) > 0 else "blue"
            ))
        
        # Ask if they want to mark any as attempted
        if Confirm.ask("\n[cyan]Would you like to mark any problem as attempted/completed?[/cyan]", default=False):
            self.update_progress(recommendations)
    
    def update_progress(self, recommendations):
        """Update progress and gather feedback for a problem"""
        # Show options
        console.print("\n[bold]Select a problem:[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"{i}. {rec['name']}")
        console.print("0. Cancel")
        
        choice = Prompt.ask("Enter number", default="0")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            if 1 <= choice_num <= len(recommendations):
                problem = recommendations[choice_num - 1]
                action = Prompt.ask(
                    "Action",
                    choices=["attempted", "completed", "feedback", "cancel"],
                    default="attempted"
                )
                
                if action == "attempted":
                    self.tracker.mark_attempted(problem['name'])
                    console.print(f"[green]✓ Marked '{problem['name']}' as attempted[/green]")
                    # Ask for quick feedback
                    if Confirm.ask("[cyan]Rate this recommendation?[/cyan]", default=True):
                        self.collect_feedback(problem)
                        
                elif action == "completed":
                    self.tracker.mark_completed(problem['name'])
                    console.print(f"[green]🎉 Marked '{problem['name']}' as completed![/green]")
                    # Gather detailed feedback on completion
                    self.collect_completion_feedback(problem)
                    
                elif action == "feedback":
                    self.collect_feedback(problem)
        except ValueError:
            console.print("[red]Invalid choice[/red]")
    
    def collect_feedback(self, problem: Dict):
        """Collect feedback on a recommendation"""
        helpful = Confirm.ask(f"[cyan]Was '{problem['name']}' a helpful recommendation?[/cyan]")
        
        difficulty = Prompt.ask(
            "[cyan]How difficult did you find it?[/cyan]",
            choices=["easy", "medium", "hard", "skip"],
            default="skip"
        )
        
        if difficulty != "skip":
            self.feedback_engine.record_recommendation_feedback(
                problem['name'],
                helpful=helpful,
                difficulty_felt=difficulty
            )
            console.print("[green]✓ Feedback recorded![/green]")
    
    def collect_completion_feedback(self, problem: Dict):
        """Collect detailed feedback after problem completion"""
        solved = Confirm.ask(f"[cyan]Did you successfully solve '{problem['name']}'?[/cyan]", default=True)
        
        time_spent = Prompt.ask(
            "[cyan]How many minutes did it take? (or press Enter to skip)[/cyan]",
            default=""
        )
        
        if time_spent:
            try:
                time_minutes = int(time_spent)
                self.feedback_engine.record_problem_completion(
                    problem['name'],
                    solved=solved,
                    time_spent_minutes=time_minutes,
                    topics=problem.get('topics', [])
                )
                console.print("[green]✓ Completion feedback recorded![/green]")
            except ValueError:
                console.print("[yellow]Invalid time input[/yellow]")
    
    def show_stats(self):
        """Display progress statistics"""
        stats = self.tracker.get_stats()
        
        table = Table(title="📊 Your Progress", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Total Problems Attempted", str(stats['total_attempted']))
        table.add_row("Completed", str(stats['completed']))
        table.add_row("In Progress", str(stats['in_progress']))
        table.add_row("Completion Rate", f"{stats['completion_rate']:.1f}%")
        
        console.print("\n")
        console.print(table)
        
        # Show recent activity
        completed = self.tracker.get_completed_problems()
        if completed:
            console.print(f"\n[bold green]Recently Completed:[/bold green]")
            for problem in completed[-5:]:  # Last 5
                console.print(f"  ✅ {problem}")
    
    def show_insights(self):
        """Display learning insights and skill analysis"""
        insights = self.feedback_engine.get_learning_insights()
        
        console.print("\n")
        
        # Overall stats
        table = Table(title="🧠 Learning Insights", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Total Feedback Given", str(insights['total_recommendations_rated']))
        table.add_row("Recommendation Helpfulness", insights['recommendation_helpfulness'])
        table.add_row("Learning Velocity", insights['learning_velocity'].capitalize())
        
        console.print(table)
        
        # Strength areas
        strengths = insights['strength_areas']
        if strengths:
            console.print("\n[bold green]💪 Your Strengths:[/bold green]")
            for topic, score in strengths:
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                console.print(f"  {topic.capitalize():<20} {bar} {score:.0%}")
        
        # Areas needing improvement
        improvements = insights['improvement_areas']
        if improvements:
            console.print("\n[bold yellow]🎯 Areas to Improve:[/bold yellow]")
            for topic, score in improvements:
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                console.print(f"  {topic.capitalize():<20} {bar} {score:.0%}")
        
        # Difficulty comfort levels
        difficulty_comfort = insights['comfort_levels']
        console.print("\n[bold blue]📈 Difficulty Comfort Levels:[/bold blue]")
        for level, comfort in difficulty_comfort.items():
            bar = "█" * int(comfort * 10) + "░" * (10 - int(comfort * 10))
            console.print(f"  {level.capitalize():<10} {bar} {comfort:.0%}")
        
        # Recommendation for next steps
        difficulty_adjust = self.feedback_engine.should_adjust_difficulty()
        console.print("\n[bold magenta]💡 Recommendation:[/bold magenta]")
        if difficulty_adjust == "easy":
            console.print("  → You're struggling with current problems. Try starting with easier problems to build confidence!")
        elif difficulty_adjust == "medium":
            console.print("  → You're doing great with easy problems! Time to challenge yourself with medium difficulty.")
        elif difficulty_adjust == "hard":
            console.print("  → Excellent! You're ready for hard problems. Keep pushing your limits!")
        elif difficulty_adjust == "stick":
            console.print("  → You're crushing hard problems! Keep these challenging problems coming.")
        else:
            console.print("  → Keep practicing with a mix of difficulties to build well-rounded skills.")
    
    def rescan_problems(self):
        """Rescan problem files"""
        console.print("[yellow]Rescanning problem files...[/yellow]")
        self.problems = self.analyzer.scan_problems()
        self.rules_engine = RulesEngine(self.problems, feedback_engine=self.feedback_engine)
        self.agent = AIAgent(self.problems, rules_engine=self.rules_engine, feedback_engine=self.feedback_engine)
        console.print(f"[green]✓ Found {len(self.problems)} problems[/green]")
    
    def generate_problem_interactive(self, initial_query: str = ""):
        """Interactive problem generation with role context"""
        console.print("\n[bold cyan]🤖 Problem Generator with Role Context[/bold cyan]")
        
        # Get problem description
        if initial_query and any(word in initial_query.lower() for word in ["generate", "create"]):
            # Extract the actual request
            description = initial_query
        else:
            description = Prompt.ask("[cyan]What kind of problem do you want to create?[/cyan]\n[dim](e.g., 'staff swe palindrome problem', 'junior sorting', 'mid-level binary search')[/dim]")
        
        # Auto-detect role from description
        detected_role, clean_description = self.generator.detect_role(description)
        
        # Show detected role or ask to override
        console.print(f"\n[yellow]Detected: {detected_role.upper()} level problem[/yellow]")
        override_role = Confirm.ask("[cyan]Keep this role?[/cyan]", default=True)
        
        if not override_role:
            role = Prompt.ask(
                "[cyan]Select role[/cyan]",
                choices=["junior", "mid", "senior", "principal"],
                default=detected_role
            )
        else:
            role = detected_role
        
        # Get language
        language = Prompt.ask(
            "[cyan]Language[/cyan]",
            choices=["java", "csharp", "javascript", "python"],
            default="java"
        )
        
        # Role automatically determines difficulty, but allow override
        role_config = self.generator.role_definitions[role]
        default_difficulty = role_config["default_difficulty"]
        override_difficulty = Confirm.ask(f"[cyan]Use default difficulty ({default_difficulty}) for {role}?[/cyan]", default=True)
        
        if override_difficulty:
            difficulty = default_difficulty
        else:
            difficulty = Prompt.ask(
                "[cyan]Difficulty[/cyan]",
                choices=["easy", "medium", "hard"],
                default="medium"
            )
        
        console.print("\n[yellow]Generating problem...[/yellow]")
        
        problem = self.generator.generate_problem(description, language, difficulty, role)
        
        if problem:
            console.print("\n[bold green]✨ Problem Generated![/bold green]\n")
            
            # Display problem with role context
            console.print(f"[bold cyan]{problem['title']}[/bold cyan]")
            role_badge = f"👤 {problem.get('role', 'mid').upper()}"
            console.print(f"[dim]{role_badge} | Difficulty: {problem['difficulty']} | Language: {language.upper()} | Topics: {', '.join(problem.get('topics', []))}[/dim]\n")
            
            if problem.get('role_context'):
                console.print(f"[cyan]Why this matters:[/cyan] {problem['role_context']}\n")
            
            console.print(f"[white]{problem['description']}[/white]\n")
            
            # Show test cases
            if problem.get('test_cases'):
                console.print("[bold]Test Cases:[/bold]")
                for i, tc in enumerate(problem['test_cases'][:2], 1):
                    console.print(f"  {i}. Input: {tc.get('input')}")
                    console.print(f"     Output: {tc.get('expected_output')}")
                    console.print(f"     Explanation: {tc.get('explanation')}\n")
            
            # Show hints
            if problem.get('hints'):
                console.print("[bold]Hints:[/bold]")
                for i, hint in enumerate(problem['hints'], 1):
                    console.print(f"  {i}. {hint}")
            
            console.print(f"\n[dim]📁 Saved to: {problem['file_path']}[/dim]")
            
            # Ask if they want to work on it
            if Confirm.ask("\n[cyan]Mark this as attempted?[/cyan]", default=True):
                self.tracker.mark_attempted(problem['title'])
                console.print(f"[green]✓ Marked as attempted[/green]")
        else:
            console.print("[red]Failed to generate problem[/red]")
    
    def show_generated_problems(self):
        """Display all generated problems with role context"""
        generated = self.generator.list_generated_problems()
        
        if not generated:
            console.print("[yellow]No generated problems yet.[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Generated Problems ({len(generated)})[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan")
        table.add_column("Role", style="blue")
        table.add_column("Difficulty", style="yellow")
        table.add_column("Language", style="green")
        table.add_column("Topics", style="blue")
        
        for problem in generated:
            topics = ", ".join(problem.get('topics', [])[:2])
            table.add_row(
                problem.get('title', 'Unknown'),
                problem.get('role', 'mid').upper(),
                problem.get('difficulty', 'medium').upper(),
                problem.get('language', 'java').upper(),
                topics
            )
        
        console.print(table)
        
        # Option to work on one
        if Confirm.ask("\n[cyan]Work on one of these problems?[/cyan]", default=False):
            choice = Prompt.ask("Enter problem title (or press Enter to skip)", default="")
            if choice:
                for problem in generated:
                    if problem['title'].lower() == choice.lower():
                        self.tracker.mark_attempted(problem['title'])
                        console.print(f"[green]✓ Starting: {problem['title']}[/green]")
                        console.print(f"[dim]File: {problem['file_path']}[/dim]")
                        break
    
    def run_test_interactive(self):
        """Run tests on a solution interactively"""
        console.print("\n[bold cyan]🧪 Test Executor[/bold cyan]")
        
        # Get solution file path
        file_path = Prompt.ask("[cyan]Enter path to your solution file[/cyan]")
        file_path = Path(file_path).expanduser()
        
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        # Get language
        language = Prompt.ask(
            "[cyan]Programming language[/cyan]",
            choices=["java", "python", "javascript", "csharp", "c#"],
            default="python"
        )
        
        # Load test cases - check if this is a generated problem
        test_cases = []
        problem_name = Prompt.ask("[cyan]Problem name (or enter to skip)[/cyan]", default="")
        
        if problem_name:
            # Try to find problem in generated problems
            generated = self.generator.list_generated_problems()
            for problem in generated:
                if problem_name.lower() in problem['title'].lower():
                    test_cases = problem.get('test_cases', [])
                    break
        
        if not test_cases:
            # Ask user to provide test cases manually
            console.print("[yellow]No test cases found. Provide test cases:[/yellow]")
            console.print("Format: input | expected_output | explanation")
            
            while True:
                test_input = Prompt.ask("Input (or 'done' to finish)", default="")
                if test_input.lower() == "done":
                    break
                
                expected = Prompt.ask("Expected output")
                explanation = Prompt.ask("Explanation (optional)", default="")
                
                test_cases.append({
                    "input": test_input,
                    "expected_output": expected,
                    "explanation": explanation
                })
        
        if not test_cases:
            console.print("[yellow]No test cases provided. Aborting.[/yellow]")
            return
        
        # Run tests
        console.print("\n[yellow]Running tests...[/yellow]")
        summary = self.test_executor.execute_solution(
            str(file_path),
            test_cases,
            language
        )
        
        # Display results
        feedback = self.test_executor.get_detailed_feedback(summary)
        console.print(feedback)
        
        # Record test results in feedback system
        if summary.compilation_error:
            self.feedback_engine.record_recommendation_feedback(
                problem_name,
                "failure",
                f"Compilation error: {summary.compilation_error}"
            )
        else:
            quality_score = summary.success_rate / 100.0
            self.feedback_engine.record_recommendation_feedback(
                problem_name,
                "success" if summary.success_rate == 100 else "partial",
                f"{summary.passed_tests}/{summary.total_tests} tests passed"
            )
        
        # Ask if they want to mark as completed
        if summary.success_rate == 100:
            if Confirm.ask("\n[cyan]Mark as completed?[/cyan]", default=True):
                self.tracker.mark_completed(problem_name)
                console.print("[green]🎉 Problem completed![/green]")
        elif summary.passed_tests > 0:
            if Confirm.ask("\n[cyan]Mark as attempted?[/cyan]", default=True):
                self.tracker.mark_attempted(problem_name)
                console.print("[green]✓ Marked as attempted[/green]")

    def command_line_mode(self, query: str):
        """Run a single query from command line"""
        self.get_and_display_recommendations(query)


def main():
    parser = argparse.ArgumentParser(description="AI-Powered Problem Recommender")
    parser.add_argument("--query", "-q", type=str, help="Query for recommendations (non-interactive)")
    parser.add_argument("--generate", "-g", type=str, help="Generate a new problem (e.g., --generate 'sorting problem in Python')")
    parser.add_argument("--list-generated", action="store_true", help="List all generated problems")
    args = parser.parse_args()
    
    recommender = ProblemRecommender()
    
    if args.generate:
        console.print("[bold cyan]🤖 Problem Generator[/bold cyan]\n")
        problem = recommender.generator.generate_problem(args.generate, "python", "medium")
        if problem:
            console.print(f"[bold green]✓ Generated: {problem['title']}[/bold green]")
            console.print(f"[dim]File: {problem['file_path']}[/dim]")
        else:
            console.print("[red]Failed to generate problem[/red]")
    elif args.list_generated:
        recommender.show_generated_problems()
    elif args.query:
        recommender.command_line_mode(args.query)
    else:
        recommender.interactive_mode()


if __name__ == "__main__":
    main()
