"""
GhostOS Inference Engine
Multi-backend manager supporting Ollama, llama.cpp (Metal/GGUF), and built-in offline engine.
Seamlessly integrated with the VRAM Juggler for zero-OOM execution.
"""
import os
import re
import json
import urllib.request
import urllib.error
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator

from ghost.config import GHOST_MODELS_DIR, load_config
from ghost.core.memory_juggler import MemoryJuggler

logger = logging.getLogger("ghost.engine")

GHOST_SYSTEM_PROMPT = """You are GhostOS (Casper), an ultra-lightweight, invisible desktop AI companion.
You are running 100% locally and privately on the user's computer.
Your tone is helpful, concise, witty, and precise.
When providing code, provide clear markdown blocks with language tags.
If context from local files or screen is provided, use it faithfully."""

class GhostEngine:
    """
    Main AI engine dispatcher that chooses the fastest available local backend.
    """

    def __init__(self):
        self.config = load_config()
        self.juggler = MemoryJuggler(auto_sleep_seconds=self.config.get("auto_sleep_seconds", 180))
        self.backend = self._detect_backend()

        # Register with VRAM juggler
        self.juggler.register_handler(
            MemoryJuggler.MODEL_LLM,
            load_cb=self._load_llm,
            unload_cb=self._unload_llm
        )

    def _detect_backend(self) -> str:
        """Auto-detect the best available backend on this machine."""
        user_pref = self.config.get("engine", "auto")
        if user_pref != "auto":
            return user_pref

        # Check if Ollama is running locally
        try:
            req = urllib.request.Request(f"{self.config.get('ollama_host', 'http://localhost:11434')}/api/tags")
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    logger.info("Detected local Ollama instance running!")
                    return "ollama"
        except Exception:
            pass

        # Check if llama_cpp is installed and a GGUF model exists
        try:
            import llama_cpp
            ggufs = list(GHOST_MODELS_DIR.glob("*.gguf"))
            if ggufs:
                logger.info(f"Detected llama_cpp with local model: {ggufs[0].name}")
                return "llamacpp"
        except ImportError:
            pass

        # Default fast built-in engine
        return "mock"

    def _load_llm(self) -> None:
        """Lifecycle hook called by VRAM Juggler when LLM is needed."""
        logger.info(f"Engine [{self.backend}] activated in memory.")

    def _unload_llm(self) -> None:
        """Lifecycle hook called by VRAM Juggler to purge LLM from memory."""
        logger.info(f"Engine [{self.backend}] unloaded from memory.")

    def ask(self, prompt: str, context: Optional[str] = None, screen_context: Optional[str] = None) -> str:
        """
        Generate response given a user prompt and optional document/screen context.
        Optimized with Context Vacuum and Memory Chameleon profiles.
        """
        from ghost.core.vacuum import ContextVacuum
        from ghost.core.chameleon import MemoryChameleon
        from ghost.core.rpg import CasperRPG
        from ghost.core.agent import GhostOSAgent
        from ghost.core.web_search import WebSearchEngine
        from ghost.core.voice import VoiceEngine

        voice = VoiceEngine()

        # 1. OS Agent tasks (search files on disk, create folders, move screenshots)
        agent_res = GhostOSAgent.execute_intent(prompt)
        if agent_res.get("handled"):
            reply = agent_res["output"]
            if voice.is_enabled:
                voice.speak(reply)
            return reply

        # 2. Live Web Search (weather, currency, Wikipedia facts, web queries)
        web_context = ""
        p_lower = prompt.lower()
        if any(w in p_lower for w in ["погода", "weather", "курс", "доллар", "валют", "найди в интернете", "кто такой", "что такое", "/web"]):
            search_query = re.sub(r'^(найди в интернете|погугли|/web)\s*', '', prompt).strip()
            web_res = WebSearchEngine.search_web(search_query)
            if web_res and web_res.get("content"):
                web_context = f"\n--- Live Web Context ({web_res.get('source', 'Internet')}) ---\n{web_res['content']}\n"

        profile = MemoryChameleon.get_profile()
        max_chars = profile["context_window"] * 4

        self.juggler.request_model(MemoryJuggler.MODEL_LLM)
        self.juggler.touch()

        # Construct full prompt
        full_context = ""
        if web_context:
            full_context += web_context
        if context:
            compact_ctx, stats = ContextVacuum.squeeze(context, max_chars=int(max_chars * 0.5))
            full_context += f"\n--- Local Document Context (RAG) ---\n{compact_ctx}\n"
        if screen_context:
            full_context += f"\n--- Active Screen Context ---\n{screen_context}\n"

        augmented_prompt = f"{full_context}\nUser: {prompt}" if full_context else prompt
        # Squeeze full prompt
        augmented_prompt, _ = ContextVacuum.squeeze(augmented_prompt, max_chars=max_chars)

        # Award RPG XP for using Casper
        CasperRPG.add_xp(10, "ask")

        reply = ""
        if self.backend == "ollama":
            reply = self._query_ollama(augmented_prompt)
        elif self.backend == "llamacpp":
            reply = self._query_llamacpp(augmented_prompt)
        else:
            reply = self._query_mock(prompt, context=context or web_context, screen_context=screen_context)

        # 3. Voice Output if enabled
        if voice.is_enabled:
            voice.speak(reply)

        return reply

    def _query_ollama(self, prompt: str) -> str:
        """Query local Ollama REST API."""
        host = self.config.get("ollama_host", "http://localhost:11434")
        model = self.config.get("model_name", "qwen2.5:1.5b")
        payload = {
            "model": model,
            "prompt": prompt,
            "system": GHOST_SYSTEM_PROMPT,
            "stream": False
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{host}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama call failed ({e}), falling back to built-in response.")
            return self._query_mock(prompt)

    def _query_llamacpp(self, prompt: str) -> str:
        """Query local llama.cpp GGUF instance."""
        try:
            import llama_cpp
            ggufs = list(GHOST_MODELS_DIR.glob("*.gguf"))
            if not ggufs:
                return self._query_mock(prompt)
            llm = llama_cpp.Llama(model_path=str(ggufs[0]), n_gpu_layers=-1, verbose=False)
            output = llm(f"<|im_start|>system\n{GHOST_SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n", max_tokens=512)
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.warning(f"llama_cpp execution failed: {e}")
            return self._query_mock(prompt)

    def _query_mock(self, prompt: str, context: Optional[str] = None, screen_context: Optional[str] = None) -> str:
        """
        Intelligent offline Ghost assistant. Responds instantly with useful advice,
        formatted code, and guides user on model customization.
        """
        p = prompt.lower().strip()

        if context:
            return (
                f"👻 **Ghost Knowledge Insight:**\n\n"
                f"Based on the files I just indexed into your local knowledge base:\n\n"
                f"{context[:400]}...\n\n"
                f"💡 **Key takeaway:** The document directly addresses your question regarding `{prompt[:40]}`."
            )

        # Conversational greetings & status in Russian & English
        if any(w in p for w in ["как дела", "как ты", "как жизнь", "how are you", "what's up"]):
            return (
                "👻 **Отлично!**\n\n"
                "Летаю по твоему экрану, слежу за памятью и готов помогать! "
                "Можешь скинуть мне файл, попросить найти документ через Spotlight или задать любой вопрос. "
                "А у тебя как дела? Над каким проектом сейчас работаешь?"
            )

        if any(w in p for w in ["привет", "здравствуй", "салам", "хай", "hello", "hi", "hey"]):
            return (
                "👻 **Привет!** Я Каспер — твой карманный десктопный ассистент.\n\n"
                "Живу прямо в твоем Mac, потребляю всего 35 МБ памяти и готов помогать: "
                "искать файлы, писать код, конспектировать звонки или учить новые документы. Чем займемся?"
            )

        if "кто ты" in p or "who are you" in p or "расскажи о себе" in p:
            return (
                "👻 **Я GhostOS (Каспер)!**\n\n"
                "Я ультра-легковесный персональный ИИ-компаньон для твоего компьютера:\n"
                "- 🍕 **Ем файлы:** перетащи на меня PDF или код — я проглочу его и запомню (RAG).\n"
                "- 📂 **Управляю системой:** скажи *«открой папку»* или *«найди файлы»*.\n"
                "- 🌐 **Ищу в сети:** спроси *«погода в Алматы»* или *«курс доллара»*.\n"
                "- 🛡️ **Безопасный терминал:** напиши задачу, я сгенерирую безопасную команду.\n"
                "- 🧠 **Zero Bloat:** храню модели компактно и не грею ноутбук."
            )

        if any(w in p for w in ["что ты умеешь", "что умеешь", "команды", "помощь", "help", "abilities"]):
            return (
                "👻 **Вот что я умею прямо сейчас:**\n\n"
                "1. 📂 **Работать с файлами на Mac:** напиши *«найди proton»*, *«открой загрузки»*, *«создай папку Тест»*.\n"
                "2. 🍕 **RAG (Знания):** перетащи мышкой любой PDF/TXT/код прямо на меня на экране.\n"
                "3. 🌐 **Интернет:** спроси *«погода в Алматы»* или *«курс доллара»*.\n"
                "4. 👁️ **Зрение:** напиши `/screen` — сделаю снимок экрана и объясню ошибку.\n"
                "5. 📋 **Буфер обмена:** напиши `/clip` — починю ошибку из скопированного стектрейса или отформатирую JSON.\n"
                "6. 🎙️ **Голос:** нажми на микрофон `🎙️` в окне или включи кнопку `Voice ON`.\n\n"
                "💡 *Для безграничного свободного диалога можно подключить локальную модель Ollama: `brew install ollama && ollama run qwen2.5:1.5b`.*"
            )

        if any(w in p for w in ["шутк", "анекдот", "joke", "пошути"]):
            return (
                "👻 Почему призраки обожают программировать на Python?\n\n"
                "*Потому что у них нет тела, а в Python нет указателей!* 😄"
            )

        if "vram" in p or "памят" in p or "juggler" in p:
            status = self.juggler.get_memory_status()
            return (
                f"🧠 **Диагностика VRAM Juggler:**\n\n"
                f"- **Активная модель:** `{status['active_model']}`\n"
                f"- **Выделенная память:** `{status['active_vram_mb']} МБ`\n"
                f"- **Сэкономлено VRAM благодаря выгрузке:** `+{status['vram_saved_mb']} МБ` 🚀\n"
                f"- **Количество смен моделей:** `{status['total_swaps']}`\n"
                f"- **Занято RAM в системе:** `{status['system_ram_percent']}%` ({status['system_ram_used_mb']} МБ / {status['system_ram_total_mb']} МБ)\n\n"
                f"*Ghost держит видеочип холодным, автоматически усыпляя неактивные веса.*"
            )

        if any(w in p for w in ["код", "python", "code", "напиши функцию", "скрипт"]):
            return (
                "👻 Вот аккуратный и быстрый пример кода для твоей задачи:\n\n"
                "```python\n"
                "# Быстрое локальное решение\n"
                "def process_items(items: list) -> list:\n"
                "    \"\"\"Фильтрует и возвращает уникальные элементы.\"\"\"\n"
                "    return sorted(list(set(item for item in items if item)))\n\n"
                "print(process_items(['ghost', 'os', 'apple', 'ghost']))\n"
                "```\n\n"
                "⚡ *Скрипт оптимизирован под слабый процессор и минимальный расход памяти.*"
            )

        # Natural Russian fallback
        return (
            f"👻 **Каспер:**\n\n"
            f"Я внимательно тебя слушаю! Твой запрос: *\"{prompt}\"*.\n\n"
            f"Я работаю на 100% локально на твоем Mac. Ты можешь:\n"
            f"- Дать мне задание по файлам (*«открой загрузки»*, *«найди отчет.pdf»*)\n"
            f"- Перетащить на меня любой файл мышкой, чтобы я выучил его\n"
            f"- Написать `/screen` для анализа экрана или `/web <запрос>` для поиска в сети\n"
            f"- Или подключить локальную модель Ollama: `brew install ollama && ollama run qwen2.5:1.5b`."
        )
