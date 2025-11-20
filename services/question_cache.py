"""File-based caching service for RFP question extraction.

This service provides a simple file-based cache to avoid redundant LLM calls
for the same RFP documents.
"""
import json
import hashlib
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class QuestionCache:
    """File-based cache for extracted questions.

    Uses content hashing to determine cache keys, storing results as JSON files.
    """

    def __init__(self, cache_dir: str = "./data/cache/questions"):
        """Initialize the question cache.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, document_text: str) -> str:
        """Generate a cache key from document text.

        Args:
            document_text: Full text of the RFP document

        Returns:
            Hash string to use as cache key
        """
        # Create hash of the document text
        text_hash = hashlib.sha256(document_text.encode('utf-8')).hexdigest()
        return text_hash[:16]  # Use first 16 chars for readability

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key.

        Args:
            cache_key: Cache key identifier

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def get(self, document_text: str) -> Optional[List[str]]:
        """Retrieve cached questions for a document.

        Args:
            document_text: Full text of the RFP document

        Returns:
            List of questions if cached, None otherwise
        """
        cache_key = self._generate_cache_key(document_text)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            print(f"[Cache] MISS - No cached questions for key {cache_key}")
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            questions = cache_data.get('questions', [])
            cached_at = cache_data.get('cached_at', 'unknown')

            print(f"[Cache] HIT - Found {len(questions)} cached questions (key: {cache_key}, cached: {cached_at})")
            return questions

        except Exception as e:
            print(f"[Cache] ERROR - Failed to read cache: {e}")
            return None

    def set(self, document_text: str, questions: List[str]) -> bool:
        """Store questions in cache for a document.

        Args:
            document_text: Full text of the RFP document
            questions: Extracted questions to cache

        Returns:
            True if caching succeeded, False otherwise
        """
        cache_key = self._generate_cache_key(document_text)
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                'questions': questions,
                'cached_at': datetime.utcnow().isoformat(),
                'question_count': len(questions),
                'document_length': len(document_text)
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            print(f"[Cache] SAVED - Cached {len(questions)} questions (key: {cache_key})")
            return True

        except Exception as e:
            print(f"[Cache] ERROR - Failed to write cache: {e}")
            return False

    def clear(self) -> int:
        """Clear all cached questions.

        Returns:
            Number of cache files deleted
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            print(f"[Cache] CLEARED - Removed {count} cache files")
            return count
        except Exception as e:
            print(f"[Cache] ERROR - Failed to clear cache: {e}")
            return count

    def get_cache_stats(self) -> dict:
        """Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                'cache_count': len(cache_files),
                'total_size_bytes': total_size,
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            print(f"[Cache] ERROR - Failed to get stats: {e}")
            return {
                'cache_count': 0,
                'total_size_bytes': 0,
                'cache_dir': str(self.cache_dir)
            }
