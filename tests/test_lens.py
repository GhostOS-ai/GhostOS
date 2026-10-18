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

    def test_sandbox_destructive_blocked(self):
        cmd = "rm -rf /"
        res = GhostLens.verify_and_patch(cmd)
        sandbox = res.get("sandbox", {})
        self.assertEqual(sandbox.get("safety_level"), "CRITICAL")
        self.assertTrue(sandbox.get("is_blocked"))

    def test_sandbox_safe_command(self):
        cmd = "ls -la"
        res = GhostLens.verify_and_patch(cmd)
        sandbox = res.get("sandbox", {})
        self.assertEqual(sandbox.get("safety_level"), "SAFE")
        self.assertFalse(sandbox.get("is_blocked"))

if __name__ == "__main__":
    unittest.main()
