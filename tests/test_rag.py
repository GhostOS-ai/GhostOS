"""
Unit tests for GhostOS Zero-DB RAG
"""
import unittest
import tempfile
from pathlib import Path
from ghost.core.rag import ZeroDbRAG

class TestZeroDbRAG(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_knowledge.db"
        self.rag = ZeroDbRAG(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ingest_and_search_text_file(self):
        sample_file = Path(self.temp_dir.name) / "notes.txt"
        sample_file.write_text(
            "GhostOS uses SQLite FTS5 for zero-overhead local full text search. "
            "It runs on CPU or Metal without needing any vector databases.",
            encoding="utf-8"
        )

        res = self.rag.ingest_file(str(sample_file))
        self.assertTrue(res["success"])
        self.assertEqual(res["filename"], "notes.txt")
        self.assertGreaterEqual(res["chunks_count"], 1)

        # Search for keyword
        results = self.rag.search("SQLite FTS5")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["filename"], "notes.txt")
        self.assertIn("SQLite FTS5", results[0]["content"])

    def test_list_and_clear_documents(self):
        sample_file = Path(self.temp_dir.name) / "code.py"
        sample_file.write_text("def hello_ghost(): return 'boo!'", encoding="utf-8")
        self.rag.ingest_file(str(sample_file))

        docs = self.rag.list_documents()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["filename"], "code.py")

        self.rag.clear()
        docs_after = self.rag.list_documents()
        self.assertEqual(len(docs_after), 0)

if __name__ == "__main__":
    unittest.main()
