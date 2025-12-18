"""Tests for RAG components."""

import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore
from langchain_core.documents import Document


class TestDocumentLoader:
    """Tests for the DocumentLoader class."""

    def test_loader_initialization(self):
        """Test document loader initializes with default settings."""
        loader = DocumentLoader()
        assert loader.chunk_size == 1000
        assert loader.chunk_overlap == 200

    def test_loader_custom_settings(self):
        """Test document loader with custom settings."""
        loader = DocumentLoader(chunk_size=500, chunk_overlap=50)
        assert loader.chunk_size == 500
        assert loader.chunk_overlap == 50

    def test_load_text_file(self):
        """Test loading a text file."""
        loader = DocumentLoader()

        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test resume.\n" * 100)
            temp_path = f.name

        try:
            text = loader.load_text(temp_path)
            assert "test resume" in text
            assert len(text) > 0
        finally:
            os.unlink(temp_path)

    def test_load_document_with_metadata(self):
        """Test loading document with metadata."""
        loader = DocumentLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Senior Python Developer with experience in Django and FastAPI.\n" * 50)
            temp_path = f.name

        try:
            docs = loader.load_document(
                temp_path,
                metadata={"type": "resume", "candidate": "John Doe"}
            )

            assert len(docs) > 0
            assert docs[0].metadata.get("type") == "resume"
            assert docs[0].metadata.get("candidate") == "John Doe"
            assert "source" in docs[0].metadata
        finally:
            os.unlink(temp_path)

    def test_load_document_chunking(self):
        """Test that long documents are properly chunked."""
        loader = DocumentLoader(chunk_size=100, chunk_overlap=20)

        # Create a document longer than chunk size
        long_text = "Python developer. " * 100  # ~1800 chars

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(long_text)
            temp_path = f.name

        try:
            docs = loader.load_document(temp_path)
            assert len(docs) > 1  # Should be chunked
            assert docs[0].metadata.get("chunk_index") == 0
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        loader = DocumentLoader()

        with pytest.raises(FileNotFoundError):
            loader.load_document("/nonexistent/path/file.txt")

    def test_json_to_text_conversion(self):
        """Test JSON to text conversion."""
        loader = DocumentLoader()

        data = {
            "name": "John Doe",
            "skills": ["Python", "Django"]
        }

        text = loader._json_to_text(data)
        assert "Name:" in text
        assert "Skills:" in text


class TestVectorStore:
    """Tests for the VectorStore class."""

    @pytest.fixture
    def temp_vector_store(self):
        """Create a temporary vector store for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(
                collection_name="test_collection",
                persist_directory=temp_dir
            )
            yield store
            # Cleanup handled by context manager

    def test_vector_store_initialization(self, temp_vector_store):
        """Test vector store initializes correctly."""
        assert temp_vector_store.collection is not None
        assert temp_vector_store.embeddings is not None

    def test_add_documents(self, temp_vector_store):
        """Test adding documents to vector store."""
        docs = [
            Document(page_content="Python developer", metadata={"type": "resume"}),
            Document(page_content="Java developer", metadata={"type": "resume"})
        ]

        count = temp_vector_store.add_documents(docs)
        assert count == 2
        assert temp_vector_store.get_document_count() == 2

    def test_add_empty_documents(self, temp_vector_store):
        """Test adding empty document list."""
        count = temp_vector_store.add_documents([])
        assert count == 0

    def test_get_document_count(self, temp_vector_store):
        """Test document count retrieval."""
        # Initially empty
        assert temp_vector_store.get_document_count() == 0

        # Add a document
        temp_vector_store.add_documents([
            Document(page_content="Test content", metadata={})
        ])

        assert temp_vector_store.get_document_count() == 1

    def test_reset_collection(self, temp_vector_store):
        """Test resetting the collection."""
        # Add documents
        temp_vector_store.add_documents([
            Document(page_content="Test", metadata={})
        ])
        assert temp_vector_store.get_document_count() == 1

        # Reset
        temp_vector_store.reset()
        assert temp_vector_store.get_document_count() == 0


class TestRAGIntegration:
    """Integration tests for RAG components."""

    def test_loader_to_store_pipeline(self):
        """Test the complete pipeline from loader to store."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "resume.txt")
            with open(test_file, 'w') as f:
                f.write("Experienced Python developer with Django expertise.\n" * 20)

            # Create vector store in temp dir
            store_dir = os.path.join(temp_dir, "vector_store")
            os.makedirs(store_dir)

            loader = DocumentLoader(chunk_size=100)
            store = VectorStore(
                collection_name="integration_test",
                persist_directory=store_dir
            )

            # Load and add
            docs = loader.load_document(test_file, metadata={"type": "resume"})
            store.add_documents(docs)

            assert store.get_document_count() > 0


# Run with: pytest tests/test_rag.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
