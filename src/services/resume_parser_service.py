"""Enhanced resume parsing service supporting multiple formats."""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class ResumeParserService:
    """Advanced resume parsing with multiple format support."""

    def __init__(self):
        self.supported_formats = [".pdf", ".docx", ".txt", ".doc", ".rtf"]

    def parse_resume(
        self,
        file_path: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse resume from file.

        Args:
            file_path: Path to resume file
            file_type: File extension (auto-detected if not provided)

        Returns:
            Parsed resume data
        """
        if not file_type:
            file_type = os.path.splitext(file_path)[1].lower()

        # Extract text based on format
        if file_type == ".pdf":
            text = self._parse_pdf(file_path)
        elif file_type in [".docx", ".doc"]:
            text = self._parse_docx(file_path)
        elif file_type == ".txt":
            text = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_type}")

        # Parse structured data from text
        parsed_data = self._extract_structured_data(text)

        return {
            "raw_text": text,
            **parsed_data,
            "parsed_at": datetime.now().isoformat(),
            "source_file": file_path,
            "file_type": file_type
        }

    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF resume."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")

    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX resume."""
        try:
            import docx

            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")

    def _parse_txt(self, file_path: str) -> str:
        """Parse text resume."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured information from resume text."""
        return {
            "contact_info": self._extract_contact_info(text),
            "education": self._extract_education(text),
            "experience": self._extract_experience(text),
            "skills": self._extract_skills(text),
            "summary": self._extract_summary(text),
            "certifications": self._extract_certifications(text),
            "years_of_experience": self._estimate_years_of_experience(text)
        }

    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        github_pattern = r'github\.com/[\w-]+'

        email = re.search(email_pattern, text)
        phone = re.search(phone_pattern, text)
        linkedin = re.search(linkedin_pattern, text)
        github = re.search(github_pattern, text)

        # Extract name (first few lines usually)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        name = lines[0] if lines else None

        return {
            "name": name,
            "email": email.group() if email else None,
            "phone": phone.group() if phone else None,
            "linkedin_url": f"https://{linkedin.group()}" if linkedin else None,
            "github_url": f"https://{github.group()}" if github else None
        }

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education history."""
        education = []

        # Common degree patterns
        degree_patterns = [
            r'(B\.?S\.?|Bachelor|M\.?S\.?|Master|Ph\.?D\.?|MBA|Associate)\s+(?:of\s+)?(?:Science|Arts|Engineering|Business|Computer Science)?',
            r'(Bachelor\'s|Master\'s|Doctorate)'
        ]

        # University patterns
        university_keywords = ['university', 'college', 'institute', 'school']

        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Check if line contains degree or university keywords
            lower_line = line.lower()

            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    education.append({
                        "degree": line.strip(),
                        "institution": None,  # Would need more sophisticated parsing
                        "year": self._extract_year(line),
                        "field": None
                    })
                    break

        return education

    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience."""
        experience = []

        # Look for common experience section headers
        exp_keywords = ['experience', 'employment', 'work history', 'professional experience']

        # This is simplified - real implementation would be more sophisticated
        # Could use NLP to identify job titles, companies, dates, responsibilities

        return experience  # Placeholder

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume."""
        # Common technical skills database
        common_skills = [
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',

            # Frameworks & Libraries
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'node.js',
            'express', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',

            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'oracle',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',
            'ansible', 'git', 'github', 'gitlab',

            # Other
            'agile', 'scrum', 'machine learning', 'deep learning', 'nlp', 'data science',
            'api design', 'microservices', 'rest', 'graphql'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill.title())

        return list(set(found_skills))  # Remove duplicates

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary."""
        summary_keywords = ['summary', 'objective', 'profile', 'about']

        lines = text.split('\n')
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()

            # Check if this is a summary section header
            if any(keyword in lower_line for keyword in summary_keywords):
                # Take next few lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break

                if summary_lines:
                    return ' '.join(summary_lines)

        return None

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        cert_keywords = [
            'certified', 'certification', 'certificate',
            'AWS', 'Azure', 'GCP', 'PMP', 'CISSP', 'CPA', 'CFA'
        ]

        certifications = []
        lines = text.split('\n')

        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in cert_keywords):
                certifications.append(line.strip())

        return certifications

    def _estimate_years_of_experience(self, text: str) -> Optional[float]:
        """Estimate total years of experience."""
        # Extract years from text
        years = re.findall(r'\b(19|20)\d{2}\b', text)

        if len(years) >= 2:
            years_int = [int(y) for y in years]
            earliest = min(years_int)
            latest = max(years_int)

            # Estimate experience
            experience_years = datetime.now().year - earliest

            # Cap at reasonable range
            return min(experience_years, 50)

        return None

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text."""
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        return int(year_match.group()) if year_match else None

    def parse_linkedin_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LinkedIn profile data."""
        return {
            "contact_info": {
                "name": profile_data.get("name"),
                "email": profile_data.get("email"),
                "linkedin_url": profile_data.get("profile_url"),
                "location": profile_data.get("location")
            },
            "current_title": profile_data.get("headline"),
            "summary": profile_data.get("summary"),
            "experience": profile_data.get("positions", []),
            "education": profile_data.get("education", []),
            "skills": profile_data.get("skills", []),
            "years_of_experience": self._calculate_linkedin_experience(
                profile_data.get("positions", [])
            )
        }

    def _calculate_linkedin_experience(self, positions: List[Dict]) -> Optional[float]:
        """Calculate years of experience from LinkedIn positions."""
        if not positions:
            return None

        # Sum up all position durations
        total_months = 0

        for position in positions:
            start = position.get("start_date")
            end = position.get("end_date") or datetime.now()

            # Calculate duration (simplified)
            # Real implementation would parse dates properly

        return total_months / 12 if total_months > 0 else None

    def detect_duplicate_candidates(
        self,
        candidate1: Dict[str, Any],
        candidate2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect if two candidates are duplicates."""
        score = 0
        matches = []

        # Email match (strongest signal)
        if candidate1.get("contact_info", {}).get("email") == candidate2.get("contact_info", {}).get("email"):
            score += 100
            matches.append("email")

        # Name similarity
        name1 = candidate1.get("contact_info", {}).get("name", "").lower()
        name2 = candidate2.get("contact_info", {}).get("name", "").lower()

        if name1 and name2 and name1 == name2:
            score += 50
            matches.append("name")

        # Phone match
        phone1 = candidate1.get("contact_info", {}).get("phone", "")
        phone2 = candidate2.get("contact_info", {}).get("phone", "")

        if phone1 and phone2:
            # Normalize phones (remove formatting)
            phone1_clean = re.sub(r'[^\d]', '', phone1)
            phone2_clean = re.sub(r'[^\d]', '', phone2)

            if phone1_clean == phone2_clean:
                score += 80
                matches.append("phone")

        # LinkedIn match
        if candidate1.get("contact_info", {}).get("linkedin_url") == candidate2.get("contact_info", {}).get("linkedin_url"):
            score += 70
            matches.append("linkedin")

        is_duplicate = score >= 100  # Threshold for duplicate

        return {
            "is_duplicate": is_duplicate,
            "confidence_score": min(score, 100),
            "matching_fields": matches
        }
