"""Resume parsing tool for extracting structured information."""

from typing import Dict, Any, List, Type, ClassVar
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from pypdf import PdfReader
import json
import re
import os


class ResumeParserInput(BaseModel):
    """Input schema for resume parser tool."""
    file_path: str = Field(description="Path to the resume file (PDF or TXT)")


class ResumeParserTool(BaseTool):
    """Tool for parsing resumes and extracting structured information."""

    name: str = "parse_resume"
    description: str = """
    Parse a resume file and extract structured information including:
    - Contact details (name, email, phone)
    - Skills (technical and soft skills)
    - Work experience
    - Education
    - Certifications

    Input: file path to resume (PDF or TXT)
    Output: Structured JSON with extracted information
    """
    args_schema: Type[BaseModel] = ResumeParserInput

    # Common technical skills to look for
    TECH_SKILLS: ClassVar[List[str]] = [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r",
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "spring", "fastapi", "nextjs", "svelte",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "git", "jenkins", "github actions", "ci/cd", "devops",
        "machine learning", "deep learning", "ai", "nlp", "computer vision",
        "data analysis", "data science", "pandas", "numpy", "tensorflow",
        "pytorch", "scikit-learn", "spark", "hadoop",
        "html", "css", "sass", "tailwind", "bootstrap",
        "rest api", "graphql", "microservices", "agile", "scrum"
    ]

    SOFT_SKILLS: ClassVar[List[str]] = [
        "leadership", "communication", "teamwork", "problem solving",
        "analytical", "project management", "time management",
        "mentoring", "collaboration", "presentation", "negotiation"
    ]

    def _run(self, file_path: str) -> str:
        """
        Parse resume and return structured data.

        Args:
            file_path: Path to the resume file

        Returns:
            JSON string with extracted information
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return json.dumps({
                    "error": f"File not found: {file_path}",
                    "success": False
                })

            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                text = self._extract_pdf_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            # Parse the resume
            parsed = {
                "success": True,
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "contact": {
                    "name": self._extract_name(text),
                    "email": self._extract_email(text),
                    "phone": self._extract_phone(text),
                    "linkedin": self._extract_linkedin(text)
                },
                "skills": {
                    "technical": self._extract_technical_skills(text),
                    "soft": self._extract_soft_skills(text)
                },
                "experience_years": self._estimate_experience_years(text),
                "education": self._extract_education(text),
                "certifications": self._extract_certifications(text),
                "raw_text_preview": text[:1500] + "..." if len(text) > 1500 else text
            }

            return json.dumps(parsed, indent=2)

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "success": False,
                "file_path": file_path
            })

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)

    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume."""
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Skip empty lines and lines that look like headers
            if not line or '@' in line or line.lower() in ['resume', 'curriculum vitae', 'cv']:
                continue
            # Check if it looks like a name (2-4 words, mostly letters)
            words = line.split()
            if 1 <= len(words) <= 4:
                if all(word.replace('.', '').replace('-', '').isalpha() for word in words):
                    return line
        return ""

    def _extract_email(self, text: str) -> str:
        """Extract email address from text."""
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0).lower() if match else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text."""
        patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL from text."""
        pattern = r'linkedin\.com/in/[\w-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://www.{match.group(0)}" if match else ""

    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        text_lower = text.lower()
        found_skills = []
        for skill in self.TECH_SKILLS:
            # Use word boundary matching for better accuracy
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
        return list(set(found_skills))

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from text."""
        text_lower = text.lower()
        found_skills = []
        for skill in self.SOFT_SKILLS:
            if skill in text_lower:
                found_skills.append(skill.title())
        return list(set(found_skills))

    def _estimate_experience_years(self, text: str) -> int:
        """Estimate years of experience from resume."""
        # Look for explicit mentions
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in\s+)?(?:software|development|engineering)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                if 0 < years < 50:  # Sanity check
                    return years

        # Count date ranges in work experience
        year_pattern = r'(19|20)\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years = [int(y + '00') for y in years]  # Convert to full years
            # This is a rough estimate
            return min(max(max(years) - min(years), 0), 30)

        return 0

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from text."""
        education = []

        # Common degree patterns
        degree_patterns = [
            (r"(?:Ph\.?D\.?|Doctor(?:ate)?)\s+(?:in\s+)?(\w+(?:\s+\w+)*)", "PhD"),
            (r"(?:M\.?S\.?|Master(?:'s)?)\s+(?:in\s+)?(\w+(?:\s+\w+)*)", "Master's"),
            (r"(?:M\.?B\.?A\.?)", "MBA"),
            (r"(?:B\.?S\.?|Bachelor(?:'s)?)\s+(?:in\s+)?(\w+(?:\s+\w+)*)", "Bachelor's"),
            (r"(?:B\.?A\.?)\s+(?:in\s+)?(\w+(?:\s+\w+)*)", "Bachelor's"),
        ]

        for pattern, degree_type in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                field = match.group(1) if match.lastindex else ""
                education.append({
                    "degree": degree_type,
                    "field": field.strip() if field else "Not specified"
                })

        return education[:3]  # Return top 3 education entries

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text."""
        certifications = []

        # Common certification keywords
        cert_keywords = [
            "AWS Certified", "Azure", "Google Cloud", "GCP",
            "PMP", "Scrum Master", "CISSP", "CCNA", "CCNP",
            "CKA", "CKS", "Terraform", "Certified Kubernetes"
        ]

        text_lower = text.lower()
        for cert in cert_keywords:
            if cert.lower() in text_lower:
                certifications.append(cert)

        return list(set(certifications))

    async def _arun(self, file_path: str) -> str:
        """Async version of _run."""
        return self._run(file_path)
