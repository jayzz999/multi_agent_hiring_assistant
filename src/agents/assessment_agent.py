"""Assessment Agent for generating and evaluating skills tests."""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.assessment_prompts import ASSESSMENT_SYSTEM_PROMPT


class AssessmentAgent(BaseAgent):
    """Agent responsible for creating and evaluating skills assessments."""

    def __init__(self):
        super().__init__(
            name="AssessmentAgent",
            system_prompt=ASSESSMENT_SYSTEM_PROMPT,
            temperature=0.7
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute assessment planning.

        Args:
            state: Current workflow state

        Returns:
            Updated state with assessment plan
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Creating assessment plan")

        job_description = state.get("job_description", "")
        plan = state.get("plan", "")

        prompt = f"""
        Based on this job description and hiring plan, create a comprehensive assessment strategy:

        JOB DESCRIPTION:
        {job_description}

        HIRING PLAN:
        {plan}

        Create an assessment plan that includes:
        1. Recommended assessment types (coding, take-home, system design, etc.)
        2. Skills to test and how to test them
        3. Difficulty level recommendations
        4. Time allocations
        5. Evaluation criteria and rubrics
        6. Sample questions/problems
        7. What to look for in good vs. poor answers

        Format as a structured assessment plan.
        """

        response = self.invoke([HumanMessage(content=prompt)])

        state["assessment_plan"] = response
        state["assessment_plan_completed"] = True
        state["execution_log"].append(f"[{self.name}] Assessment plan created")

        return state

    def generate_coding_challenge(
        self,
        skills_required: List[str],
        difficulty: str = "medium",
        time_limit_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Generate a coding challenge.

        Args:
            skills_required: List of skills to test
            difficulty: easy, medium, or hard
            time_limit_minutes: Time limit for the challenge

        Returns:
            Dictionary with problem statement, test cases, rubric
        """
        prompt = f"""
        Generate a coding challenge with these requirements:

        SKILLS TO TEST: {', '.join(skills_required)}
        DIFFICULTY: {difficulty}
        TIME LIMIT: {time_limit_minutes} minutes

        Include:
        1. Problem statement (clear and unambiguous)
        2. Input/output examples
        3. Test cases (including edge cases)
        4. Evaluation rubric
        5. What constitutes a good solution
        6. Common mistakes to watch for

        Make it realistic and practical, not just algorithmic puzzles.
        """

        response = self.chat(prompt)

        return {
            "problem": response,
            "skills_tested": skills_required,
            "difficulty": difficulty,
            "time_limit": time_limit_minutes,
            "type": "coding"
        }

    def generate_system_design_question(
        self,
        domain: str,
        level: str = "senior"
    ) -> Dict[str, Any]:
        """Generate a system design question."""
        prompt = f"""
        Generate a system design question for:

        DOMAIN: {domain}
        LEVEL: {level}

        Include:
        1. Problem statement
        2. Requirements (functional and non-functional)
        3. Scale expectations
        4. What to evaluate (architecture, scalability, trade-offs)
        5. Discussion points
        6. Evaluation rubric

        Make it realistic and relevant to actual work.
        """

        response = self.chat(prompt)

        return {
            "question": response,
            "domain": domain,
            "level": level,
            "type": "system_design"
        }

    def evaluate_code_submission(
        self,
        problem: str,
        submission_code: str,
        test_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a code submission.

        Args:
            problem: Original problem statement
            submission_code: Candidate's code
            test_results: Results from automated tests

        Returns:
            Evaluation with scores and feedback
        """
        test_info = f"\n\nTEST RESULTS:\n{test_results}" if test_results else ""

        prompt = f"""
        Evaluate this code submission:

        PROBLEM:
        {problem}

        SUBMITTED CODE:
        ```
        {submission_code}
        ```
        {test_info}

        Evaluate on:
        1. Correctness (does it solve the problem?)
        2. Code quality (readability, structure, naming)
        3. Efficiency (time/space complexity)
        4. Edge case handling
        5. Best practices
        6. Testing (if included)

        Provide:
        - Overall score (0-100)
        - Scores for each criterion
        - Strengths
        - Areas for improvement
        - Recommendation (strong pass, pass, borderline, fail)
        """

        response = self.chat(prompt)

        return {
            "evaluation": response,
            "evaluated_at": "datetime.now().isoformat()"
        }

    def detect_plagiarism(
        self,
        submission_code: str,
        reference_solutions: List[str]
    ) -> Dict[str, Any]:
        """
        Detect potential plagiarism in code submission.

        Args:
            submission_code: Candidate's code
            reference_solutions: Known solutions from internet/other candidates

        Returns:
            Plagiarism analysis
        """
        prompt = f"""
        Analyze this code for potential plagiarism:

        SUBMISSION:
        ```
        {submission_code}
        ```

        Compare against common patterns and check for:
        1. Unusual similarity to reference solutions
        2. Comments/variable names indicating copy-paste
        3. Inconsistent coding style
        4. Over-optimization for a timed test
        5. Code structure that matches common online solutions

        Provide plagiarism likelihood (low, medium, high) and reasoning.
        """

        response = self.chat(prompt)

        return {
            "analysis": response,
            "checked_at": "datetime.now().isoformat()"
        }

    def create_take_home_assignment(
        self,
        role_type: str,
        skills_to_test: List[str],
        time_estimate_hours: int = 4
    ) -> Dict[str, Any]:
        """Generate a take-home assignment."""
        prompt = f"""
        Create a take-home assignment for a {role_type} role:

        SKILLS TO TEST: {', '.join(skills_to_test)}
        ESTIMATED TIME: {time_estimate_hours} hours

        Include:
        1. Project description
        2. Requirements (must-have and nice-to-have)
        3. Evaluation criteria
        4. Submission instructions
        5. What we're looking for
        6. Tips for candidates

        Make it realistic, practical, and respectful of their time.
        Don't ask for more than {time_estimate_hours} hours of work.
        """

        response = self.chat(prompt)

        return {
            "assignment": response,
            "role_type": role_type,
            "time_estimate": time_estimate_hours,
            "skills_tested": skills_to_test,
            "type": "take_home"
        }

    def evaluate_take_home(
        self,
        assignment: str,
        submission_url: str,
        evaluation_criteria: List[str]
    ) -> Dict[str, Any]:
        """Evaluate a take-home assignment submission."""
        prompt = f"""
        Evaluate this take-home assignment:

        ASSIGNMENT:
        {assignment}

        SUBMISSION URL: {submission_url}

        EVALUATION CRITERIA:
        {chr(10).join(f"- {c}" for c in evaluation_criteria)}

        Review and provide:
        1. Score for each criterion (0-10)
        2. Overall score
        3. Strengths of the solution
        4. Areas for improvement
        5. Recommendation (strong hire, hire, maybe, no hire)
        6. Discussion questions for follow-up interview

        Be fair and considerate of the time invested.
        """

        response = self.chat(prompt)

        return {
            "evaluation": response,
            "evaluated_at": "datetime.now().isoformat()"
        }
