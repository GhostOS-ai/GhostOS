"""
Unit tests for Memory Chameleon
"""
import unittest
from ghost.core.chameleon import MemoryChameleon

class TestMemoryChameleon(unittest.TestCase):

    def setUp(self):
        MemoryChameleon.set_override(None)

    def test_default_profile(self):
        prof = MemoryChameleon.get_profile()
        self.assertIn("active_mode", prof)
        self.assertIn("context_window", prof)
        self.assertIn("auto_sleep_seconds", prof)

    def test_override_profile(self):
        MemoryChameleon.set_override(MemoryChameleon.MODE_ECO)
        prof = MemoryChameleon.get_profile()
        self.assertEqual(prof["active_mode"], MemoryChameleon.MODE_ECO)
        self.assertEqual(prof["context_window"], 1024)
        self.assertEqual(prof["auto_sleep_seconds"], 60)

        MemoryChameleon.set_override(None)

if __name__ == "__main__":
    unittest.main()
