"""
Unit tests for GhostOS Safe Terminal Autopilot
"""
import unittest
from ghost.core.autopilot import TerminalAutopilot

class TestTerminalAutopilot(unittest.TestCase):

    def setUp(self):
        self.pilot = TerminalAutopilot()

    def test_safe_command_evaluation(self):
        res = self.pilot.evaluate_risk("ls -la")
        self.assertEqual(res["level"], "safe")
        self.assertFalse(res["requires_confirm"])

    def test_dangerous_command_evaluation(self):
        res = self.pilot.evaluate_risk("rm -rf /tmp/test")
        self.assertEqual(res["level"], "dangerous")
        self.assertTrue(res["requires_confirm"])

        res_sudo = self.pilot.evaluate_risk("sudo apt update")
        self.assertEqual(res_sudo["level"], "dangerous")

    def test_caution_command_evaluation(self):
        res = self.pilot.evaluate_risk("kill -9 1234")
        self.assertEqual(res["level"], "caution")
        self.assertTrue(res["requires_confirm"])

    def test_command_generation_recipes(self):
        res = self.pilot.generate_command("kill port 8080")
        self.assertIn("8080", res["command"])
        self.assertIn("kill", res["command"])

    def test_safe_execution(self):
        res = self.pilot.execute_command("echo 'GhostOS Online'")
        self.assertTrue(res["success"])
        self.assertEqual(res["stdout"], "GhostOS Online")

if __name__ == "__main__":
    unittest.main()
