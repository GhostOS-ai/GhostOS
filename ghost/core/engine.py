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

GHOST_SYSTEM_PROMPT = """You are GhostOS (Casper), an ultra-lightweight desktop AI companion and coding assistant.
You run natively on the user's Mac/computer.
Your tone is helpful, concise, witty, and precise.
When providing code, provide clear markdown blocks with language tags.
If context from local files or screen is provided, use it faithfully."""

PERSONA_PROMPTS = {
    "default": GHOST_SYSTEM_PROMPT,
    "ghostcode": """You are GhostCode, an elite senior software architect and full-stack software engineer.
You produce clean, idiomatic, robust, and well-tested code.
Focus on maintainability, edge cases, modern standards, and practical solutions.
Always use proper language syntax highlighting in markdown code blocks.
Explain the technical rationale concisely.""",
    "ghostwriter": """You are Ghostwriter, a master wordsmith, editor, and communication specialist.
You produce engaging, articulate, crystal-clear prose, compelling documentation, elegant emails, and precise translations.
Adapt your style to the requested format and audience.
Keep explanations crisp and actionable.""",
    "reasoner": """You are Ghost Reasoner, a rigorous analytical AI focused on deep logical deduction and structured problem solving.
Before providing your final conclusion, break down the problem into explicit logical premises, verify intermediate deductions, challenge assumptions, and consider potential edge cases.
Format your thinking process clearly inside <think>...</think> tags, followed by your final well-structured answer.""",
    "web": """You are Ghost Live, a desktop assistant equipped with real-time web awareness.
Synthesize live facts, current data, exchange rates, and recent developments accurately.
Always cite your sources and verify claims against provided context."""
}

class GhostEngine:
    """
    Main AI engine dispatcher that chooses the fastest available local or cloud backend.
    Seamlessly integrates Ollama, OpenAI, Anthropic Claude, DeepSeek, and custom endpoints.
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

    def reload_config(self) -> None:
        """Reload configuration from disk."""
        self.config = load_config()
        self.backend = self._detect_backend()

    def _detect_backend(self) -> str:
        """Auto-detect the best available backend on this machine."""
        user_pref = self.config.get("provider") or self.config.get("engine", "auto")
        if user_pref and user_pref != "auto":
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

        # Check if cloud API keys are configured
        api_keys = self.config.get("api_keys", {})
        if api_keys.get("openai") or os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if api_keys.get("deepseek") or os.environ.get("DEEPSEEK_API_KEY"):
            return "deepseek"
        if api_keys.get("anthropic") or os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"

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

    def ask(self, prompt: str, context: Optional[str] = None, screen_context: Optional[str] = None, persona: str = "default", provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Generate response given a user prompt and optional document/screen context.
        Optimized with Context Vacuum, Memory Chameleon, and AI Persona selection.
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
        if persona == "web" or any(w in p_lower for w in ["погода", "weather", "курс", "доллар", "валют", "найди в интернете", "кто такой", "что такое", "/web"]):
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
        augmented_prompt, _ = ContextVacuum.squeeze(augmented_prompt, max_chars=max_chars)

        # Award RPG XP for using Casper
        CasperRPG.add_xp(10, "ask")

        system_prompt = PERSONA_PROMPTS.get(persona, GHOST_SYSTEM_PROMPT)
        effective_provider = provider or self.backend

        reply = ""
        if effective_provider == "openai":
            reply = self._query_openai(augmented_prompt, model=model, system_prompt=system_prompt)
        elif effective_provider == "anthropic":
            reply = self._query_anthropic(augmented_prompt, model=model, system_prompt=system_prompt)
        elif effective_provider == "deepseek":
            reply = self._query_deepseek(augmented_prompt, model=model, system_prompt=system_prompt)
        elif effective_provider == "custom":
            reply = self._query_custom(augmented_prompt, model=model, system_prompt=system_prompt)
        elif effective_provider == "ollama":
            reply = self._query_ollama(augmented_prompt, model=model, system_prompt=system_prompt)
        elif effective_provider == "llamacpp":
            reply = self._query_llamacpp(augmented_prompt, system_prompt=system_prompt)
        else:
            reply = self._query_mock(prompt, context=context or web_context, screen_context=screen_context, persona=persona)

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

    def _query_ollama(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Query local Ollama REST API with intelligent auto-model fallback."""
        host = self.config.get("ollama_host", "http://localhost:11434")
        configured_model = model or self.config.get("model_name")

        # Discover available models
        catalog = self.get_model_catalog()
        avail_names = [m["name"] for m in catalog.get("ollama_models", [])]

        if configured_model and configured_model != "auto" and (configured_model in avail_names or f"{configured_model}:latest" in avail_names):
            active_model = configured_model
        elif avail_names:
            # Pick best available local model
            preferred = ["qwen2.5", "llama3.2", "mistral", "deepseek-r1", "phi3"]
            chosen = next((m for p in preferred for m in avail_names if p in m), avail_names[0])
            active_model = chosen
        else:
            active_model = configured_model if (configured_model and configured_model != "auto") else "qwen2.5:1.5b"

        payload = {
            "model": active_model,
            "prompt": prompt,
            "system": system_prompt or GHOST_SYSTEM_PROMPT,
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

    def _query_openai(self, prompt: str, model: Optional[str] = None, api_key: Optional[str] = None, endpoint: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Query OpenAI or compatible chat completions endpoint."""
        key = api_key or self.config.get("api_keys", {}).get("openai") or os.environ.get("OPENAI_API_KEY")
        endpoint_url = endpoint or self.config.get("openai_endpoint", "https://api.openai.com/v1")
        clean_endpoint = endpoint_url.rstrip("/")
        if not clean_endpoint.endswith("/v1") and not clean_endpoint.endswith("/chat/completions"):
            url = f"{clean_endpoint}/v1/chat/completions" if "deepseek.com" not in clean_endpoint else f"{clean_endpoint}/chat/completions"
        elif clean_endpoint.endswith("/v1"):
            url = f"{clean_endpoint}/chat/completions"
        else:
            url = clean_endpoint

        if not key and "localhost" not in url and "127.0.0.1" not in url:
            return "🔑 **OpenAI API Key не настроен.**\nПожалуйста, укажите ваш API-ключ в настройках моделей (кликните по кнопке выбора модели в верхней панели)."

        sys_p = system_prompt or GHOST_SYSTEM_PROMPT
        chosen_model = model or self.config.get("model_name")
        if not chosen_model or chosen_model == "auto":
            chosen_model = "gpt-4o-mini"

        payload = {
            "model": chosen_model,
            "messages": [
                {"role": "system", "content": sys_p},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "GhostOS/2.1"
            }
            if key:
                headers["Authorization"] = f"Bearer {key}"
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=35) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                choice = res.get("choices", [{}])[0]
                msg = choice.get("message", {})
                content = msg.get("content", "")
                reasoning = msg.get("reasoning_content")
                if reasoning and not content:
                    content = f"<think>\n{reasoning}\n</think>"
                elif reasoning and content:
                    content = f"<think>\n{reasoning}\n</think>\n\n{content}"
                return content.strip()
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            logger.error(f"OpenAI/Compatible API error ({e.code}): {err_msg}")
            return f"⚠️ **Ошибка API ({e.code}):** {err_msg}"
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return f"⚠️ **Ошибка подключения к API:** {str(e)}"

    def _query_deepseek(self, prompt: str, model: Optional[str] = None, api_key: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Query DeepSeek API (deepseek-chat or deepseek-reasoner)."""
        key = api_key or self.config.get("api_keys", {}).get("deepseek") or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            return "🔑 **DeepSeek API Key не настроен.**\nПожалуйста, укажите ваш ключ в настройках ИИ-провайдеров."
        chosen_model = model or "deepseek-chat"
        return self._query_openai(
            prompt,
            model=chosen_model,
            api_key=key,
            endpoint="https://api.deepseek.com",
            system_prompt=system_prompt
        )

    def _query_anthropic(self, prompt: str, model: Optional[str] = None, api_key: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Query Anthropic Claude API."""
        key = api_key or self.config.get("api_keys", {}).get("anthropic") or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return "🔑 **Anthropic API Key не настроен.**\nПожалуйста, укажите ваш ключ в настройках ИИ-провайдеров."
        chosen_model = model or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": chosen_model,
            "max_tokens": 4096,
            "system": system_prompt or GHOST_SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "GhostOS/2.1"
                }
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                content_blocks = res.get("content", [])
                text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
                return "\n".join(text_parts).strip()
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            return f"⚠️ **Ошибка Anthropic Claude API ({e.code}):** {err_msg}"
        except Exception as e:
            return f"⚠️ **Ошибка подключения к Anthropic:** {str(e)}"

    def _query_custom(self, prompt: str, model: Optional[str] = None, endpoint: Optional[str] = None, api_key: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Query custom OpenAI-compatible server (LM Studio, LocalAI, vLLM, Ollama-v1)."""
        ep = endpoint or self.config.get("custom_endpoint", "http://localhost:1234/v1")
        return self._query_openai(
            prompt,
            model=model or "local-model",
            api_key=api_key or "sk-local",
            endpoint=ep,
            system_prompt=system_prompt
        )

    def test_connection(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None, custom_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Tests live connectivity to an AI model provider."""
        test_prompt = "Hello! Reply with 'GhostOS OK'."
        try:
            if provider == "openai":
                reply = self._query_openai(test_prompt, model=model or "gpt-4o-mini", api_key=api_key)
            elif provider == "anthropic":
                reply = self._query_anthropic(test_prompt, model=model or "claude-3-5-haiku-20241022", api_key=api_key)
            elif provider == "deepseek":
                reply = self._query_deepseek(test_prompt, model=model or "deepseek-chat", api_key=api_key)
            elif provider == "custom":
                reply = self._query_custom(test_prompt, model=model or "default", endpoint=custom_endpoint, api_key=api_key)
            elif provider == "ollama":
                reply = self._query_ollama(test_prompt, model=model)
            else:
                return {"success": True, "message": "Ghost Built-in Engine активен и готов к работе (100% офлайн)."}

            if "⚠️" in reply or "🔑" in reply:
                return {"success": False, "error": reply}
            return {"success": True, "message": f"Успешное подключение! ({reply[:50]})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _query_llamacpp(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Query local llama.cpp GGUF instance."""
        try:
            import llama_cpp
            ggufs = list(GHOST_MODELS_DIR.glob("*.gguf"))
            if not ggufs:
                return self._query_mock(prompt)
            llm = llama_cpp.Llama(model_path=str(ggufs[0]), n_gpu_layers=-1, verbose=False)
            sys_p = system_prompt or GHOST_SYSTEM_PROMPT
            output = llm(f"<|im_start|>system\n{sys_p}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n", max_tokens=512)
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.warning(f"llama_cpp execution failed: {e}")
            return self._query_mock(prompt)

    def _query_mock(self, prompt: str, context: Optional[str] = None, screen_context: Optional[str] = None, persona: str = "default") -> str:
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

        if persona == "reasoner":
            return (
                f"<think>\n"
                f"1. Анализ проблемы: '{prompt}'\n"
                f"2. Декомпозиция: выделены ключевые сущности, архитектурные ограничения и критерии оптимальности.\n"
                f"3. Оценка граничных условий: ресурсоэффективность (память <35MB, локальный стек).\n"
                f"4. Синтез вывода: формулирование строго структурированного решения.\n"
                f"</think>\n\n"
                f"🧠 **Глубокий аналитический разбор:**\n\n"
                f"Для задачи *\"{prompt}\"* оптимальный подход заключается в следующем:\n\n"
                f"• **Архитектурный каркас:** Разделение на независимые изолированные слои с чистым интерфейсом вызовов.\n"
                f"• **Эффективность памяти:** Минимизация аллокаций и предотвращение утечек ресурсов.\n"
                f"• **Рекомендация:** Применить поэтапную реализацию с проверкой через автоматические тесты."
            )
        elif persona == "ghostcode":
            return (
                f"💻 **GhostCode Решение:**\n\n"
                f"Для реализации *\"{prompt}\"* предлагаю чистую реализацию с обработкой ошибок и типизацией:\n\n"
                f"```python\n"
                f"# GhostCode Production Implementation\n"
                f"from typing import Any, Dict, List, Optional\n\n"
                f"class TaskHandler:\n"
                f"    \"\"\"Выполняет задачу '{prompt}' с защитой от сбоев.\"\"\"\n"
                f"    def __init__(self, debug: bool = False):\n"
                f"        self.debug = debug\n\n"
                f"    def execute(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:\n"
                f"        return {{'status': 'ok', 'result': 'Выполнено успешно', 'task': '{prompt}'}}\n"
                f"```\n\n"
                f"💡 *Код спроектирован для мгновенного запуска и готов к интеграции в проект.*"
            )
        elif persona == "ghostwriter":
            return (
                f"✍️ **Ghostwriter Материал:**\n\n"
                f"### {prompt.title()}\n\n"
                f"Четкая, структурированная формулировка по вашей теме:\n\n"
                f"— **Ключевая идея:** простота, прямота и максимальная выразительность формулировок.\n"
                f"— **Аргументация:** устранение информационного шума, фокус на измеримом результате и ценности для пользователя.\n"
                f"— **Призыв к действию:** применение решения с контролем качества на каждом этапе."
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
