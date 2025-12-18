"""Document loading and chunking utilities."""

from pathlib import Path
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class DocumentLoader:
    """Load and chunk documents for the hiring assistant."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize the document loader.

        Args:
            chunk_size: Size of text chunks (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", ", ", " ", ""],
            length_function=len
        )

    def load_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        reader = PdfReader(file_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)

    def load_text(self, file_path: str) -> str:
        """
        Load text from a file.

        Args:
            file_path: Path to the text file

        Returns:
            File content as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_json(self, file_path: str) -> str:
        """
        Load and format JSON file content.

        Args:
            file_path: Path to the JSON file

        Returns:
            Formatted JSON content as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert JSON to readable text
        if isinstance(data, dict):
            return self._json_to_text(data)
        elif isinstance(data, list):
            return "\n\n".join(self._json_to_text(item) for item in data)
        return json.dumps(data, indent=2)

    def _json_to_text(self, data: Dict[str, Any]) -> str:
        """Convert a JSON object to readable text."""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)

    def load_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Load and chunk a document.

        Args:
            file_path: Path to the document
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Document objects (chunks)
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Load based on file type
        suffix = path.suffix.lower()
        if suffix == '.pdf':
            text = self.load_pdf(file_path)
        elif suffix == '.json':
            text = self.load_json(file_path)
        else:
            text = self.load_text(file_path)

        # Prepare metadata
        doc_metadata = metadata.copy() if metadata else {}
        doc_metadata["source"] = path.name
        doc_metadata["file_path"] = str(path.absolute())

        # Split into chunks
        chunks = self.text_splitter.split_text(text)

        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = doc_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            documents.append(Document(page_content=chunk, metadata=chunk_metadata))

        return documents

    def load_directory(
        self,
        dir_path: str,
        doc_type: str = "resume",
        file_extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Load all documents from a directory.

        Args:
            dir_path: Path to the directory
            doc_type: Type of documents (for metadata)
            file_extensions: List of extensions to include (default: pdf, txt, md, json)

        Returns:
            List of all Document chunks
        """
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")

        # Default extensions
        if file_extensions is None:
            file_extensions = ['.pdf', '.txt', '.md', '.json']

        documents = []

        for file_path in path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    docs = self.load_document(
                        str(file_path),
                        metadata={"type": doc_type}
                    )
                    documents.extend(docs)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")

        return documents

    def load_resume(self, file_path: str, candidate_name: str = None) -> List[Document]:
        """
        Load a resume with appropriate metadata.

        Args:
            file_path: Path to the resume file
            candidate_name: Optional candidate name

        Returns:
            List of Document chunks
        """
        metadata = {
            "type": "resume",
            "candidate_name": candidate_name or Path(file_path).stem
        }
        return self.load_document(file_path, metadata)

    def load_job_description(
        self,
        file_path: str,
        job_title: str = None
    ) -> List[Document]:
        """
        Load a job description with appropriate metadata.

        Args:
            file_path: Path to the job description file
            job_title: Optional job title

        Returns:
            List of Document chunks
        """
        metadata = {
            "type": "job_description",
            "job_title": job_title or Path(file_path).stem
        }
        return self.load_document(file_path, metadata)
