"""
AI Agent for Problem Recommendation
Uses GitHub Models (or OpenAI) to provide intelligent recommendations with feedback integration
"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import GITHUB_TOKEN, MODEL_ENDPOINT, MODEL_NAME
from rules_engine import RulesEngine


class AIAgent:
    def __init__(self, problems: List[Dict[str, Any]], rules_engine: RulesEngine = None, feedback_engine: Optional[Any] = None):
        self.problems = problems
        self.rules_engine = rules_engine
        self.feedback_engine = feedback_engine
        
        # Initialize OpenAI client with GitHub Models endpoint
        if GITHUB_TOKEN:
            self.client = OpenAI(
                base_url=MODEL_ENDPOINT,
                api_key=GITHUB_TOKEN
            )
        else:
            self.client = None
    
    def get_recommendations(self, user_query: str, user_progress: Dict = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get problem recommendations based on user query
        
        Args:
            user_query: Natural language query from user
            user_progress: Dictionary of completed problems
            max_results: Maximum number of recommendations
        
        Returns:
            List of recommended problems with explanations
        """
        # If no AI client is available, use rules-based recommendations
        if not self.client:
            if self.rules_engine:
                return self.rules_engine.recommend(user_query, max_results=max_results)
            return self._fallback_recommendations(user_query, max_results)

        # Prepare context about available problems
        problems_context = self._create_problems_context()
        
        # Create system prompt
        system_prompt = f"""You are an expert coding interview coach helping students find the right practice problems.

Available Problems Database:
{problems_context}

Your task:
1. Understand what the user is looking for
2. Recommend the most relevant problems from the database
3. Explain why each problem is a good match
4. Order recommendations from most to least relevant

Respond ONLY with a JSON array of recommended problems in this format:
[
  {{
    "problem_name": "exact name from database",
    "relevance_score": 0.95,
    "reason": "why this problem matches their needs"
  }}
]
"""
        
        # Add progress context if available
        if user_progress:
            completed = [p for p, data in user_progress.items() if data.get('completed')]
            if completed:
                system_prompt += f"\n\nUser has already completed: {', '.join(completed)}"
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse AI response
            recommendations_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in recommendations_text:
                recommendations_text = recommendations_text.split("```json")[1].split("```")[0].strip()
            elif "```" in recommendations_text:
                recommendations_text = recommendations_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(recommendations_text)
            
            # Match recommendations with full problem data
            results = []
            for rec in recommendations[:max_results]:
                problem = self._find_problem_by_name(rec["problem_name"])
                if problem:
                    results.append({
                        **problem,
                        "relevance_score": rec.get("relevance_score", 0.0),
                        "recommendation_reason": rec.get("reason", "")
                    })
            
            if self.rules_engine:
                return self.rules_engine.apply_rules(results, user_query)
            return results
            
        except Exception as e:
            print(f"Error getting AI recommendations: {e}")
            # Fallback to simple keyword matching
            return self._fallback_recommendations(user_query, max_results)
    
    def _create_problems_context(self) -> str:
        """Create a concise context of all available problems"""
        context_lines = []
        for p in self.problems:
            topics = ", ".join(p.get("topics", []))
            context_lines.append(
                f"- {p['name']} ({p['difficulty']}) | Topics: {topics}"
            )
        return "\n".join(context_lines)
    
    def _find_problem_by_name(self, name: str) -> Dict[str, Any]:
        """Find a problem by its name (case-insensitive partial match)"""
        name_lower = name.lower()
        for problem in self.problems:
            if name_lower in problem['name'].lower() or problem['name'].lower() in name_lower:
                return problem
        return None
    
    def _fallback_recommendations(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simple keyword-based fallback if AI fails"""
        if self.rules_engine:
            return self.rules_engine.recommend(query, max_results=max_results)

        query_lower = query.lower()
        scored_problems = []
        
        for problem in self.problems:
            score = 0
            text = (problem['name'] + ' ' + ' '.join(problem.get('topics', [])) + ' ' + problem.get('description', '')).lower()
            
            # Simple keyword matching
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            if score > 0:
                scored_problems.append({
                    **problem,
                    "relevance_score": score / len(keywords),
                    "recommendation_reason": "Keyword match"
                })
        
        # Sort by score and return top results
        scored_problems.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_problems[:max_results]


if __name__ == "__main__":
    # Test the AI agent
    from problem_analyzer import ProblemAnalyzer
    
    analyzer = ProblemAnalyzer()
    problems = analyzer.load_problems()
    
    agent = AIAgent(problems)
    recommendations = agent.get_recommendations("I need to practice loops and arrays")
    
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"\n{rec['name']} ({rec['difficulty']})")
        print(f"Reason: {rec['recommendation_reason']}")
