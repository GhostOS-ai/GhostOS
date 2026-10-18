import unittest
from ghost.core.ghostwriter import Ghostwriter

class TestGhostwriter(unittest.TestCase):
    def setUp(self):
        self.writer = Ghostwriter()

    def test_empty_text(self):
        res = self.writer.rewrite_text("")
        self.assertFalse(res["success"])
        self.assertIn("No text", res["error"])

    def test_rewrite_modes(self):
        modes = ["polish", "polite", "grammar", "summarize", "translate_en", "translate_ru"]
        for m in modes:
            res = self.writer.rewrite_text("Testing text rewrite.", mode=m)
            self.assertTrue(res["success"])
            self.assertIn("result", res)

if __name__ == "__main__":
    unittest.main()
