"""
Unit tests for Web Search Engine
"""
import unittest
from ghost.core.web_search import WebSearchEngine

class TestWebSearchEngine(unittest.TestCase):

    def test_routing_weather(self):
        res = WebSearchEngine.search_web("погода в Париже")
        self.assertEqual(res["type"], "weather")
        self.assertIn("Погода", res["content"])

    def test_routing_currency(self):
        res = WebSearchEngine.search_web("курс доллара")
        self.assertEqual(res["type"], "currency")
        self.assertIn("Курс USD", res["content"])

    def test_routing_wikipedia(self):
        res = WebSearchEngine.search_web("Python programming language")
        self.assertEqual(res["type"], "wikipedia")
        self.assertIn("Python", res["content"])

if __name__ == "__main__":
    unittest.main()
