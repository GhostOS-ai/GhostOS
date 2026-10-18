import unittest
from ghost.core.time_machine import GhostTimeMachine

class TestTimeMachine(unittest.TestCase):
    def test_session_summary(self):
        res = GhostTimeMachine.generate_session_summary()
        self.assertIn("summary", res)
        self.assertIn("commit_suggestion", res)
        self.assertIn("standup", res)

    def test_daily_standup_generation(self):
        standup = GhostTimeMachine.generate_daily_standup()
        self.assertIn("Daily Standup Report", standup)
        self.assertIn("accomplished today", standup)

    def test_conventional_commit_format(self):
        commit = GhostTimeMachine.generate_conventional_commit()
        self.assertTrue(any(commit.startswith(prefix) for prefix in ["feat", "fix", "refactor", "chore", "style", "test", "docs", "perf"]))

if __name__ == "__main__":
    unittest.main()
