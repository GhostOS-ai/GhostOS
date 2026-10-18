import unittest
import tempfile
from pathlib import Path
from ghost.core.memory_vault import MemoryVault

class TestMemoryVault(unittest.TestCase):
    def setUp(self):
        MemoryVault._instance = None
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_ghost.db"
        self.vault = MemoryVault(self.db_path)

    def tearDown(self):
        MemoryVault._instance = None
        self.temp_dir.cleanup()

    def test_remember_and_recall(self):
        self.vault.remember("favorite_language", "Python", category="preferences")
        val = self.vault.recall("favorite_language")
        self.assertEqual(val, "Python")

    def test_forget(self):
        self.vault.remember("temp_fact", "123")
        self.assertEqual(self.vault.recall("temp_fact"), "123")
        forgotten = self.vault.forget("temp_fact")
        self.assertTrue(forgotten)
        self.assertIsNone(self.vault.recall("temp_fact"))

    def test_auto_extract_facts(self):
        extracted = self.vault.auto_extract_facts("Привет, меня зовут Alex, я пишу на Flutter и Python")
        self.assertTrue(len(extracted) >= 1)
        self.assertEqual(self.vault.recall("user_name"), "Alex")

    def test_context_block(self):
        self.vault.remember("project_name", "GhostOS")
        block = self.vault.get_context_block()
        self.assertIn("project_name: GhostOS", block)

if __name__ == "__main__":
    unittest.main()
