"""Job description parsing tool."""

from typing import Dict, Any, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class JDParserInput(BaseModel):
    """Input schema for job description parser."""
    job_description: str = Field(description="The raw job description text to parse")


class JDParserTool(BaseTool):
    """Tool for parsing job descriptions and extracting structured requirements."""

    name: str = "parse_job_description"
    description: str = """
    Parse a job description and extract structured requirements including:
    - Job title
    - Required skills (must-have)
    - Preferred skills (nice-to-have)
    - Years of experience required
    - Education requirements
    - Key responsibilities
    - Other requirements

    Input: Raw job description text
    Output: Structured JSON with extracted requirements
    """
    args_schema: Type[BaseModel] = JDParserInput

    SYSTEM_PROMPT: ClassVar[str] = """You are an expert HR assistant that extracts structured information from job descriptions.

Extract the following information and return ONLY valid JSON (no markdown, no explanation):

{
    "title": "Job title",
    "department": "Department or team",
    "level": "Entry/Mid/Senior/Lead/Principal",
    "required_skills": ["list of required/must-have technical skills"],
    "preferred_skills": ["list of nice-to-have skills"],
    "experience_years": {
        "min": minimum years required (integer),
        "max": maximum years if specified (integer or null)
    },
    "education": {
        "required": "Required education level",
        "preferred": "Preferred education if different"
    },
    "responsibilities": ["list of key responsibilities"],
    "requirements": ["list of other must-have requirements"],
    "benefits": ["list of benefits if mentioned"],
    "remote_policy": "Remote/Hybrid/On-site/Not specified"
}

Be precise and extract only what's explicitly stated. Use null for fields not mentioned."""

    def _run(self, job_description: str) -> str:
        """
        Parse job description using LLM.

        Args:
            job_description: Raw job description text

        Returns:
            JSON string with structured requirements
        """
        if not job_description or len(job_description.strip()) < 50:
            return json.dumps({
                "error": "Job description is too short or empty",
                "success": False
            })

        try:
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )

            response = llm.invoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=f"Parse this job description:\n\n{job_description}")
            ])

            # Try to parse and validate JSON
            try:
                parsed = json.loads(response.content)
                parsed["success"] = True
                parsed["raw_text_preview"] = job_description[:500] + "..." if len(job_description) > 500 else job_description
                return json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, return the raw response
                return json.dumps({
                    "success": False,
                    "error": "Could not parse LLM response as JSON",
                    "raw_response": response.content
                })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    def parse_without_llm(self, job_description: str) -> Dict[str, Any]:
        """
        Parse job description without LLM (rule-based extraction).
        Useful as a fallback or when LLM is unavailable.

        Args:
            job_description: Raw job description text

        Returns:
            Dictionary with extracted requirements
        """
        import re

        text = job_description.lower()
        result = {
            "title": "",
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": {"min": 0, "max": None},
            "education": {"required": "", "preferred": ""},
            "responsibilities": [],
            "requirements": []
        }

        # Extract experience years
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
            r'(\d+)\s*-\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?'
        ]

        for pattern in exp_patterns:
            match = re.search(pattern, text)
            if match:
                result["experience_years"]["min"] = int(match.group(1))
                if match.lastindex == 2:
                    result["experience_years"]["max"] = int(match.group(2))
                break

        # Extract education requirements
        if "phd" in text or "doctorate" in text:
            result["education"]["required"] = "PhD"
        elif "master" in text:
            result["education"]["required"] = "Master's degree"
        elif "bachelor" in text:
            result["education"]["required"] = "Bachelor's degree"

        # Common skills to look for
        skills = [
            "python", "java", "javascript", "typescript", "react", "node.js",
            "aws", "azure", "gcp", "docker", "kubernetes", "sql", "nosql",
            "machine learning", "data science", "agile", "scrum"
        ]

        for skill in skills:
            if skill in text:
                result["required_skills"].append(skill.title())

        return result

    async def _arun(self, job_description: str) -> str:
        """Async version of _run."""
        return self._run(job_description)
