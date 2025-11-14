"""Batch ingestion script for RFP knowledge base."""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService, ChunkingStrategy
from services.metadata_extractor import MetadataExtractor, ClientMatcher
from config import settings


class RFPKnowledgeIngestion:
    """Batch ingestion pipeline for RFP documents."""

    def __init__(self, use_openai_embeddings: bool = False, use_gemini_embeddings: bool = False):
        """Initialize ingestion pipeline."""
        print("Initializing RFP Knowledge Ingestion Pipeline...")

        self.llm = LLMService()
        self.doc_processor = DocumentProcessor()
        self.metadata_extractor = MetadataExtractor(self.llm)
        self.embedding_service = EmbeddingService(
            use_openai=use_openai_embeddings,
            use_gemini=use_gemini_embeddings
        )
        self.vector_store = VectorStore()
        self.chunking = ChunkingStrategy()

        self.stats = {
            "total_files": 0,
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "clients": set(),
        }

    def discover_documents(self, root_dir: str = "resources/RFP_Hackathon") -> List[str]:
        """
        Discover all RFP documents.
        """
        supported_extensions = [".pdf", ".docx", ".doc", ".txt"]
        documents = []

        root_path = Path(root_dir)
        if not root_path.exists():
            print(f"Warning: Directory {root_dir} not found!")
            return []

        for ext in supported_extensions:
            pattern = f"**/*{ext}"
            files = list(root_path.glob(pattern))
            documents.extend([str(f) for f in files])

        print(f"Discovered {len(documents)} documents")
        return documents

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document: extract text, metadata, chunk, embed.
        """
        try:
            # Step 1: Extract text
            text = self.doc_processor.extract_text(file_path)
            if not text or len(text) < 50:
                print(f"Skipping {file_path}: No meaningful content")
                return None

            # Step 2: Extract metadata
            metadata = self.metadata_extractor.extract_complete_metadata(file_path, text)

            # Step 3: Chunk document
            chunks = self.chunking.hybrid_chunk(text, max_chunk_size=800)

            # Step 4: Generate embeddings for chunks
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_service.embed_batch(chunk_texts)

            # Step 5: Prepare for vector store
            doc_data = {
                "file_path": file_path,
                "metadata": metadata,
                "chunks": chunks,
                "embeddings": embeddings,
                "num_chunks": len(chunks),
            }

            self.stats["total_chunks"] += len(chunks)
            if metadata.get("client_name"):
                self.stats["clients"].add(metadata["client_name"])

            return doc_data

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            self.stats["failed"] += 1
            return None

    def add_to_vector_store(self, doc_data: Dict[str, Any]):
        """
        Add processed document to vector store.
        """
        if not doc_data:
            return

        # Add each chunk to vector store
        for i, (chunk, embedding) in enumerate(zip(doc_data["chunks"], doc_data["embeddings"])):
            # Prepare chunk metadata
            chunk_metadata = {
                **doc_data["metadata"],
                "chunk_id": i,
                "chunk_type": chunk.get("type", "unknown"),
                "chunk_size": chunk.get("size", 0),
            }

            # Add to vector store (but don't embed again, we already have embeddings)
            # We need to add directly to FAISS
            pass  # This requires modifying VectorStore to accept pre-computed embeddings

        # For now, use the existing add_documents method
        chunk_texts = [chunk["text"] for chunk in doc_data["chunks"]]
        chunk_metadata_list = [
            {
                **doc_data["metadata"],
                "chunk_id": i,
                "chunk_type": chunk.get("type", "unknown"),
            }
            for i, chunk in enumerate(doc_data["chunks"])
        ]

        self.vector_store.add_documents(chunk_texts, chunk_metadata_list)

    def link_rfp_pairs(self, all_metadata: List[Dict[str, Any]]):
        """
        Link RFP requests to responses.
        """
        print("\nLinking RFP pairs...")

        # Group by client
        by_client = {}
        for meta in all_metadata:
            client = meta.get("client_name", "Unknown")
            if client not in by_client:
                by_client[client] = []
            by_client[client].append(meta)

        # For each client, link received to response
        linked_count = 0
        for client, docs in by_client.items():
            received = [d for d in docs if d.get("doc_type") == "rfp_received"]
            responses = [d for d in docs if d.get("doc_type") == "rfp_response"]

            for rfp in received:
                for response in responses:
                    if ClientMatcher.link_rfp_to_response(rfp, response):
                        # Store bidirectional link
                        rfp["linked_response"] = response["file_path"]
                        response["linked_request"] = rfp["file_path"]
                        linked_count += 1

        print(f"Linked {linked_count} RFP-Response pairs")

    def run(self, root_dir: str = "resources/RFP_Hackathon", dry_run: bool = False):
        """
        Run the complete ingestion pipeline.
        """
        print("=" * 80)
        print("RFP KNOWLEDGE BASE INGESTION")
        print("=" * 80)

        # Step 1: Discover documents
        documents = self.discover_documents(root_dir)
        self.stats["total_files"] = len(documents)

        if not documents:
            print("No documents found!")
            return

        if dry_run:
            print("\nDRY RUN MODE - Files that would be processed:")
            for doc in documents[:10]:
                print(f"  - {doc}")
            print(f"  ... and {len(documents) - 10} more")
            return

        # Step 2: Process each document
        print(f"\nProcessing {len(documents)} documents...")
        all_doc_data = []
        all_metadata = []

        for file_path in tqdm(documents, desc="Processing documents"):
            doc_data = self.process_document(file_path)
            if doc_data:
                all_doc_data.append(doc_data)
                all_metadata.append(doc_data["metadata"])
                self.stats["processed"] += 1

        # Step 3: Link RFP pairs
        self.link_rfp_pairs(all_metadata)

        # Step 4: Add to vector store
        print("\nAdding to vector store...")
        for doc_data in tqdm(all_doc_data, desc="Indexing"):
            self.add_to_vector_store(doc_data)

        # Step 5: Save vector store
        print("\nSaving vector store...")
        self.vector_store.save()

        # Step 6: Save metadata separately
        metadata_file = f"{settings.vector_store_path}/rfp_metadata.json"
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=2, default=str)

        # Print statistics
        self.print_stats()

    def print_stats(self):
        """Print ingestion statistics."""
        print("\n" + "=" * 80)
        print("INGESTION COMPLETE")
        print("=" * 80)
        print(f"Total files discovered: {self.stats['total_files']}")
        print(f"Successfully processed: {self.stats['processed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Total chunks created: {self.stats['total_chunks']}")
        print(f"Avg chunks per doc: {self.stats['total_chunks'] / max(self.stats['processed'], 1):.1f}")
        print(f"Unique clients: {len(self.stats['clients'])}")
        print(f"Clients: {', '.join(sorted(self.stats['clients']))}")
        print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest RFP documents into knowledge base")
    parser.add_argument("--dry-run", action="store_true", help="Preview files without processing")
    parser.add_argument("--use-openai", action="store_true", help="Use OpenAI embeddings (higher quality)")
    parser.add_argument("--use-gemini", action="store_true", help="Use Google Gemini embeddings (alternative to OpenAI)")
    parser.add_argument("--root-dir", default="resources/RFP_Hackathon", help="Root directory of RFP files")

    args = parser.parse_args()

    # Run ingestion
    pipeline = RFPKnowledgeIngestion(
        use_openai_embeddings=args.use_openai,
        use_gemini_embeddings=args.use_gemini
    )
    pipeline.run(root_dir=args.root_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
