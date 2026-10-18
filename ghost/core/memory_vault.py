"""
GhostOS Memory Vault
Cross-session long-term user facts and context graph stored in local SQLite.
Zero external vector DBs, zero VRAM overhead, instant retrieval.
"""
import re
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ghost.config import GHOST_DB_PATH, ensure_dirs

class MemoryVault:
    """
    Manages long-term personal user facts, developer preferences, and project context.
    Allows Casper to remember facts across restarts with zero cloud leaks.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryVault, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is not None:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            return
        if getattr(self, "_initialized", False):
            return
        ensure_dirs()
        self.db_path = GHOST_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create the memory_vault table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    fact_key TEXT UNIQUE NOT NULL,
                    fact_value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_vault_category ON memory_vault (category);
            """)
            conn.commit()

    def remember(self, key: str, value: str, category: str = "general", confidence: float = 1.0) -> bool:
        """Store or update a learned fact."""
        clean_key = key.strip().lower()
        clean_val = value.strip()
        if not clean_key or not clean_val:
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO memory_vault (category, fact_key, fact_value, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(fact_key) DO UPDATE SET
                    fact_value = excluded.fact_value,
                    category = excluded.category,
                    confidence = excluded.confidence,
                    updated_at = excluded.updated_at;
            """, (category, clean_key, clean_val, confidence, now))
            conn.commit()
            return True

    def recall(self, key: str) -> Optional[str]:
        """Fetch a specific fact by its key."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fact_value FROM memory_vault WHERE fact_key = ?", (key.strip().lower(),))
            row = cursor.fetchone()
            return row["fact_value"] if row else None

    def forget(self, key: str) -> bool:
        """Delete a fact from memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory_vault WHERE fact_key = ?", (key.strip().lower(),))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_facts(self) -> List[Dict[str, Any]]:
        """List all facts currently in the memory vault."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, fact_key, fact_value, updated_at FROM memory_vault ORDER BY category, fact_key")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_context_block(self, max_facts: int = 10) -> str:
        """
        Format learned facts into a compact system context prompt for the LLM.
        """
        facts = self.get_all_facts()
        if not facts:
            return ""

        lines = ["User Personal Memory & Context:"]
        for f in facts[:max_facts]:
            lines.append(f"- {f['fact_key']}: {f['fact_value']}")
        return "\n".join(lines)

    def auto_extract_facts(self, text: str) -> List[Dict[str, str]]:
        """
        Heuristic fast fact extractor from user chat queries without requiring an LLM.
        Matches common declarative statements like 'я пишу на python', 'my project is X'.
        """
        extracted = []
        t = text.strip()

        # 1. Name: "меня зовут X" / "my name is X"
        m = re.search(r'(?:меня зовут|мое имя|my name is|i am)\s+([A-Za-zА-Яа-яЁё]+)', t, re.IGNORECASE)
        if m:
            extracted.append({"key": "user_name", "value": m.group(1), "category": "profile"})

        # 2. Tech stack: "я пишу на python/flutter/rust" / "i code in rust"
        m = re.search(r'(?:я пишу на|разрабатываю на|мой стек|i code in|i write in|my tech stack is)\s+([^\.,!\?]+)', t, re.IGNORECASE)
        if m:
            extracted.append({"key": "tech_stack", "value": m.group(1).strip(), "category": "preferences"})

        # 3. Project name: "мой проект X" / "my project is X"
        m = re.search(r'(?:мой проект|разрабатываю проект|my project is|working on)\s+([A-Za-z0-9_\-]+)', t, re.IGNORECASE)
        if m:
            extracted.append({"key": "current_project", "value": m.group(1).strip(), "category": "project"})

        for item in extracted:
            self.remember(item["key"], item["value"], item["category"])

        return extracted
