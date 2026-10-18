"""
Unit tests for GhostOS i18n & Locale Detection
"""
import unittest
from ghost.ui.api import GhostBridgeAPI
from ghost.core.agent import GhostOSAgent

class TestGhostI18n(unittest.TestCase):

    def setUp(self):
        self.api = GhostBridgeAPI()

    def test_system_locale_detection(self):
        res = self.api.get_system_locale()
        self.assertIn("locale", res)
        self.assertIsInstance(res["locale"], str)
        self.assertGreaterEqual(len(res["locale"]), 2)

    def test_set_locale(self):
        res = self.api.set_locale("ru")
        self.assertEqual(res["locale"], "ru")
        res_kk = self.api.set_locale("kk")
        self.assertEqual(res_kk["locale"], "kk")

    def test_multilingual_agent(self):
        # Kazakh search intent
        res_kk = GhostOSAgent.execute_intent("файлдарды тап")
        self.assertTrue(res_kk["handled"])
        self.assertEqual(res_kk["action"], "find_files")

        # English search intent
        res_en = GhostOSAgent.execute_intent("find file notes.txt")
        self.assertTrue(res_en["handled"])
        self.assertEqual(res_en["action"], "find_files")

if __name__ == "__main__":
    unittest.main()
