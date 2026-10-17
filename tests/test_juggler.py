"""
Unit tests for VRAM Juggler memory swapping
"""
import unittest
from ghost.core.memory_juggler import MemoryJuggler

class TestMemoryJuggler(unittest.TestCase):

    def setUp(self):
        self.juggler = MemoryJuggler(auto_sleep_seconds=300)

    def test_memory_status(self):
        status = self.juggler.get_memory_status()
        self.assertIn("active_model", status)
        self.assertIn("vram_saved_mb", status)
        self.assertGreater(status["vram_saved_mb"], 0)

    def test_model_lifecycle(self):
        loaded = []
        unloaded = []

        self.juggler.register_handler(
            "test_model_a",
            load_cb=lambda: loaded.append("a"),
            unload_cb=lambda: unloaded.append("a")
        )
        self.juggler.register_handler(
            "test_model_b",
            load_cb=lambda: loaded.append("b"),
            unload_cb=lambda: unloaded.append("b")
        )

        # Request A
        self.juggler.request_model("test_model_a")
        self.assertEqual(self.juggler.active_model, "test_model_a")
        self.assertIn("a", loaded)

        # Request B -> should unload A and load B
        self.juggler.request_model("test_model_b")
        self.assertEqual(self.juggler.active_model, "test_model_b")
        self.assertIn("a", unloaded)
        self.assertIn("b", loaded)

if __name__ == "__main__":
    unittest.main()
