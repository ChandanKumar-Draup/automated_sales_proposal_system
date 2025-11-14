"""Enhanced embedding service with multi-model support."""
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings


class EmbeddingService:
    """Advanced embedding service with multiple model support."""

    def __init__(
        self,
        primary_model: str = None,
        use_openai: bool = False,
        openai_model: str = "text-embedding-3-small",
    ):
        """Initialize embedding service."""
        self.use_openai = use_openai
        self.openai_model = openai_model

        if use_openai:
            try:
                from openai import OpenAI
                import os

                api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                self.openai_client = OpenAI(api_key=api_key)
                print(f"Using OpenAI embeddings: {openai_model}")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}. Falling back to sentence-transformers")
                self.use_openai = False

        if not self.use_openai:
            model_name = primary_model or settings.embedding_model
            self.encoder = SentenceTransformer(model_name)
            self.dimension = self.encoder.get_sentence_embedding_dimension()
            print(f"Using sentence-transformers: {model_name} (dim={self.dimension})")

    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text."""
        if self.use_openai:
            return self._embed_openai([text])[0]
        else:
            return self.encoder.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed multiple texts efficiently."""
        if self.use_openai:
            return self._embed_openai(texts)
        else:
            return self.encoder.encode(
                texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True
            )

    def _embed_openai(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI."""
        try:
            # OpenAI allows batch up to 2048 texts
            all_embeddings = []

            for i in range(0, len(texts), 2048):
                batch = texts[i : i + 2048]
                response = self.openai_client.embeddings.create(input=batch, model=self.openai_model)
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)

            return np.array(all_embeddings, dtype=np.float32)
        except Exception as e:
            raise Exception(f"OpenAI embedding failed: {str(e)}")

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.use_openai:
            # text-embedding-3-small: 1536, text-embedding-3-large: 3072
            return 1536 if "small" in self.openai_model else 3072
        else:
            return self.dimension


class ChunkingStrategy:
    """Advanced chunking strategies for documents."""

    @staticmethod
    def structural_chunk(text: str, max_chunk_size: int = 512) -> List[Dict[str, Any]]:
        """
        Chunk by structure (sections, Q&A pairs).

        Looks for patterns like:
        - Q1: Question text
        - A1: Answer text
        - Section headers
        - Numbered lists
        """
        chunks = []

        # Pattern 1: Numbered Q&A pairs
        import re

        # Find all Q&A patterns
        qa_pattern = r"(?:Q\d+|Question \d+|^\d+\.)\s*:?\s*(.+?)(?=(?:Q\d+|Question \d+|^\d+\.)|$)"
        matches = re.finditer(qa_pattern, text, re.MULTILINE | re.DOTALL)

        for match in matches:
            question_text = match.group(1).strip()
            if len(question_text) > 50:  # Meaningful question
                chunks.append({"text": question_text, "type": "qa_pair", "size": len(question_text)})

        # If no Q&A found, fall back to semantic chunking
        if not chunks:
            chunks = ChunkingStrategy.semantic_chunk(text, max_chunk_size)

        return chunks

    @staticmethod
    def semantic_chunk(text: str, max_chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Chunk by semantic boundaries (paragraphs, sentences).
        """
        chunks = []
        paragraphs = text.split("\n\n")

        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this para exceeds limit, save current chunk
            if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                chunks.append({"text": current_chunk.strip(), "type": "semantic", "size": len(current_chunk)})

                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else ""
                current_chunk = overlap_text + " " + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add final chunk
        if current_chunk:
            chunks.append({"text": current_chunk.strip(), "type": "semantic", "size": len(current_chunk)})

        return chunks

    @staticmethod
    def hybrid_chunk(text: str, max_chunk_size: int = 512) -> List[Dict[str, Any]]:
        """
        Try structural first, fall back to semantic.
        """
        # Try structural chunking
        chunks = ChunkingStrategy.structural_chunk(text, max_chunk_size)

        # If chunks too large, apply semantic chunking to each
        final_chunks = []
        for chunk in chunks:
            if chunk["size"] > max_chunk_size:
                sub_chunks = ChunkingStrategy.semantic_chunk(chunk["text"], max_chunk_size)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)

        return final_chunks
