"""
Unit tests for Ghost Lens
"""
import unittest
from ghost.core.lens import GhostLens

class TestGhostLens(unittest.TestCase):

    def test_patch_sed_bsd(self):
        cmd = "sed -i 's/foo/bar/g' test.txt"
        res = GhostLens.verify_and_patch(cmd)
        self.assertIn("sed -i '' 's/foo/bar/g' test.txt", res["patched_command"])
        self.assertGreater(len(res["modifications"]), 0)

    def test_patch_grep_posix(self):
        cmd = "grep -P '^[0-9]+' data.log"
        res = GhostLens.verify_and_patch(cmd)
        self.assertIn("grep -E", res["patched_command"])

    def test_builtin_validation(self):
        cmd = "echo 'testing'"
        res = GhostLens.verify_and_patch(cmd)
        self.assertTrue(res["is_valid"])

if __name__ == "__main__":
    unittest.main()
