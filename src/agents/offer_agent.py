"""Offer Agent for managing job offers and negotiations."""

from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.offer_prompts import OFFER_SYSTEM_PROMPT


class OfferAgent(BaseAgent):
    """Agent responsible for creating offers and managing negotiations."""

    def __init__(self):
        super().__init__(
            name="OfferAgent",
            system_prompt=OFFER_SYSTEM_PROMPT,
            temperature=0.3
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute offer creation.

        Args:
            state: Current workflow state

        Returns:
            Updated state with offer recommendations
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Creating offer recommendations")

        final_recommendations = state.get("final_recommendations", "")
        job_description = state.get("job_description", "")

        prompt = f"""
        Based on the final candidate recommendations, create offer guidance:

        JOB DESCRIPTION:
        {job_description}

        FINAL RECOMMENDATIONS:
        {final_recommendations}

        For the top candidate(s), provide:
        1. Recommended salary range based on experience and market
        2. Suggested compensation package structure
        3. Key selling points for this candidate
        4. Potential negotiation points
        5. Risk assessment (likelihood to accept, competing offers)
        6. Timeline recommendations

        Be strategic and data-driven.
        """

        response = self.invoke([HumanMessage(content=prompt)])

        state["offer_recommendations"] = response
        state["offer_planning_completed"] = True
        state["execution_log"].append(f"[{self.name}] Offer recommendations created")

        return state

    def generate_offer_letter(
        self,
        candidate_info: Dict[str, Any],
        offer_details: Dict[str, Any],
        template: Optional[str] = None
    ) -> str:
        """
        Generate a formal offer letter.

        Args:
            candidate_info: Candidate information
            offer_details: Compensation and role details
            template: Optional custom template

        Returns:
            Generated offer letter
        """
        prompt = f"""
        Generate a professional offer letter with these details:

        CANDIDATE:
        - Name: {candidate_info.get('name')}
        - Email: {candidate_info.get('email')}

        OFFER DETAILS:
        - Position: {offer_details.get('title')}
        - Department: {offer_details.get('department')}
        - Base Salary: ${offer_details.get('base_salary'):,.2f} {offer_details.get('currency', 'USD')}
        - Bonus: {offer_details.get('bonus', 'Not specified')}
        - Equity: {offer_details.get('equity', 'Not specified')}
        - Start Date: {offer_details.get('start_date', 'To be determined')}
        - Employment Type: {offer_details.get('employment_type', 'Full-time')}
        - Location: {offer_details.get('location')}

        Include:
        1. Formal greeting and congratulations
        2. Position details and compensation
        3. Benefits overview
        4. Start date and reporting structure
        5. Employment terms (at-will, etc.)
        6. Acceptance deadline
        7. Next steps
        8. Contact information

        Use professional, warm tone. Make them excited to join!
        """

        return self.chat(prompt)

    def recommend_compensation(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: Dict[str, Any],
        salary_range: Dict[str, float],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend compensation package.

        Args:
            candidate_profile: Candidate experience and skills
            job_requirements: Job requirements
            salary_range: Approved salary range
            market_data: Market compensation data

        Returns:
            Recommended compensation package
        """
        market_info = f"\n\nMARKET DATA:\n{market_data}" if market_data else ""

        prompt = f"""
        Recommend compensation for this candidate:

        CANDIDATE PROFILE:
        - Experience: {candidate_profile.get('years_experience')} years
        - Skills: {candidate_profile.get('skills')}
        - Current Salary: {candidate_profile.get('current_salary', 'Unknown')}
        - Expectations: {candidate_profile.get('salary_expectation', 'Unknown')}
        - Location: {candidate_profile.get('location')}

        JOB REQUIREMENTS:
        {job_requirements}

        APPROVED SALARY RANGE:
        Min: ${salary_range.get('min'):,.2f}
        Max: ${salary_range.get('max'):,.2f}
        {market_info}

        Recommend:
        1. Base salary (within range)
        2. Performance bonus structure
        3. Equity/stock options (if applicable)
        4. Additional perks
        5. Total compensation value
        6. Rationale for recommendation
        7. Negotiation room

        Be fair and competitive.
        """

        response = self.chat(prompt)

        return {
            "recommendation": response,
            "created_at": datetime.now().isoformat()
        }

    def evaluate_counteroffer(
        self,
        original_offer: Dict[str, Any],
        counteroffer: Dict[str, Any],
        budget_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate's counteroffer.

        Args:
            original_offer: Our original offer
            counteroffer: Candidate's counter
            budget_constraints: Budget limits

        Returns:
            Analysis and recommendation
        """
        prompt = f"""
        Analyze this counteroffer:

        ORIGINAL OFFER:
        - Base: ${original_offer.get('base_salary'):,.2f}
        - Bonus: {original_offer.get('bonus')}
        - Equity: {original_offer.get('equity')}

        COUNTEROFFER:
        - Requested Base: ${counteroffer.get('requested_salary'):,.2f}
        - Other requests: {counteroffer.get('other_requests')}
        - Reasoning: {counteroffer.get('reasoning')}

        BUDGET CONSTRAINTS:
        - Max approved: ${budget_constraints.get('max_approved'):,.2f}
        - Flexibility: {budget_constraints.get('flexibility')}

        Provide:
        1. Is the counter reasonable?
        2. Can we meet their request?
        3. If not, what counter-counter should we make?
        4. Alternative value propositions (non-monetary)
        5. Risk assessment (will they walk away?)
        6. Recommendation (accept, counter, decline)

        Be strategic but fair.
        """

        response = self.chat(prompt)

        return {
            "analysis": response,
            "analyzed_at": datetime.now().isoformat()
        }

    def generate_negotiation_response(
        self,
        situation: str,
        strategy: str = "collaborative"
    ) -> str:
        """
        Generate negotiation response email.

        Args:
            situation: Current negotiation situation
            strategy: Negotiation strategy (collaborative, firm, flexible)

        Returns:
            Email response
        """
        prompt = f"""
        Generate a negotiation response email:

        SITUATION:
        {situation}

        STRATEGY: {strategy}

        The response should:
        - Acknowledge their perspective
        - Explain our position clearly
        - Propose a path forward
        - Keep relationship positive
        - Maintain professionalism

        Tone should be {strategy} and respectful.
        """

        return self.chat(prompt)

    def calculate_total_compensation(
        self,
        base_salary: float,
        bonus: Optional[float] = None,
        equity_value: Optional[float] = None,
        benefits_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculate total compensation value."""
        total = base_salary

        components = {
            "base_salary": base_salary,
            "bonus": bonus or 0,
            "equity_value": equity_value or 0,
            "benefits_value": benefits_value or 0
        }

        total = sum(components.values())

        return {
            "components": components,
            "total_compensation": total,
            "currency": "USD"
        }
