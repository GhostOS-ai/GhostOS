"""
Unit tests for Casper RPG
"""
import unittest
import tempfile
from pathlib import Path
from ghost.core.rpg import CasperRPG

class TestCasperRPG(unittest.TestCase):

    def test_rank_progression(self):
        rank_1 = CasperRPG.get_rank(0)
        self.assertEqual(rank_1["level"], 1)

        rank_3 = CasperRPG.get_rank(300)
        self.assertEqual(rank_3["level"], 3)
        self.assertEqual(rank_3["accessory"], "visor")

        rank_6 = CasperRPG.get_rank(2000)
        self.assertEqual(rank_6["level"], 6)
        self.assertEqual(rank_6["accessory"], "crown")

    def test_add_xp(self):
        res = CasperRPG.add_xp(15, "eat")
        self.assertGreater(res["total_xp"], 0)
        self.assertIn("title", res)

if __name__ == "__main__":
    unittest.main()
