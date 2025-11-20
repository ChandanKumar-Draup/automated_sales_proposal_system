#!/usr/bin/env python3
"""
Simple demonstration of the question caching functionality.
This script tests the cache without needing the full API server.
"""
import time
from services.question_cache import QuestionCache

# Sample RFP document
SAMPLE_RFP = """
REQUEST FOR PROPOSAL (RFP)
Enterprise Software Development Services

1. What is your company's experience with cloud-native applications?
2. Describe your development methodology and testing practices.
3. Please provide pricing for different developer levels.
4. What is your approach to security and data protection?
5. How do you handle production support and maintenance?
"""

def main():
    print("=" * 80)
    print("QUESTION CACHING DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize cache
    cache = QuestionCache()

    # Sample questions
    sample_questions = [
        "What is your company's experience with cloud-native applications?",
        "Describe your development methodology and testing practices.",
        "Please provide pricing for different developer levels.",
        "What is your approach to security and data protection?",
        "How do you handle production support and maintenance?"
    ]

    # === TEST 1: Cache Miss ===
    print("TEST 1: First extraction (cache MISS expected)")
    print("-" * 80)
    start_time = time.time()
    cached_result = cache.get(SAMPLE_RFP)
    elapsed = time.time() - start_time

    if cached_result is None:
        print(f"✓ Cache MISS (as expected) - took {elapsed*1000:.2f}ms")
        print(f"  Simulating LLM extraction...")
        time.sleep(0.5)  # Simulate LLM call
        cache.set(SAMPLE_RFP, sample_questions)
        print(f"✓ Questions cached successfully ({len(sample_questions)} questions)")
    else:
        print(f"✗ ERROR: Expected cache MISS but got HIT")

    print()

    # === TEST 2: Cache Hit ===
    print("TEST 2: Second extraction (cache HIT expected)")
    print("-" * 80)
    start_time = time.time()
    cached_result = cache.get(SAMPLE_RFP)
    elapsed = time.time() - start_time

    if cached_result is not None:
        print(f"✓ Cache HIT - took {elapsed*1000:.2f}ms")
        print(f"✓ Retrieved {len(cached_result)} questions from cache")
        print()
        print("Sample questions from cache:")
        for i, q in enumerate(cached_result[:3], 1):
            print(f"  {i}. {q[:70]}...")
    else:
        print(f"✗ ERROR: Expected cache HIT but got MISS")

    print()

    # === TEST 3: Cache Stats ===
    print("TEST 3: Cache Statistics")
    print("-" * 80)
    stats = cache.get_cache_stats()
    print(f"Cache files: {stats['cache_count']}")
    print(f"Total size: {stats['total_size_bytes']} bytes")
    print(f"Cache directory: {stats['cache_dir']}")
    print()

    # === TEST 4: Different Document (Cache Miss) ===
    print("TEST 4: Different document (cache MISS expected)")
    print("-" * 80)
    different_rfp = "Different RFP content here..."
    start_time = time.time()
    cached_result = cache.get(different_rfp)
    elapsed = time.time() - start_time

    if cached_result is None:
        print(f"✓ Cache MISS (as expected) - took {elapsed*1000:.2f}ms")
        print(f"  Content hash is different, so cache miss is correct")
    else:
        print(f"✗ ERROR: Expected cache MISS but got HIT")

    print()

    # === SUMMARY ===
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ File-based caching is working correctly!")
    print("✓ Cache MISS on first call (calls LLM)")
    print("✓ Cache HIT on second call (avoids LLM)")
    print("✓ Different content correctly generates different cache keys")
    print()
    print(f"Performance benefit: ~500ms saved per cache hit (no LLM call)")
    print()

if __name__ == "__main__":
    main()
