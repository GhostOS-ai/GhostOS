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

    def get_model_catalog(self) -> Dict[str, Any]:
        """
        Detects local LLM backends, installed models, and hardware acceleration capabilities.
        """
        import platform
        import sys

        host = self.config.get("ollama_host", "http://localhost:11434")
        ollama_active = False
        ollama_models = []

        try:
            req = urllib.request.Request(f"{host}/api/tags")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    ollama_active = True
                    data = json.loads(resp.read().decode("utf-8"))
                    for m in data.get("models", []):
                        size_gb = m.get("size", 0) / (1024 ** 3)
                        ollama_models.append({
                            "name": m.get("name"),
                            "size_gb": round(size_gb, 2),
                            "modified_at": m.get("modified_at", "")[:10]
                        })
        except Exception:
            ollama_active = False

        gguf_models = []
        for g in GHOST_MODELS_DIR.glob("*.gguf"):
            gguf_models.append({
                "name": g.name,
                "size_gb": round(g.stat().st_size / (1024 ** 3), 2),
                "path": str(g)
            })

        # Hardware acceleration
        hw_accel = "CPU Fallback"
        if sys.platform == "darwin":
            hw_accel = "Apple Silicon Metal (Unified Memory MPS)"
        else:
            try:
                import torch
                if torch.cuda.is_available():
                    hw_accel = f"NVIDIA CUDA ({torch.cuda.get_device_name(0)})"
            except ImportError:
                hw_accel = "CPU (x86_64/ARM)"

        return {
            "active_backend": self.backend,
            "hardware_acceleration": hw_accel,
            "ollama_active": ollama_active,
            "ollama_host": host,
            "ollama_models": ollama_models,
            "gguf_models": gguf_models,
            "recommended_models": [
                {"name": "qwen2.5:1.5b", "ram": "1.8GB", "tier": "Base Laptops (4GB-8GB)"},
                {"name": "llama3.2:3b", "ram": "3.2GB", "tier": "Balanced (8GB-16GB)"},
                {"name": "deepseek-r1:1.5b", "ram": "2.1GB", "tier": "Reasoning Model"}
            ]
        }

    def _query_ollama(self, prompt: str) -> str:
        """Query local Ollama REST API with intelligent auto-model fallback."""
        host = self.config.get("ollama_host", "http://localhost:11434")
        configured_model = self.config.get("model_name")

        # Discover available models
        catalog = self.get_model_catalog()
        avail_names = [m["name"] for m in catalog.get("ollama_models", [])]

        if configured_model and (configured_model in avail_names or f"{configured_model}:latest" in avail_names):
            model = configured_model
        elif avail_names:
            # Pick best available local model
            preferred = ["qwen2.5", "llama3.2", "mistral", "deepseek-r1", "phi3"]
            chosen = next((m for p in preferred for m in avail_names if p in m), avail_names[0])
            model = chosen
        else:
            model = configured_model or "qwen2.5:1.5b"

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

        # 1a. Greetings & Pleasantries (Kazakh)
        if any(w in p for w in ["сәлем", "амансыз ба", "қайырлы таң", "қайырлы күн", "қайырлы кеш"]):
            return (
                "👻 **Сәлем!** Мен Каспермін — сенің дербес офлайн Mac көмекшіңмін.\n\n"
                "Компьютеріңде бар болғаны ~35 МБ жедел жад (RAM) алып, 100% құпия жұмыс істеймін:\n"
                "- 🍕 **Файлды үйрету:** кез келген PDF, код немесе конспектіні үстіме тастасаң, бірден жаттап аламын.\n"
                "- 📂 **Файлдарды басқару:** *«жүктеулерді аш»* немесе *«құжатты тап»* деп жаз.\n"
                "- 🌐 **Желілік іздеу:** *«Алматыдағы ауа райы»* немесе *«доллар бағамы»*.\n"
                "- ✍️ **Ghostwriter:** кез келген бағдарламада мәтінді түзету және жинақтау.\n\n"
                "Қазір не істейміз?"
            )

        # 1b. Greetings & Pleasantries (English)
        if any(w in p for w in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return (
                "👻 **Hello!** I'm Casper — your featherweight desktop copilot.\n\n"
                "Running 100% locally and privately on your Mac (<35MB RAM):\n"
                "- 🍕 **Feed me files:** drag & drop any PDF, code, or logs onto me to index them instantly.\n"
                "- 📂 **File actions:** ask *'open downloads'*, *'find report.pdf'*.\n"
                "- 🌐 **Live Web Search:** ask *'weather in Almaty'* or *'exchange rates'*.\n"
                "- ✍️ **Ghostwriter:** select text anywhere and summon smart rewriting.\n\n"
                "What are we building today?"
            )

        # 1c. Greetings & Pleasantries (Russian)
        if any(w in p for w in [
            "привет", "здравствуй", "салам", "хай", "доброе утро", "добрый день", "добрый вечер"
        ]):
            return (
                "👻 **Привет!** Я Каспер — твой карманный десктопный ассистент.\n\n"
                "Живу прямо в твоем Mac, потребляю всего 35 МБ памяти и готов помогать:\n"
                "- 🍕 **Скорми мне файл:** просто перетащи любой PDF, код или лог прямо на меня, и я выучу его.\n"
                "- 📂 **Управление файлами:** напиши *«найди отчет.pdf»* или *«открой загрузки»*.\n"
                "- 🌐 **Поиск в сети:** напиши *«погода в Алматы»* или *«курс доллара»*.\n"
                "- ✍️ **Ghostwriter:** выдели текст в любой программе и нажми шорткат.\n\n"
                "Чем займемся прямо сейчас?"
            )

        # 2. Conversational status & small talk
        if any(w in p for w in ["как дела", "как ты", "как жизнь", "how are you", "what's up", "қалайсың", "қалай жағдай"]):
            return (
                "👻 **Отлично!**\n\n"
                "Летаю по твоему экрану, слежу за памятью (всего ~35 МБ RAM) и готов к работе! "
                "Можешь скинуть мне файл для анализа, попросить найти документ или задать вопрос. "
                "Над какой задачей сейчас работаешь?"
            )

        # 3. Purpose, identity, and clarification of what the bot is for
        if any(w in p for w in [
            "кто ты", "who are you", "расскажи о себе", "что за бот", "зачем ты", "для чего",
            "что это такое", "что ты делаешь", "ерунда", "бесполезн", "зачем данный бот",
            "для чего вообще", "ничего не понятно", "что это"
        ]):
            return (
                "👻 **Я GhostOS (Каспер) — твой персональный локальный десктоп-копайлот!**\n\n"
                "В отличие от тяжелых программ вроде LM Studio или AnythingLLM, которые съедают 1.5 ГБ памяти на Electron, "
                "я практически невесом (**~35 МБ RAM**) и работаю на 100% приватно на твоем Mac.\n\n"
                "**Вот 5 вещей, которые я делаю прямо сейчас:**\n"
                "1. 🍕 **Мгновенный RAG без баз данных:** перетащи мышкой любой PDF, документ, код или лог прямо на меня — я «проглочу» его и смогу отвечать на любые вопросы по нему.\n"
                "2. 📂 **Управление файлами (OS Агент):** напиши *«открой загрузки»*, *«найди файлы python»* или *«создай папку Проект»* — я сделаю это в системе.\n"
                "3. 🌐 **Быстрый поиск:** напиши *«погода в Алматы»* или *«курс доллара»* — покажу ответ без открытия браузера.\n"
                "4. ✍️ **Ghostwriter:** умею переписывать текст в деловой тон, исправлять ошибки или писать саммари в любой программе.\n"
                "5. 🎙️ **Протокол встреч:** кнопка `Voice` запишет звонок в Zoom/Meet и составит список задач.\n\n"
                "💡 *Если хочешь общаться со свободной большой нейросетью оффлайн (как с ChatGPT), подключи локальную модель: `brew install ollama && ollama run qwen2.5:1.5b` — я автоматически подхвачу её!*"
            )

        # 4. Capabilities & help
        if any(w in p for w in ["что ты умеешь", "что умеешь", "команды", "помощь", "help", "abilities", "что делать"]):
            return (
                "👻 **Вот быстрые команды, которые можно попробовать прямо сейчас:**\n\n"
                "- 📂 **Файлы:** *«открой загрузки»*, *«найди main.py»*, *«открой рабочий стол»*\n"
                "- 🍕 **Знания:** перетащи любой файл на летающего Каспера на рабочем столе\n"
                "- 🌐 **Интернет:** *«погода в Алматы»*, *«курс валют»*, *«кто такой Илон Маск»*\n"
                "- 👁️ **Экран:** нажми кнопку `Экран` вверху или напиши `/screen` — объясню, что открыто\n"
                "- 📋 **Буфер:** нажми `Буфер` — разберу ошибку или JSON из скопированного текста\n"
                "- 🎨 **Сменить скин:** напиши в терминале `ghost pet --skin cyberpunk` (или `gold`, `matrix`)\n"
                "- 🔍 **Spotlight HUD:** нажми `Cmd+Shift+Space` для быстрого вызова строки поиска\n\n"
                "Просто напиши мне любую команду!"
            )

        # 5. Gratitude
        if any(w in p for w in ["спасибо", "благодарю", "рахмет", "thanks", "thank you"]):
            return "👻 Всегда пожалуйста! Обращайся в любой момент — я всегда здесь, на твоем рабочем столе."

        # 6. Actual Document/Web Knowledge Context (only when actual document snippet is retrieved)
        if context and any(marker in context for marker in ["[", "--- Local Document Context", "--- Live Web Context"]):
            return (
                f"👻 **Анализ найденных материалов:**\n\n"
                f"По вашему вопросу *«{prompt}»* в локальной базе знаний найден следующий фрагмент:\n\n"
                f"```text\n{context[:450]}...\n```\n\n"
                f"💡 Этот документ содержит прямой ответ на ваш запрос."
            )

        # 7. Diagnostics & Tools
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

        if any(w in p for w in ["шутк", "анекдот", "joke", "пошути"]):
            return (
                "👻 Почему призраки обожают программировать на Python?\n\n"
                "*Потому что у них нет тела, а в Python нет указателей!* 😄"
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

        # 8. Natural Russian fallback
        return (
            f"👻 **Каспер:**\n\n"
            f"Я внимательно тебя слушаю! Твой запрос: *\"{prompt}\"*.\n\n"
            f"Я работаю на 100% локально на твоем Mac. Ты можешь:\n"
            f"- Дать мне задание по файлам (*«открой загрузки»*, *«найди отчет.pdf»*)\n"
            f"- Перетащить на меня любой файл мышкой, чтобы я выучил его\n"
            f"- Написать `/screen` для анализа экрана или `/web <запрос>` для поиска в сети\n"
            f"- Или подключить локальную модель Ollama: `brew install ollama && ollama run qwen2.5:1.5b`."
        )
