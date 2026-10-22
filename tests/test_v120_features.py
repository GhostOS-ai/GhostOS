"""
Unit tests for GhostOS v1.2.0 features:
- Casper Feeder (Drag & Drop Base64 + Text file ingestion with XP)
- Menu Bar Tray Controller (GhostTrayController)
- Spotlight HUD & CLI routing
"""
import unittest
import base64
from unittest.mock import patch, MagicMock

from ghost.ui.api import GhostBridgeAPI
from ghost.ui.tray import GhostTrayController
from ghost.config import GHOST_CACHE_DIR

class TestV120Features(unittest.TestCase):

    def setUp(self):
        self.api = GhostBridgeAPI()

    def test_ingest_dropped_content_text(self):
        """Test text content drop ingestion."""
        res = self.api.ingest_dropped_content("test_feed.txt", "GhostOS is awesome and ultra-lightweight.")
        self.assertTrue(res.get("success"))
        self.assertGreaterEqual(res.get("chunks_count", 0), 1)

    def test_ingest_dropped_file_base64(self):
        """Test binary/Base64 content drop ingestion."""
        sample_text = "Binary simulated content for Casper Feeder"
        b64_str = "data:text/plain;base64," + base64.b64encode(sample_text.encode("utf-8")).decode("utf-8")
        res = self.api.ingest_dropped_file_base64("test_feed_b64.txt", b64_str)
        self.assertTrue(res.get("success"))
        self.assertGreaterEqual(res.get("chunks_count", 0), 1)

    def test_tray_controller_properties(self):
        """Test GhostTrayController initialization and platform detection."""
        tray = GhostTrayController()
        self.assertIsNotNone(tray.engine)
        self.assertIsNotNone(tray.juggler)
        # On Darwin it is supported, on other platforms it returns platform bool
        import sys
        if sys.platform == "darwin":
            self.assertTrue(tray.is_supported())
        else:
            self.assertFalse(tray.is_supported())

    @patch("ghost.ui.app.webview")
    def test_spotlight_hud_launcher_mock(self, mock_webview):
        """Test that launch_spotlight_hud configures HUD mode correctly."""
        from ghost.ui.app import launch_spotlight_hud
        mock_webview.screens = []
        mock_webview.create_window.return_value = MagicMock()
        
        launch_spotlight_hud(skin="cyberpunk")
        mock_webview.create_window.assert_called_once()
        call_kwargs = mock_webview.create_window.call_args[1]
        self.assertIn("mode=hud", call_kwargs["url"])
        self.assertIn("skin=cyberpunk", call_kwargs["url"])
        self.assertEqual(call_kwargs["width"], 740)
        self.assertEqual(call_kwargs["height"], 580)

if __name__ == "__main__":
    unittest.main()
