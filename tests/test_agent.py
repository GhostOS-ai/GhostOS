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
        # Russian
        res_ru = GhostOSAgent.execute_intent("найди все pdf на рабочем столе")
        self.assertTrue(res_ru["handled"])
        self.assertEqual(res_ru["action"], "find_files")

        # English
        res_en = GhostOSAgent.execute_intent("find files report.docx on desktop")
        self.assertTrue(res_en["handled"])
        self.assertEqual(res_en["action"], "find_files")

        # Kazakh
        res_kk = GhostOSAgent.execute_intent("жұмыс үстелінен pdf тап")
        self.assertTrue(res_kk["handled"])
        self.assertEqual(res_kk["action"], "find_files")

        # Create folder in English & Russian
        res_mkdir = GhostOSAgent.execute_intent("create folder TestApp on desktop")
        self.assertTrue(res_mkdir["handled"])
        self.assertEqual(res_mkdir["action"], "create_folder")

if __name__ == "__main__":
    unittest.main()
