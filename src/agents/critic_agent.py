"""Critic Agent for quality evaluation and oversight."""

from typing import Any, Dict
from langchain_core.messages import HumanMessage
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.critic_prompts import CRITIC_SYSTEM_PROMPT, CRITIC_TASK_PROMPT


class CriticAgent(BaseAgent):
    """
    Critic Agent that evaluates the quality and fairness of the hiring process.

    This is the final agent in the PEC (Planner-Executor-Critic) architecture.
    It reviews decisions made by other agents and ensures quality standards.
    """

    def __init__(self):
        """Initialize the Critic Agent."""
        super().__init__(
            name="Hiring Critic",
            system_prompt=CRITIC_SYSTEM_PROMPT,
            temperature=0.4  # Moderate temperature for balanced critique
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the quality of the hiring process and decisions.

        Args:
            state: Current workflow state containing:
                - plan: The hiring plan
                - screening_results: Results from Resume Screener
                - matching_results: Results from Skill Matcher
                - ranking_results: Results from Candidate Ranker

        Returns:
            Updated state with:
                - critique: Detailed evaluation
                - verdict: APPROVE, REVISE, or REJECT
                - critique_completed: True
                - current_step: Incremented
        """
        plan = state.get("plan", "")
        screening_results = state.get("screening_results", "")
        matching_results = state.get("matching_results", "")
        ranking_results = state.get("ranking_results", "")

        # Check if we have enough data to critique
        if not any([screening_results, matching_results, ranking_results]):
            return {
                **state,
                "error": "Insufficient data for critique - no agent results found",
                "critique": None,
                "verdict": "REJECT",
                "critique_completed": False
            }

        # Create critique prompt
        prompt = CRITIC_TASK_PROMPT.format(
            plan=plan or "No plan provided",
            screening_results=screening_results or "No screening results",
            matching_results=matching_results or "No matching results",
            ranking_results=ranking_results or "No ranking results"
        )

        # Perform critique
        critique = self.invoke([HumanMessage(content=prompt)])

        # Extract verdict from critique
        verdict = self._extract_verdict(critique)

        return {
            **state,
            "critique": critique,
            "verdict": verdict,
            "critique_completed": True,
            "current_step": state.get("current_step", 0) + 1
        }

    def _extract_verdict(self, critique: str) -> str:
        """
        Extract the verdict from critique text.

        Args:
            critique: Full critique text

        Returns:
            Verdict: APPROVE, REVISE, or REJECT
        """
        # Look for explicit verdict
        critique_upper = critique.upper()

        # Check for verdict patterns
        verdict_patterns = [
            r'FINAL\s+VERDICT:\s*(APPROVE|REVISE|REJECT)',
            r'VERDICT:\s*(APPROVE|REVISE|REJECT)',
            r'\*\*(APPROVE|REVISE|REJECT)\*\*'
        ]

        for pattern in verdict_patterns:
            match = re.search(pattern, critique_upper)
            if match:
                return match.group(1)

        # Fallback: count mentions
        approve_count = critique_upper.count("APPROVE")
        revise_count = critique_upper.count("REVISE")
        reject_count = critique_upper.count("REJECT")

        if reject_count > approve_count and reject_count > revise_count:
            return "REJECT"
        elif revise_count > approve_count:
            return "REVISE"
        else:
            return "APPROVE"

    def quick_review(
        self,
        ranking_results: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Perform a quick review of ranking results.

        Args:
            ranking_results: Final rankings
            job_description: Original job requirements

        Returns:
            Quick review result
        """
        prompt = f"""
Perform a quick quality check on these ranking results:

JOB REQUIREMENTS:
{job_description}

RANKING RESULTS:
{ranking_results}

Briefly evaluate:
1. Are rankings justified? (Yes/Partially/No)
2. Any obvious issues? (List or "None")
3. Quick verdict: APPROVE/REVISE/REJECT
"""

        result = self.invoke([HumanMessage(content=prompt)])

        return {
            "quick_review": result,
            "verdict": self._extract_verdict(result)
        }

    def check_for_bias(
        self,
        all_results: str
    ) -> str:
        """
        Specifically check for potential biases in the process.

        Args:
            all_results: Combined results from all agents

        Returns:
            Bias analysis report
        """
        prompt = f"""
Analyze these hiring process results specifically for potential biases:

PROCESS RESULTS:
{all_results}

Check for:
1. Name/origin bias indicators
2. Institutional bias (preference for certain schools/companies)
3. Age/experience bias
4. Gender indicators
5. Any other fairness concerns

For each, provide: Clear/Potential/None with evidence.
Provide recommendations for improvement.
"""

        return self.invoke([HumanMessage(content=prompt)])

    def generate_improvement_report(
        self,
        critique: str,
        verdict: str
    ) -> str:
        """
        Generate detailed improvement recommendations.

        Args:
            critique: Full critique
            verdict: The verdict given

        Returns:
            Improvement recommendations
        """
        prompt = f"""
Based on this critique and verdict, generate actionable improvement recommendations:

CRITIQUE:
{critique}

VERDICT: {verdict}

Provide:
1. Immediate action items (if REVISE/REJECT)
2. Process improvements for future
3. Training recommendations for agents
4. Best practices to implement
"""

        return self.invoke([HumanMessage(content=prompt)])
