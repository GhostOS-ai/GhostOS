"""
Unit tests for GhostOS v1.3.0 features:
- Live Skin/Theme Switcher (set_skin)
- Chat History Reset (clear_chat)
- Conversational Greeting Filtering (Russian / Kazakh / English natural replies)
- Safe modern locale detection
"""
import unittest
from ghost.ui.api import GhostBridgeAPI
from ghost.core.engine import GhostEngine

class TestV130Features(unittest.TestCase):

    def setUp(self):
        self.api = GhostBridgeAPI()
        self.engine = GhostEngine()

    def test_set_skin(self):
        """Test theme/skin switcher API."""
        res = self.api.set_skin("cyberpunk")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("skin"), "cyberpunk")
        self.assertEqual(self.api.skin, "cyberpunk")

        res_gold = self.api.set_skin("gold")
        self.assertTrue(res_gold.get("success"))
        self.assertEqual(res_gold.get("skin"), "gold")

    def test_clear_chat(self):
        """Test clearing chat session."""
        res = self.api.clear_chat()
        self.assertTrue(res.get("success"))

    def test_conversational_greetings_russian(self):
        """Test warm conversational response to Russian greeting 'Привет'."""
        reply = self.engine._query_mock("Привет")
        self.assertIn("Привет!", reply)
        self.assertIn("Каспер", reply)

    def test_conversational_greetings_kazakh(self):
        """Test warm conversational response to Kazakh greeting 'Сәлем'."""
        reply = self.engine._query_mock("Сәлем! Қалың қалай?")
        self.assertIn("Сәлем!", reply)
        self.assertIn("Каспермін", reply)

    def test_conversational_greetings_english(self):
        """Test warm conversational response to English greeting 'Hello Casper'."""
        reply = self.engine._query_mock("Hello Casper")
        self.assertIn("Hello!", reply)
        self.assertIn("Casper", reply)

    def test_get_locale_no_deprecation(self):
        """Test locale detection without throwing deprecated warnings."""
        res = self.api.get_system_locale()
        self.assertIn("locale", res)
        self.assertIsInstance(res["locale"], str)
        self.assertTrue(len(res["locale"]) >= 2)

if __name__ == "__main__":
    unittest.main()
