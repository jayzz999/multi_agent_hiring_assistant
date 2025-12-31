"""Compliance Agent for ensuring legal and regulatory adherence."""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.compliance_prompts import COMPLIANCE_SYSTEM_PROMPT


class ComplianceAgent(BaseAgent):
    """Agent responsible for compliance, bias detection, and legal adherence."""

    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            system_prompt=COMPLIANCE_SYSTEM_PROMPT,
            temperature=0.2
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance checks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with compliance analysis
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Running compliance checks")

        # Analyze the entire workflow for compliance
        prompt = f"""
        Review this hiring workflow for compliance issues:

        SCREENING RESULTS: {state.get('screening_results', '')}
        MATCHING RESULTS: {state.get('matching_results', '')}
        RANKING RESULTS: {state.get('ranking_results', '')}

        Check for:
        1. Potential bias in screening criteria
        2. Discriminatory patterns
        3. Equal opportunity compliance
        4. Fair evaluation practices
        5. Adverse impact concerns
        6. Documentation completeness

        Provide compliance report with any red flags.
        """

        response = self.invoke([HumanMessage(content=prompt)])

        state["compliance_report"] = response
        state["compliance_checked"] = True
        state["execution_log"].append(f"[{self.name}] Compliance check completed")

        return state

    def detect_bias_in_screening(
        self,
        screening_criteria: List[str],
        screening_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect potential bias in screening decisions.

        Args:
            screening_criteria: Criteria used for screening
            screening_results: Screening outcomes

        Returns:
            Bias detection report
        """
        prompt = f"""
        Analyze for potential bias:

        SCREENING CRITERIA:
        {chr(10).join(f"- {c}" for c in screening_criteria)}

        SCREENING RESULTS:
        Total candidates: {len(screening_results)}
        Passed: {sum(1 for r in screening_results if r.get('passed'))}
        Failed: {sum(1 for r in screening_results if not r.get('passed'))}

        Detect:
        1. Criteria that may have disparate impact
        2. Potential age bias (experience requirements)
        3. Gender bias (language, requirements)
        4. Educational bias (degree requirements)
        5. Location bias
        6. Name-based bias

        Provide:
        - Bias likelihood (low, medium, high)
        - Specific concerns
        - Recommendations to mitigate
        """

        response = self.chat(prompt)

        return {
            "analysis": response,
            "risk_level": "to_be_extracted",
            "recommendations": []
        }

    def check_job_description_compliance(
        self,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Check job description for compliance issues.

        Args:
            job_description: Job description text

        Returns:
            Compliance analysis
        """
        prompt = f"""
        Review this job description for compliance:

        JOB DESCRIPTION:
        {job_description}

        Check for:
        1. Discriminatory language (age, gender, race, etc.)
        2. Unnecessary requirements that may exclude protected groups
        3. ADA compliance (essential vs non-essential functions)
        4. Equal opportunity statement
        5. Inclusive language
        6. Overly restrictive requirements

        Provide:
        - Issues found (if any)
        - Severity (low, medium, high)
        - Suggested corrections
        - Compliant version of problematic sections
        """

        response = self.chat(prompt)

        return {
            "analysis": response,
            "compliant": True,  # to be determined from response
            "issues": []
        }

    def calculate_adverse_impact(
        self,
        demographic_data: Dict[str, Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Calculate adverse impact ratio.

        Args:
            demographic_data: Selection rates by demographic group

        Returns:
            Adverse impact analysis

        The four-fifths rule: selection rate for any group should be
        at least 80% of the selection rate of the highest group.
        """
        # Example structure:
        # {
        #   "group_a": {"applied": 100, "selected": 20},
        #   "group_b": {"applied": 50, "selected": 5}
        # }

        results = {}
        highest_rate = 0
        highest_group = None

        # Calculate selection rates
        for group, data in demographic_data.items():
            applied = data.get("applied", 0)
            selected = data.get("selected", 0)

            if applied > 0:
                rate = selected / applied
                results[group] = {
                    "applied": applied,
                    "selected": selected,
                    "selection_rate": rate
                }

                if rate > highest_rate:
                    highest_rate = rate
                    highest_group = group

        # Check for adverse impact
        adverse_impact_found = False
        failing_groups = []

        for group, data in results.items():
            if group != highest_group:
                ratio = data["selection_rate"] / highest_rate if highest_rate > 0 else 0

                if ratio < 0.8:  # Four-fifths rule
                    adverse_impact_found = True
                    failing_groups.append({
                        "group": group,
                        "ratio": ratio,
                        "selection_rate": data["selection_rate"]
                    })

        return {
            "adverse_impact_detected": adverse_impact_found,
            "highest_selection_rate": highest_rate,
            "highest_group": highest_group,
            "failing_groups": failing_groups,
            "all_results": results
        }

    def generate_eeo_report(
        self,
        job_id: str,
        applications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate EEO compliance report.

        Args:
            job_id: Job ID
            applications: All applications with demographic data

        Returns:
            EEO report
        """
        # Count by demographics (if voluntarily provided)
        total = len(applications)

        # This would aggregate demographic data
        # Gender, ethnicity, veteran status, disability status

        report = {
            "job_id": job_id,
            "total_applications": total,
            "demographics": {
                # Aggregated counts (anonymized)
            },
            "selection_rates": {
                # By demographic group
            },
            "adverse_impact_analysis": {},
            "generated_at": "datetime.now().isoformat()"
        }

        return report

    def anonymize_resume(
        self,
        resume_text: str,
        remove_fields: Optional[List[str]] = None
    ) -> str:
        """
        Anonymize resume for blind screening.

        Args:
            resume_text: Original resume
            remove_fields: Fields to remove (name, gender indicators, age, etc.)

        Returns:
            Anonymized resume
        """
        default_fields = ["name", "gender", "age", "photo", "address"]
        fields_to_remove = remove_fields or default_fields

        prompt = f"""
        Anonymize this resume by removing identifying information:

        RESUME:
        {resume_text}

        REMOVE:
        {', '.join(fields_to_remove)}

        Keep:
        - Skills and experience
        - Education (without dates if age-related)
        - Work history (sanitized company names if requested)

        Return the anonymized version.
        """

        return self.chat(prompt)

    def check_interview_questions(
        self,
        questions: List[str]
    ) -> Dict[str, Any]:
        """
        Check interview questions for legal compliance.

        Args:
            questions: List of proposed interview questions

        Returns:
            Compliance analysis
        """
        prompt = f"""
        Review these interview questions for legal compliance:

        QUESTIONS:
        {chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

        Flag any questions that:
        1. Ask about protected characteristics (age, marital status, etc.)
        2. Could lead to discrimination
        3. Are not job-related
        4. Violate privacy
        5. Are illegal in any US jurisdiction

        For each flagged question, provide:
        - Why it's problematic
        - Legal risk (low, medium, high)
        - Alternative question that gets at the same competency legally
        """

        response = self.chat(prompt)

        return {
            "analysis": response,
            "has_issues": False,  # to be determined
            "flagged_questions": []
        }
