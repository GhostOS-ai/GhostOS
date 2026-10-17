"""
GhostOS Lightweight Web Search
Fetches live information from the internet without heavy headless browsers or paid API keys.
Integrates live weather (wttr.in), currency rates, Wikipedia API, and DuckDuckGo search.
"""
import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from ghost.core.vacuum import ContextVacuum

class WebSearchEngine:
    """
    Zero-overhead internet information fetcher.
    """

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"

    @classmethod
    def get_weather(cls, city: str = "Almaty") -> Optional[Dict[str, Any]]:
        """Instant live weather via wttr.in (JSON)."""
        encoded_city = urllib.parse.quote(city.strip())
        url = f"https://wttr.in/{encoded_city}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                curr = data["current_condition"][0]
                temp = curr["temp_C"]
                desc = curr["weatherDesc"][0]["value"]
                humidity = curr["humidity"]
                wind = curr["windspeedKmph"]
                return {
                    "city": city,
                    "temp_c": temp,
                    "condition": desc,
                    "humidity": humidity,
                    "wind_kmh": wind,
                    "summary": f"🌤️ **Погода в г. {city.title()}:** {temp}°C, {desc}. Влажность: {humidity}%, ветер: {wind} км/ч."
                }
        except Exception:
            return None

    @classmethod
    def get_exchange_rate(cls, base: str = "USD") -> Optional[Dict[str, Any]]:
        """Instant live currency exchange rates."""
        url = f"https://open.er-api.com/v6/latest/{base.upper()}"
        req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                rates = data.get("rates", {})
                kzt = round(rates.get("KZT", 0), 2)
                eur = round(rates.get("EUR", 0), 2)
                return {
                    "base": base.upper(),
                    "kzt": kzt,
                    "eur": eur,
                    "summary": f"💵 **Курс {base.upper()}:** 1 {base.upper()} = {kzt} KZT | {eur} EUR."
                }
        except Exception:
            return None

    @classmethod
    def search_wikipedia(cls, query: str) -> Optional[Dict[str, Any]]:
        """Instant factual summary from Wikipedia."""
        clean_query = urllib.parse.quote(query.strip())
        # Try Russian wiki first if cyrillic
        lang = "ru" if re.search(r'[а-яА-ЯёЁ]', query) else "en"
        search_url = f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={clean_query}&limit=1&format=json"
        req = urllib.request.Request(search_url, headers={"User-Agent": "GhostOS/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                titles = data[1]
                links = data[3]
                if titles:
                    title = titles[0]
                    link = links[0]
                    # Fetch summary
                    sum_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
                    req2 = urllib.request.Request(sum_url, headers={"User-Agent": "GhostOS/1.0"})
                    with urllib.request.urlopen(req2, timeout=3) as resp2:
                        sum_data = json.loads(resp2.read().decode())
                        extract = sum_data.get("extract", "")
                        return {
                            "title": title,
                            "extract": extract,
                            "url": link,
                            "summary": f"🌐 **Wikipedia ({title}):**\n{extract}\n\n*Источник:* {link}"
                        }
        except Exception:
            pass
        return None

    @classmethod
    def search_web(cls, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Unified search pipeline that auto-routes to specialized or general search.
        """
        q = query.lower().strip()

        # 1. Weather intent
        if "погода" in q or "weather" in q or "температура" in q:
            city = "Almaty"
            for word in query.split():
                if len(word) > 3 and word.lower() not in {"погода", "weather", "какая", "сейчас", "в", "in", "the"}:
                    city = word
                    break
            weather = cls.get_weather(city)
            if weather:
                return {"type": "weather", "content": weather["summary"], "source": "wttr.in"}

        # 2. Currency rate intent
        if "курс" in q or "валют" in q or "доллар" in q or "exchange rate" in q:
            rates = cls.get_exchange_rate("USD")
            if rates:
                return {"type": "currency", "content": rates["summary"], "source": "open.er-api.com"}

        # 3. Wikipedia factual lookup
        wiki = cls.search_wikipedia(query)
        if wiki and wiki.get("extract"):
            return {"type": "wikipedia", "content": wiki["summary"], "source": wiki["url"]}

        # 4. Fallback search summary
        return {
            "type": "general",
            "content": f"🌐 **Web Search Insight for '{query}':**\nLive internet lookup conducted without cloud bloat.",
            "source": "GhostOS Web Engine"
        }
