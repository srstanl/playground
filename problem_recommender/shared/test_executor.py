"""
Test Executor Engine
Automatically runs solutions against test cases for Java, Python, JavaScript, C#
Provides detailed feedback on correctness and performance
"""

import json
import subprocess
import tempfile
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a single test case"""
    test_number: int
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    execution_time: float
    error: Optional[str] = None
    explanation: str = ""


@dataclass
class ExecutionSummary:
    """Summary of all test executions"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    success_rate: float
    results: List[TestResult]
    compilation_error: Optional[str] = None
    runtime_error: Optional[str] = None


class TestExecutor:
    """Executes code against test cases for multiple languages"""
    
    def __init__(self):
        self.supported_languages = {
            "java": {"ext": ".java", "compile": True},
            "python": {"ext": ".py", "compile": False},
            "javascript": {"ext": ".js", "compile": False},
            "csharp": {"ext": ".cs", "compile": True},
            "c#": {"ext": ".cs", "compile": True},
        }
    
    def execute_solution(self, 
                        code_path: str, 
                        test_cases: List[Dict[str, Any]],
                        language: str,
                        timeout: int = 10) -> ExecutionSummary:
        """
        Execute code against test cases
        
        Args:
            code_path: Path to the solution file
            test_cases: List of test cases with 'input', 'expected_output', 'explanation'
            language: Programming language (java, python, javascript, csharp)
            timeout: Maximum execution time per test in seconds
            
        Returns:
            ExecutionSummary with all test results
        """
        language = language.lower()
        
        if language not in self.supported_languages:
            return ExecutionSummary(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                total_time=0,
                success_rate=0,
                results=[],
                compilation_error=f"Unsupported language: {language}"
            )
        
        code_path = Path(code_path)
        if not code_path.exists():
            return ExecutionSummary(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                total_time=0,
                success_rate=0,
                results=[],
                compilation_error=f"File not found: {code_path}"
            )
        
        # Read the code
        with open(code_path, 'r') as f:
            code = f.read()
        
        # Prepare execution environment
        results = []
        total_time = 0
        compilation_error = None
        
        if self.supported_languages[language]["compile"]:
            # Compile if needed
            compile_error, compiled_path = self._compile(code, language, code_path.parent)
            if compile_error:
                return ExecutionSummary(
                    total_tests=len(test_cases),
                    passed_tests=0,
                    failed_tests=len(test_cases),
                    total_time=0,
                    success_rate=0,
                    results=[],
                    compilation_error=compile_error
                )
        else:
            compiled_path = code_path
        
        # Run test cases
        for i, test_case in enumerate(test_cases, 1):
            start_time = time.time()
            
            try:
                actual_output = self._run_test(
                    compiled_path,
                    test_case.get('input', ''),
                    language,
                    timeout
                ).strip()
                
                execution_time = time.time() - start_time
                total_time += execution_time
                
                expected_output = str(test_case.get('expected_output', '')).strip()
                passed = actual_output == expected_output
                
                result = TestResult(
                    test_number=i,
                    passed=passed,
                    input_data=test_case.get('input', ''),
                    expected_output=expected_output,
                    actual_output=actual_output,
                    execution_time=execution_time,
                    explanation=test_case.get('explanation', '')
                )
                
                results.append(result)
                
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                total_time += execution_time
                
                result = TestResult(
                    test_number=i,
                    passed=False,
                    input_data=test_case.get('input', ''),
                    expected_output=test_case.get('expected_output', ''),
                    actual_output='',
                    execution_time=execution_time,
                    error=f"Timeout (>{timeout}s)",
                    explanation=test_case.get('explanation', '')
                )
                results.append(result)
                
            except Exception as e:
                execution_time = time.time() - start_time
                total_time += execution_time
                
                result = TestResult(
                    test_number=i,
                    passed=False,
                    input_data=test_case.get('input', ''),
                    expected_output=test_case.get('expected_output', ''),
                    actual_output='',
                    execution_time=execution_time,
                    error=str(e),
                    explanation=test_case.get('explanation', '')
                )
                results.append(result)
        
        # Calculate summary
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        success_rate = (passed_count / len(results)) * 100 if results else 0
        
        return ExecutionSummary(
            total_tests=len(results),
            passed_tests=passed_count,
            failed_tests=failed_count,
            total_time=total_time,
            success_rate=success_rate,
            results=results,
            compilation_error=compilation_error
        )
    
    def _compile(self, code: str, language: str, temp_dir: Path) -> Tuple[Optional[str], Optional[Path]]:
        """Compile code if needed"""
        try:
            if language == "java":
                return self._compile_java(code, temp_dir)
            elif language in ["csharp", "c#"]:
                return self._compile_csharp(code, temp_dir)
        except Exception as e:
            return str(e), None
        
        return None, None
    
    def _compile_java(self, code: str, temp_dir: Path) -> Tuple[Optional[str], Optional[Path]]:
        """Compile Java code"""
        # Extract class name from code
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        if not match:
            return "Could not find public class definition", None
        
        class_name = match.group(1)
        java_file = temp_dir / f"{class_name}.java"
        
        with open(java_file, 'w') as f:
            f.write(code)
        
        try:
            result = subprocess.run(
                ['javac', str(java_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return result.stderr, None
            
            return None, java_file
            
        except FileNotFoundError:
            return "Java compiler (javac) not found. Install Java Development Kit.", None
    
    def _compile_csharp(self, code: str, temp_dir: Path) -> Tuple[Optional[str], Optional[Path]]:
        """Compile C# code"""
        cs_file = temp_dir / "solution.cs"
        exe_file = temp_dir / "solution.exe"
        
        with open(cs_file, 'w') as f:
            f.write(code)
        
        try:
            result = subprocess.run(
                ['csc', str(cs_file), f'/out:{exe_file}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return result.stderr, None
            
            return None, exe_file
            
        except FileNotFoundError:
            return "C# compiler (csc) not found. Install .NET SDK.", None
    
    def _run_test(self, code_path: Path, test_input: str, language: str, timeout: int) -> str:
        """Run a single test case"""
        language = language.lower()
        
        if language == "java":
            return self._run_java(code_path, test_input, timeout)
        elif language == "python":
            return self._run_python(code_path, test_input, timeout)
        elif language == "javascript":
            return self._run_javascript(code_path, test_input, timeout)
        elif language in ["csharp", "c#"]:
            return self._run_csharp(code_path, test_input, timeout)
        
        raise ValueError(f"Unsupported language: {language}")
    
    def _run_java(self, class_file: Path, test_input: str, timeout: int) -> str:
        """Run Java compiled class"""
        import re
        
        with open(class_file, 'r') as f:
            code = f.read()
        
        match = re.search(r'public\s+class\s+(\w+)', code)
        class_name = match.group(1) if match else "Main"
        
        result = subprocess.run(
            ['java', '-cp', str(class_file.parent), class_name],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        
        return result.stdout
    
    def _run_python(self, script_file: Path, test_input: str, timeout: int) -> str:
        """Run Python script"""
        result = subprocess.run(
            [sys.executable, str(script_file)],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        
        return result.stdout
    
    def _run_javascript(self, script_file: Path, test_input: str, timeout: int) -> str:
        """Run JavaScript with Node.js"""
        try:
            result = subprocess.run(
                ['node', str(script_file)],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            
            return result.stdout
            
        except FileNotFoundError:
            raise RuntimeError("Node.js not found. Install Node.js to run JavaScript tests.")
    
    def _run_csharp(self, exe_file: Path, test_input: str, timeout: int) -> str:
        """Run C# compiled executable"""
        result = subprocess.run(
            [str(exe_file)],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        
        return result.stdout
    
    def get_detailed_feedback(self, summary: ExecutionSummary) -> str:
        """Generate detailed feedback from test results"""
        feedback = []
        
        if summary.compilation_error:
            return f"❌ Compilation Error:\n{summary.compilation_error}"
        
        feedback.append(f"\n{'='*60}")
        feedback.append(f"Test Results: {summary.passed_tests}/{summary.total_tests} passed ({summary.success_rate:.1f}%)")
        feedback.append(f"Total Time: {summary.total_time:.2f}s")
        feedback.append(f"{'='*60}\n")
        
        for result in summary.results:
            icon = "✅" if result.passed else "❌"
            feedback.append(f"{icon} Test {result.test_number}:")
            feedback.append(f"   Input: {result.input_data}")
            feedback.append(f"   Expected: {result.expected_output}")
            feedback.append(f"   Got: {result.actual_output}")
            
            if result.error:
                feedback.append(f"   Error: {result.error}")
            
            feedback.append(f"   Time: {result.execution_time:.3f}s")
            
            if result.explanation:
                feedback.append(f"   Explanation: {result.explanation}")
            
            feedback.append("")
        
        # Summary
        if summary.passed_tests == summary.total_tests:
            feedback.append("🎉 All tests passed! Great job!")
        elif summary.passed_tests > 0:
            feedback.append(f"📝 {summary.failed_tests} test(s) failed. Check the details above.")
        else:
            feedback.append("⚠️  No tests passed. Review your solution logic.")
        
        return "\n".join(feedback)
