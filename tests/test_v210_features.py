"""
Unit tests for GhostOS v2.1.0 Features:
- Hybrid Brain & Multi-Provider Architecture (OpenAI, Anthropic, DeepSeek, Custom, Ollama, Mock)
- AI Personas (Casper, GhostCode, Ghostwriter, Deep Think, Web Live)
- Deep Reasoning (<think> CoT tags)
- Multi-Session Chat Management & Persistence
"""
import os
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from ghost.config import load_config, save_config, DEFAULT_CONFIG
from ghost.core.engine import GhostEngine, PERSONA_PROMPTS
from ghost.ui.api import GhostBridgeAPI


class TestGhostOSv210Features(unittest.TestCase):

    def setUp(self):
        self.orig_config = load_config()
        self.test_dir = tempfile.mkdtemp(prefix="ghost_v210_test_")
        self.api = GhostBridgeAPI()

    def tearDown(self):
        save_config(self.orig_config)
        self.api.engine.reload_config()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_config_deep_merge_and_providers(self):
        cfg = load_config()
        self.assertIn("provider", cfg)
        self.assertIn("api_keys", cfg)
        self.assertIn("custom_endpoint", cfg)
        self.assertIn("openai", cfg["api_keys"])
        self.assertIn("deepseek", cfg["api_keys"])
        self.assertIn("anthropic", cfg["api_keys"])

    def test_persona_prompts_exist(self):
        self.assertIn("default", PERSONA_PROMPTS)
        self.assertIn("ghostcode", PERSONA_PROMPTS)
        self.assertIn("ghostwriter", PERSONA_PROMPTS)
        self.assertIn("reasoner", PERSONA_PROMPTS)
        self.assertIn("web", PERSONA_PROMPTS)

    def test_engine_reasoner_persona_generates_think_tags(self):
        engine = GhostEngine()
        reply = engine.ask("Реши уравнение x^2 - 4 = 0", persona="reasoner", provider="mock")
        self.assertIn("<think>", reply)
        self.assertIn("</think>", reply)
        self.assertIn("Анализ", reply)

    def test_engine_ghostcode_persona(self):
        engine = GhostEngine()
        reply = engine.ask("Создай кэширующий декоратор", persona="ghostcode", provider="mock")
        self.assertIn("GhostCode", reply)
        self.assertIn("```python", reply)

    def test_engine_ghostwriter_persona(self):
        engine = GhostEngine()
        reply = engine.ask("Пресс-релиз для GhostOS", persona="ghostwriter", provider="mock")
        self.assertIn("Ghostwriter", reply)

    def test_ai_config_bridge_api(self):
        cfg_res = self.api.get_ai_config()
        self.assertIn("provider", cfg_res)
        self.assertIn("providers_list", cfg_res)
        self.assertIn("masked_keys", cfg_res)
        self.assertIn("custom_endpoint", cfg_res)
        self.assertTrue(len(cfg_res["providers_list"]) >= 6)

    def test_save_ai_config_and_reload(self):
        save_res = self.api.save_ai_config(
            provider="openai",
            model="gpt-4o",
            api_keys={"openai": "sk-test1234567890"},
            custom_endpoint="https://api.openai.com/v1"
        )
        self.assertTrue(save_res["success"])
        self.assertEqual(save_res["provider"], "openai")
        self.assertEqual(save_res["model"], "gpt-4o")

        # Verify through get_ai_config
        new_cfg = self.api.get_ai_config()
        self.assertEqual(new_cfg["provider"], "openai")
        self.assertEqual(new_cfg["model_name"], "gpt-4o")
        self.assertTrue(new_cfg["has_keys"]["openai"])

    def test_test_ai_connection_built_in(self):
        res = self.api.test_ai_connection("mock")
        self.assertTrue(res["success"])
        self.assertIn("100% офлайн", res["message"])

    def test_studio_session_management_flow(self):
        # 1. Clear any prior test sessions
        self.api.clear_all_studio_sessions()

        # 2. Verify empty list
        res_empty = self.api.get_saved_sessions()
        self.assertEqual(res_empty["sessions"], [])

        # 3. Save a new session
        test_session_id = "test_sess_001"
        test_messages = [
            {"sender": "user", "text": "Как сделать FastAPI микросервис?", "timestamp": 12345678},
            {"sender": "ghost", "text": "Вот пример кода...", "citations": []}
        ]
        save_res = self.api.save_studio_session(
            session_id=test_session_id,
            title="FastAPI Микросервис",
            mode="chat",
            messages=test_messages
        )
        self.assertTrue(save_res["success"])

        # 4. Fetch and verify saved session
        res_list = self.api.get_saved_sessions()
        self.assertEqual(len(res_list["sessions"]), 1)
        sess = res_list["sessions"][0]
        self.assertEqual(sess["id"], test_session_id)
        self.assertEqual(sess["title"], "FastAPI Микросервис")
        self.assertEqual(len(sess["messages"]), 2)

        # 5. Delete session
        del_res = self.api.delete_studio_session(test_session_id)
        self.assertTrue(del_res["success"])

        res_after = self.api.get_saved_sessions()
        self.assertEqual(len(res_after["sessions"]), 0)

    def test_bridge_ask_with_persona_and_provider(self):
        res = self.api.ask("Привет!", persona="ghostcode", provider="mock")
        self.assertTrue(res["success"])
        self.assertIsInstance(res["response"], str)
        self.assertTrue(len(res["response"]) > 0)


if __name__ == "__main__":
    unittest.main()
