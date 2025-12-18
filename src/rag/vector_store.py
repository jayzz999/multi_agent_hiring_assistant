"""Vector store operations using ChromaDB."""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class VectorStore:
    """ChromaDB-based vector store for document retrieval."""

    def __init__(
        self,
        collection_name: str = "hiring_assistant",
        persist_directory: str = None
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Ensure persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects to add
            batch_size: Number of documents to process at once

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        # Process in batches
        total_added = 0
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]

            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)

            # Generate unique IDs
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + j}" for j in range(len(batch))]

            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            total_added += len(batch)

        return total_added

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Add raw texts to the vector store.

        Args:
            texts: List of text strings
            metadatas: Optional list of metadata dicts

        Returns:
            Number of texts added
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]

        documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]

        return self.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional filter criteria

        Returns:
            List of matching Documents
        """
        k = k or settings.TOP_K_RESULTS

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict
        )

        # Convert to Document objects
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc_text in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                # Add distance/similarity score to metadata
                if results.get('distances') and results['distances'][0]:
                    metadata['distance'] = results['distances'][0][i]
                documents.append(Document(page_content=doc_text, metadata=metadata))

        return documents

    def similarity_search_with_scores(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        Search for similar documents with similarity scores.

        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional filter criteria

        Returns:
            List of (Document, score) tuples
        """
        k = k or settings.TOP_K_RESULTS

        query_embedding = self.embeddings.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict,
            include=['documents', 'metadatas', 'distances']
        )

        documents_with_scores = []
        if results['documents'] and results['documents'][0]:
            for i, doc_text in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                doc = Document(page_content=doc_text, metadata=metadata)
                # ChromaDB returns distance (lower is better), convert to similarity
                distance = results['distances'][0][i] if results.get('distances') else 0
                similarity = 1 - distance  # Convert cosine distance to similarity
                documents_with_scores.append((doc, similarity))

        return documents_with_scores

    def get_document_count(self) -> int:
        """Get the total number of documents in the collection."""
        return self.collection.count()

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass  # Collection may not exist

    def reset(self) -> None:
        """Reset the collection (delete and recreate)."""
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def get_all_documents(
        self,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Get all documents from the collection.

        Args:
            filter_dict: Optional filter criteria

        Returns:
            List of all Documents
        """
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.get(
            where=filter_dict,
            include=['documents', 'metadatas']
        )

        documents = []
        if results['documents']:
            for i, doc_text in enumerate(results['documents']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                documents.append(Document(page_content=doc_text, metadata=metadata))

        return documents
