"""
Unit tests for Native Voice Engine
"""
import unittest
from ghost.core.voice import VoiceEngine

class TestVoiceEngine(unittest.TestCase):

    def setUp(self):
        self.voice = VoiceEngine()

    def test_clean_text_for_speech(self):
        text = "Check this code:\n```python\nprint('hello')\n```\nAnd read `item` with **bold** text and https://google.com link."
        cleaned = self.voice.clean_text_for_speech(text)
        self.assertNotIn("```", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertIn("item", cleaned)
        self.assertIn("bold", cleaned)

    def test_voice_toggle(self):
        initial = self.voice.is_enabled
        toggled = self.voice.toggle()
        self.assertEqual(toggled, not initial)
        # Reset
        self.voice.toggle(initial)

if __name__ == "__main__":
    unittest.main()
