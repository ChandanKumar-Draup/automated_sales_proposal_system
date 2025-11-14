"""Validation script for embedding quality."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.vector_store import VectorStore
from services.llm_service import LLMService
from config import settings
import json


class EmbeddingValidator:
    """Validate embedding quality and retrieval accuracy."""

    def __init__(self):
        """Initialize validator."""
        self.vector_store = VectorStore()
        self.llm = LLMService()

        # Load metadata if available
        metadata_file = f"{settings.vector_store_path}/rfp_metadata.json"
        try:
            with open(metadata_file, "r") as f:
                self.metadata = json.load(f)
        except:
            self.metadata = []

    def test_semantic_coherence(self):
        """Test if semantically similar queries return relevant results."""
        print("\n" + "=" * 80)
        print("TEST 1: Semantic Coherence")
        print("=" * 80)

        test_queries = [
            ("semiconductor talent intelligence", ["ASM", "semiconductor"]),
            ("skills taxonomy implementation", ["TE", "skills", "taxonomy"]),
            ("labor market analysis", ["Liberty Mutual", "Tennessee", "labor"]),
            ("workforce analytics platform", ["workforce", "analytics"]),
            ("hiring analysis and compensation", ["hiring", "compensation"]),
        ]

        passed = 0
        for query, expected_keywords in test_queries:
            print(f"\nQuery: '{query}'")
            results = self.vector_store.search(query, top_k=3)

            if not results:
                print("  ❌ No results found")
                continue

            # Check if any expected keyword appears in top results
            found = False
            for doc, score, meta in results:
                for keyword in expected_keywords:
                    if keyword.lower() in doc.lower() or keyword.lower() in str(meta).lower():
                        found = True
                        break
                if found:
                    break

            if found:
                print(f"  ✅ PASS - Found relevant results")
                print(f"     Top result (score={score:.3f}): {doc[:100]}...")
                passed += 1
            else:
                print(f"  ❌ FAIL - No expected keywords found in top results")

        print(f"\nResult: {passed}/{len(test_queries)} tests passed")
        return passed == len(test_queries)

    def test_client_retrieval(self):
        """Test if we can retrieve documents by client name."""
        print("\n" + "=" * 80)
        print("TEST 2: Client-Specific Retrieval")
        print("=" * 80)

        clients = ["ASM", "Atlassian", "Denso", "GMR", "TE"]
        passed = 0

        for client in clients:
            query = f"{client} RFP requirements"
            results = self.vector_store.search(query, top_k=5)

            if not results:
                print(f"  ❌ {client}: No results")
                continue

            # Check if client appears in results
            found = False
            for doc, score, meta in results:
                if client.lower() in doc.lower() or (meta and client in str(meta.get("client_name", ""))):
                    found = True
                    break

            if found:
                print(f"  ✅ {client}: Found relevant documents")
                passed += 1
            else:
                print(f"  ❌ {client}: Client not found in results")

        print(f"\nResult: {passed}/{len(clients)} clients retrieved successfully")
        return passed >= len(clients) * 0.8  # 80% threshold

    def test_category_filtering(self):
        """Test retrieval for specific categories."""
        print("\n" + "=" * 80)
        print("TEST 3: Category Filtering")
        print("=" * 80)

        categories = {
            "talent intelligence": ["talent", "hiring", "recruitment"],
            "skills taxonomy": ["skills", "taxonomy", "competenc"],
            "pricing and cost": ["pric", "cost", "commercial"],
        }

        passed = 0
        for category, keywords in categories.items():
            query = f"RFP for {category}"
            results = self.vector_store.search(query, top_k=5)

            if not results:
                print(f"  ❌ {category}: No results")
                continue

            # Check if any keyword appears
            found = False
            for doc, score, meta in results:
                for keyword in keywords:
                    if keyword.lower() in doc.lower():
                        found = True
                        break
                if found:
                    break

            if found:
                print(f"  ✅ {category}: Relevant results found")
                passed += 1
            else:
                print(f"  ❌ {category}: No relevant results")

        print(f"\nResult: {passed}/{len(categories)} categories passed")
        return passed >= len(categories) * 0.66  # 66% threshold

    def test_knowledge_coverage(self):
        """Test overall knowledge base coverage."""
        print("\n" + "=" * 80)
        print("TEST 4: Knowledge Base Coverage")
        print("=" * 80)

        total_docs = len(self.vector_store.documents)
        print(f"Total documents in vector store: {total_docs}")

        if total_docs < 50:
            print(f"  ⚠️  WARNING: Only {total_docs} documents indexed (expected ~200-300 chunks from 91 docs)")
            passed = False
        elif total_docs < 150:
            print(f"  ⚠️  PARTIAL: {total_docs} documents indexed (moderate coverage)")
            passed = True
        else:
            print(f"  ✅ GOOD: {total_docs} documents indexed (good coverage)")
            passed = True

        # Check unique clients
        unique_clients = set()
        for meta in self.vector_store.metadata:
            if "client_name" in meta:
                unique_clients.add(meta["client_name"])

        print(f"Unique clients: {len(unique_clients)}")
        print(f"Clients: {', '.join(sorted(unique_clients))}")

        return passed

    def test_retrieval_speed(self):
        """Test search performance."""
        print("\n" + "=" * 80)
        print("TEST 5: Retrieval Speed")
        print("=" * 80)

        import time

        query = "talent intelligence platform for semiconductor industry"
        iterations = 10

        start = time.time()
        for _ in range(iterations):
            results = self.vector_store.search(query, top_k=5)
        end = time.time()

        avg_time = (end - start) / iterations * 1000  # ms

        print(f"Average search time: {avg_time:.1f}ms")

        if avg_time < 100:
            print(f"  ✅ EXCELLENT: Search is very fast")
            passed = True
        elif avg_time < 500:
            print(f"  ✅ GOOD: Search is acceptably fast")
            passed = True
        else:
            print(f"  ⚠️  SLOW: Search may need optimization")
            passed = False

        return passed

    def run_all_tests(self):
        """Run all validation tests."""
        print("\n" + "🧪" * 40)
        print("  EMBEDDING VALIDATION SUITE")
        print("🧪" * 40)

        results = {
            "Semantic Coherence": self.test_semantic_coherence(),
            "Client Retrieval": self.test_client_retrieval(),
            "Category Filtering": self.test_category_filtering(),
            "Knowledge Coverage": self.test_knowledge_coverage(),
            "Retrieval Speed": self.test_retrieval_speed(),
        }

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name:30s}: {status}")

        total_passed = sum(results.values())
        total_tests = len(results)
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")

        if total_passed == total_tests:
            print("\n🎉 All tests passed! Embedding quality is excellent.")
        elif total_passed >= total_tests * 0.8:
            print("\n✅ Most tests passed. Embedding quality is good.")
        else:
            print("\n⚠️  Some tests failed. Consider re-ingesting or tuning embeddings.")

        print("=" * 80)


def main():
    """Main entry point."""
    validator = EmbeddingValidator()
    validator.run_all_tests()


if __name__ == "__main__":
    main()
