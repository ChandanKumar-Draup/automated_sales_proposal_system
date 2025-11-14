"""Vector store for semantic search using FAISS."""
import os
import pickle
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings


class VectorStore:
    """Vector store for embeddings and semantic search."""

    def __init__(self, model_name: Optional[str] = None, store_path: Optional[str] = None):
        """Initialize vector store."""
        self.model_name = model_name or settings.embedding_model
        self.store_path = store_path or settings.vector_store_path
        self.encoder = SentenceTransformer(self.model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one."""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)

        index_file = f"{self.store_path}/faiss.index"
        docs_file = f"{self.store_path}/documents.pkl"
        meta_file = f"{self.store_path}/metadata.pkl"

        if os.path.exists(index_file):
            try:
                import faiss

                self.index = faiss.read_index(index_file)
                with open(docs_file, "rb") as f:
                    self.documents = pickle.load(f)
                with open(meta_file, "rb") as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded existing index with {len(self.documents)} documents")
            except Exception as e:
                print(f"Failed to load index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        import faiss

        # Create a flat L2 index (simple but works well for small datasets)
        dimension = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
        print(f"Created new FAISS index with dimension {dimension}")

    def add_documents(self, documents: List[str], metadata: Optional[List[Dict[str, Any]]] = None):
        """Add documents to the vector store."""
        if not documents:
            return

        # Generate embeddings
        embeddings = self.encoder.encode(documents, convert_to_numpy=True)

        # Add to FAISS index
        self.index.add(embeddings.astype("float32"))

        # Store documents and metadata
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))

        print(f"Added {len(documents)} documents. Total: {len(self.documents)}")

    def search(self, query: str, top_k: Optional[int] = None, filters: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar documents."""
        k = top_k or settings.top_k_results

        if len(self.documents) == 0:
            return []

        # Encode query
        query_embedding = self.encoder.encode([query], convert_to_numpy=True).astype("float32")

        # Search in FAISS
        # FAISS returns distances, we convert to similarity scores
        distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (inverse)
                # Normalize to 0-1 range
                similarity = 1 / (1 + distance)

                doc = self.documents[idx]
                meta = self.metadata[idx] if idx < len(self.metadata) else {}

                # Apply filters if provided
                if filters:
                    match = all(meta.get(k) == v for k, v in filters.items() if k in meta)
                    if not match:
                        continue

                results.append((doc, float(similarity), meta))

        return results

    def save(self):
        """Save the index to disk."""
        import faiss

        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)

        index_file = f"{self.store_path}/faiss.index"
        docs_file = f"{self.store_path}/documents.pkl"
        meta_file = f"{self.store_path}/metadata.pkl"

        faiss.write_index(self.index, index_file)
        with open(docs_file, "wb") as f:
            pickle.dump(self.documents, f)
        with open(meta_file, "wb") as f:
            pickle.dump(self.metadata, f)

        print(f"Saved index with {len(self.documents)} documents")

    def clear(self):
        """Clear the index."""
        self._create_new_index()
        self.save()
