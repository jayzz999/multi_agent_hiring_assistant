"""RAG retriever tool for searching candidate documents."""

from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.rag.vector_store import VectorStore


class RAGRetrieverInput(BaseModel):
    """Input schema for RAG retriever tool."""
    query: str = Field(description="The search query to find matching candidates")
    doc_type: Optional[str] = Field(
        default=None,
        description="Document type to filter by (e.g., 'resume', 'job_description')"
    )


class RAGRetrieverTool(BaseTool):
    """Tool for searching through the resume/document database."""

    name: str = "resume_search"
    description: str = """
    Search through the resume database to find candidates matching specific criteria.
    Input should be a natural language query describing the skills, experience, or
    qualifications you're looking for.

    Examples:
    - "Find Python developers with 5 years of experience"
    - "Candidates with machine learning and data science background"
    - "Software engineers with AWS certification"
    """
    args_schema: Type[BaseModel] = RAGRetrieverInput
    vector_store: VectorStore = None

    def __init__(self, vector_store: VectorStore = None, **kwargs):
        """Initialize with optional vector store."""
        super().__init__(**kwargs)
        self.vector_store = vector_store or VectorStore()

    def _run(
        self,
        query: str,
        doc_type: Optional[str] = None
    ) -> str:
        """
        Execute the search.

        Args:
            query: Search query
            doc_type: Optional document type filter

        Returns:
            Formatted search results
        """
        # Build filter
        filter_dict = {"type": doc_type} if doc_type else None

        # Perform search
        results = self.vector_store.similarity_search_with_scores(
            query=query,
            k=5,
            filter_dict=filter_dict
        )

        if not results:
            return "No matching candidates found in the database."

        # Format results
        output_parts = ["Found the following relevant information:\n"]

        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            candidate_name = doc.metadata.get('candidate_name', 'Unknown')
            doc_type_found = doc.metadata.get('type', 'document')

            output_parts.append(f"--- Result {i} ---")
            output_parts.append(f"Source: {source}")
            if candidate_name != 'Unknown':
                output_parts.append(f"Candidate: {candidate_name}")
            output_parts.append(f"Type: {doc_type_found}")
            output_parts.append(f"Relevance Score: {score:.2f}")
            output_parts.append(f"\n{doc.page_content}\n")

        return "\n".join(output_parts)

    async def _arun(
        self,
        query: str,
        doc_type: Optional[str] = None
    ) -> str:
        """Async version of _run."""
        return self._run(query, doc_type)
