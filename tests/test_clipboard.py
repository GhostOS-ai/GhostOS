"""
Unit tests for Phantom Clipboard
"""
import unittest
from ghost.core.clipboard import PhantomClipboard

class TestPhantomClipboard(unittest.TestCase):

    def test_classify_error(self):
        err_text = "Traceback (most recent call last):\n  File 'app.py', line 10\nZeroDivisionError: division by zero"
        res = PhantomClipboard.inspect(err_text)
        self.assertTrue(res["detected"])
        self.assertEqual(res["category"], "error")
        self.assertEqual(res["suggested_action"], "diagnose_error")

    def test_classify_json(self):
        json_text = '{"name": "ghost", "vram_limit": 3584}'
        res = PhantomClipboard.inspect(json_text)
        self.assertTrue(res["detected"])
        self.assertEqual(res["category"], "json")
        self.assertEqual(res["suggested_action"], "format_json")

    def test_classify_sql(self):
        sql_text = "SELECT id, filename FROM documents WHERE size_bytes > 1000 ORDER BY id DESC"
        res = PhantomClipboard.inspect(sql_text)
        self.assertTrue(res["detected"])
        self.assertEqual(res["category"], "sql")

if __name__ == "__main__":
    unittest.main()
