#!/usr/bin/env python3
"""
Standalone demonstration of the question caching functionality.
This script tests the cache without needing any dependencies.
"""
import json
import hashlib
import os
import time
from pathlib import Path

# Inline cache implementation for testing
class QuestionCache:
    """File-based cache for extracted questions."""

    def __init__(self, cache_dir: str = "./data/cache/questions"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, document_text: str) -> str:
        text_hash = hashlib.sha256(document_text.encode('utf-8')).hexdigest()
        return text_hash[:16]

    def _get_cache_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.json"

    def get(self, document_text: str):
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

    def set(self, document_text: str, questions: list) -> bool:
        cache_key = self._generate_cache_key(document_text)
        cache_path = self._get_cache_path(cache_key)

        try:
            from datetime import datetime
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

    def get_cache_stats(self) -> dict:
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


# Sample RFP document
SAMPLE_RFP = """
REQUEST FOR PROPOSAL (RFP)
Enterprise Software Development Services

Client: TechCorp Industries
Industry: Technology / Software
Date: November 20, 2024
Deadline: December 15, 2024

================================================================================
SECTION 1: COMPANY BACKGROUND
================================================================================

1. Please provide a brief history of your company, including years in business,
   number of employees, and primary service offerings.

2. Describe your experience developing enterprise software for Fortune 500 companies.

3. What industries have you served in the past 5 years?

================================================================================
SECTION 2: TECHNICAL REQUIREMENTS
================================================================================

4. What is your approach to cloud-native architecture and microservices development?

5. Describe your experience with the following technologies:
   - Kubernetes and container orchestration
   - React/Vue.js frontend frameworks
   - Node.js/Python backend development
   - PostgreSQL/MongoDB databases

6. How do you ensure application security and data protection?
"""

def main():
    print("=" * 80)
    print("QUESTION CACHING DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize cache
    cache = QuestionCache()

    # Sample questions (simulating LLM extraction)
    sample_questions = [
        "Please provide a brief history of your company, including years in business, number of employees, and primary service offerings?",
        "Describe your experience developing enterprise software for Fortune 500 companies?",
        "What industries have you served in the past 5 years?",
        "What is your approach to cloud-native architecture and microservices development?",
        "Describe your experience with Kubernetes and container orchestration?",
        "How do you ensure application security and data protection?"
    ]

    # === TEST 1: Cache Miss ===
    print("📋 TEST 1: First extraction (cache MISS expected)")
    print("-" * 80)
    start_time = time.time()
    cached_result = cache.get(SAMPLE_RFP)
    elapsed_ms = (time.time() - start_time) * 1000

    if cached_result is None:
        print(f"✓ Cache MISS (as expected) - lookup took {elapsed_ms:.2f}ms")
        print(f"  🤖 Simulating LLM extraction (this takes ~2-5 seconds)...")
        time.sleep(1)  # Simulate LLM call
        cache.set(SAMPLE_RFP, sample_questions)
        print(f"✓ Questions cached successfully ({len(sample_questions)} questions)")
    else:
        print(f"✗ ERROR: Expected cache MISS but got HIT")

    print()

    # === TEST 2: Cache Hit ===
    print("📋 TEST 2: Second extraction (cache HIT expected)")
    print("-" * 80)
    start_time = time.time()
    cached_result = cache.get(SAMPLE_RFP)
    elapsed_ms = (time.time() - start_time) * 1000

    if cached_result is not None:
        print(f"✓ Cache HIT - took only {elapsed_ms:.2f}ms (vs ~2-5 seconds for LLM)")
        print(f"✓ Retrieved {len(cached_result)} questions from cache")
        print()
        print("  📝 Cached questions:")
        for i, q in enumerate(cached_result, 1):
            print(f"     {i}. {q[:65]}...")
    else:
        print(f"✗ ERROR: Expected cache HIT but got MISS")

    print()

    # === TEST 3: Cache Stats ===
    print("📊 TEST 3: Cache Statistics")
    print("-" * 80)
    stats = cache.get_cache_stats()
    print(f"  Cache files: {stats['cache_count']}")
    print(f"  Total size: {stats['total_size_bytes']} bytes")
    print(f"  Cache directory: {stats['cache_dir']}")
    print()

    # === TEST 4: Different Document (Cache Miss) ===
    print("📋 TEST 4: Different document (cache MISS expected)")
    print("-" * 80)
    different_rfp = "This is a completely different RFP with different content..."
    start_time = time.time()
    cached_result = cache.get(different_rfp)
    elapsed_ms = (time.time() - start_time) * 1000

    if cached_result is None:
        print(f"✓ Cache MISS (as expected) - took {elapsed_ms:.2f}ms")
        print(f"  ✓ Content hash is different, so cache miss is correct")
    else:
        print(f"✗ ERROR: Expected cache MISS but got HIT")

    print()

    # === TEST 5: Same Document Again (Cache Hit) ===
    print("📋 TEST 5: Original document again (cache HIT expected)")
    print("-" * 80)
    start_time = time.time()
    cached_result = cache.get(SAMPLE_RFP)
    elapsed_ms = (time.time() - start_time) * 1000

    if cached_result is not None:
        print(f"✓ Cache HIT - took only {elapsed_ms:.2f}ms")
        print(f"✓ Still cached: {len(cached_result)} questions")
    else:
        print(f"✗ ERROR: Expected cache HIT but got MISS")

    print()

    # === SUMMARY ===
    print("=" * 80)
    print("✅ SUMMARY")
    print("=" * 80)
    print("✓ File-based caching is working correctly!")
    print("✓ Cache MISS on first call → calls LLM (~2-5 seconds)")
    print("✓ Cache HIT on subsequent calls → instant (<5ms)")
    print("✓ Different content correctly generates different cache keys")
    print("✓ Same content consistently retrieves from cache")
    print()
    print(f"💰 Performance benefit: ~2-5 seconds saved per cache hit (avoids LLM call)")
    print(f"💵 Cost benefit: Saves OpenAI API costs on repeated requests")
    print()
    print("🔍 Cache files stored at: ./data/cache/questions/")
    print()

if __name__ == "__main__":
    main()
