"""Embedding generation utilities."""

from typing import List
from langchain_openai import OpenAIEmbeddings
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class EmbeddingGenerator:
    """Generate embeddings for text content."""

    def __init__(self, model: str = None):
        """
        Initialize the embedding generator.

        Args:
            model: Embedding model name (default from settings)
        """
        self.model = model or settings.EMBEDDING_MODEL
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=settings.OPENAI_API_KEY
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Embedding dimension (1536 for text-embedding-3-small)
        """
        # text-embedding-3-small produces 1536-dimensional vectors
        return 1536
