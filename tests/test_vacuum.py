"""
Unit tests for Context Vacuum
"""
import unittest
from ghost.core.vacuum import ContextVacuum

class TestContextVacuum(unittest.TestCase):

    def test_clean_code_comments(self):
        sample_code = """# This is a comment\ndef add(a, b):\n    # add numbers\n    return a + b\n"""
        cleaned = ContextVacuum.clean_code(sample_code)
        self.assertNotIn("# This is a comment", cleaned)
        self.assertNotIn("# add numbers", cleaned)
        self.assertIn("return a + b", cleaned)

    def test_compress_traceback(self):
        huge_traceback = "Traceback (most recent call last):\n" + "\n".join([f'  File "lib_{i}.py", line {i}, in func' for i in range(30)]) + "\nValueError: Invalid operand"
        compressed = ContextVacuum.compress_traceback(huge_traceback)
        self.assertIn("compressed by Context Vacuum", compressed)
        self.assertIn("ValueError: Invalid operand", compressed)

    def test_squeeze_savings(self):
        big_prompt = "Hello world! " * 200
        compacted, stats = ContextVacuum.squeeze(big_prompt, max_chars=100)
        self.assertLessEqual(len(compacted), 200)
        self.assertGreater(stats["savings_percent"], 0)

if __name__ == "__main__":
    unittest.main()
