import unittest
from ghost.core.engine import GhostEngine

class TestModelCatalog(unittest.TestCase):
    def setUp(self):
        self.engine = GhostEngine()

    def test_get_model_catalog_structure(self):
        catalog = self.engine.get_model_catalog()
        self.assertIn("active_backend", catalog)
        self.assertIn("hardware_acceleration", catalog)
        self.assertIn("ollama_active", catalog)
        self.assertIn("ollama_models", catalog)
        self.assertIn("recommended_models", catalog)
        self.assertIsInstance(catalog["recommended_models"], list)
        self.assertTrue(len(catalog["recommended_models"]) > 0)

if __name__ == "__main__":
    unittest.main()
