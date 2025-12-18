"""Resume Screener Agent for initial candidate screening."""

from typing import Any, Dict, List
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.tools.rag_retriever import RAGRetrieverTool
from src.prompts.screener_prompts import SCREENER_SYSTEM_PROMPT, SCREENER_TASK_PROMPT


class ResumeScreenerAgent(BaseAgent):
    """
    Resume Screener Agent that performs initial candidate screening.

    This executor agent reviews candidate resumes against job requirements,
    making PASS/FAIL decisions and providing preliminary scores.
    """

    def __init__(self, vector_store=None):
        """
        Initialize the Resume Screener Agent.

        Args:
            vector_store: Optional VectorStore instance for RAG
        """
        self.rag_tool = RAGRetrieverTool(vector_store=vector_store)

        super().__init__(
            name="Resume Screener",
            system_prompt=SCREENER_SYSTEM_PROMPT,
            tools=[self.rag_tool],
            temperature=0.2  # Low temperature for consistent screening decisions
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Screen resumes against job requirements.

        Args:
            state: Current workflow state containing:
                - job_description: The job requirements
                - plan: The hiring plan from Planner
                - candidates: Optional list of specific candidates

        Returns:
            Updated state with:
                - screening_results: Screening decisions for each candidate
                - screening_completed: True
                - current_step: Incremented
        """
        job_description = state.get("job_description", "")
        plan = state.get("plan", "")

        if not job_description:
            return {
                **state,
                "error": "No job description provided for screening",
                "screening_results": None,
                "screening_completed": False
            }

        # Use RAG to find relevant candidates
        search_query = self._build_search_query(job_description)
        rag_results = self.rag_tool._run(search_query, doc_type="resume")

        # Create screening prompt
        prompt = SCREENER_TASK_PROMPT.format(
            plan=plan or "No plan provided",
            job_description=job_description,
            rag_results=rag_results
        )

        # Perform screening
        screening_results = self.invoke([HumanMessage(content=prompt)])

        return {
            **state,
            "screening_results": screening_results,
            "screening_completed": True,
            "current_step": state.get("current_step", 0) + 1
        }

    def _build_search_query(self, job_description: str) -> str:
        """
        Build an effective search query from the job description.

        Args:
            job_description: The full job description

        Returns:
            Optimized search query
        """
        # Extract key terms for search (simplified version)
        # In production, you might use NLP to extract key skills
        query = f"Find candidates matching: {job_description[:500]}"
        return query

    def screen_single_resume(
        self,
        resume_text: str,
        job_description: str,
        plan: str = ""
    ) -> Dict[str, Any]:
        """
        Screen a single resume against job requirements.

        Args:
            resume_text: The resume content
            job_description: Job requirements
            plan: Optional hiring plan

        Returns:
            Screening decision dictionary
        """
        prompt = f"""
Screen this single resume against the job requirements:

HIRING PLAN:
{plan or "No plan provided"}

JOB REQUIREMENTS:
{job_description}

RESUME:
{resume_text}

Provide your screening decision following the output format.
"""

        result = self.invoke([HumanMessage(content=prompt)])

        return {
            "screening_result": result,
            "job_description_preview": job_description[:200] + "..."
        }

    def batch_screen(
        self,
        resumes: List[str],
        job_description: str,
        plan: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Screen multiple resumes.

        Args:
            resumes: List of resume texts
            job_description: Job requirements
            plan: Optional hiring plan

        Returns:
            List of screening decisions
        """
        results = []
        for i, resume in enumerate(resumes):
            result = self.screen_single_resume(resume, job_description, plan)
            result["candidate_index"] = i
            results.append(result)
        return results
