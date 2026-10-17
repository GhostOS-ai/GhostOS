"""
Unit tests for Ghost OS Agent
"""
import unittest
import tempfile
from pathlib import Path
from ghost.core.agent import GhostOSAgent

class TestGhostOSAgent(unittest.TestCase):

    def test_create_and_find_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_report_casper.txt"
            test_file.write_text("Hello Casper agent!")

            results = GhostOSAgent.find_files("test_report_casper", search_dir=tmpdir)
            self.assertGreaterEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "test_report_casper.txt")

    def test_create_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "subfolder" / "project"
            res = GhostOSAgent.create_folder(str(target))
            self.assertTrue(res["success"])
            self.assertTrue(target.exists())

    def test_intent_parsing(self):
        res = GhostOSAgent.execute_intent("найди все pdf на рабочем столе")
        self.assertTrue(res["handled"])
        self.assertEqual(res["action"], "find_files")

if __name__ == "__main__":
    unittest.main()
