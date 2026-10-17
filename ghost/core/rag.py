"""
GhostOS Zero-DB RAG Engine
Ultra-lightweight local document search & indexing powered by SQLite FTS5.
Zero bloated external vector DBs, zero Docker, zero memory overhead.
"""
import os
import re
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from ghost.config import GHOST_DB_PATH, ensure_dirs

class ZeroDbRAG:
    """
    Local knowledge base engine using SQLite FTS5 for instant sub-millisecond retrieval.
    Ingests PDFs, text, markdown, source code, and Office documents.
    """

    SUPPORTED_TEXT_EXTS = {
        ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx",
        ".html", ".css", ".json", ".csv", ".yaml", ".yml",
        ".sh", ".bash", ".zsh", ".rs", ".go", ".c", ".cpp", ".h"
    }

    def __init__(self, db_path: Optional[Path] = None):
        ensure_dirs()
        self.db_path = db_path or GHOST_DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Create tables and full-text search indexes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    size_bytes INTEGER DEFAULT 0,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
                );
            """)

            # SQLite FTS5 Virtual Table for BM25 ranking
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    content,
                    content='chunks',
                    content_rowid='id'
                );
            """)

            # Triggers to keep FTS table synchronized with chunks
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                    INSERT INTO chunks_fts(rowid, content) VALUES (new.id, new.content);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, content) VALUES('delete', old.id, old.content);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, content) VALUES('delete', old.id, old.content);
                    INSERT INTO chunks_fts(rowid, content) VALUES (new.id, new.content);
                END;
            """)
            conn.commit()

    def _extract_text(self, file_path: Path) -> str:
        """Extract text content based on file extension."""
        suffix = file_path.suffix.lower()

        if suffix in self.SUPPORTED_TEXT_EXTS:
            try:
                return file_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                return f"[Error reading text file: {e}]"

        elif suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                text_parts = []
                for idx, page in enumerate(reader.pages):
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(f"--- Page {idx+1} ---\n{extracted}")
                return "\n\n".join(text_parts)
            except Exception as e:
                return f"[Error parsing PDF: {e}]"

        elif suffix == ".docx":
            try:
                import docx
                doc = docx.Document(str(file_path))
                return "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                return f"[Error parsing DOCX: {e}]"

        return ""

    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """Split text into overlapping semantic blocks."""
        text = text.strip()
        if not text:
            return []

        # Split on paragraph or newline boundaries first
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if current_length + len(p) > chunk_size and current_chunk:
                combined = "\n\n".join(current_chunk)
                chunks.append(combined)
                # Keep last paragraph for overlap
                current_chunk = [current_chunk[-1]] if len(current_chunk) > 1 else []
                current_length = sum(len(x) for x in current_chunk)

            current_chunk.append(p)
            current_length += len(p)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Fallback for huge unstructured blobs
        if not chunks and text:
            for i in range(0, len(text), chunk_size - overlap):
                chunks.append(text[i:i + chunk_size])

        return chunks

    def ingest_file(self, file_path_str: str) -> Dict[str, Any]:
        """
        Ingest a file into SQLite knowledge base.
        Called when Ghost Pet 'eats' a file or via CLI.
        """
        path = Path(file_path_str).expanduser().resolve()
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        text = self._extract_text(path)
        if not text or len(text.strip()) < 10:
            return {"success": False, "error": "File empty or unsupported format."}

        chunks = self._chunk_text(text)
        size_bytes = path.stat().st_size

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Remove previous version if re-ingesting
            cursor.execute("DELETE FROM documents WHERE path = ?", (str(path),))

            cursor.execute("""
                INSERT INTO documents (path, filename, file_type, size_bytes)
                VALUES (?, ?, ?, ?)
            """, (str(path), path.name, path.suffix.lower(), size_bytes))
            
            doc_id = cursor.lastrowid

            for idx, chunk_content in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO chunks (doc_id, chunk_index, content)
                    VALUES (?, ?, ?)
                """, (doc_id, idx, chunk_content))

            conn.commit()

        return {
            "success": True,
            "filename": path.name,
            "path": str(path),
            "chunks_count": len(chunks),
            "size_kb": round(size_bytes / 1024, 1),
            "message": f"Chomp! Ghost ate '{path.name}' ({len(chunks)} chunks indexed)."
        }

    def ingest_directory(self, dir_path_str: str, max_files: int = 50) -> Dict[str, Any]:
        """Recursively index a directory of documents or code."""
        dir_path = Path(dir_path_str).expanduser().resolve()
        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {dir_path}"}

        ingested = []
        skipped = 0

        for root, _, files in os.walk(dir_path):
            if any(part.startswith((".", "node_modules", "__pycache__", "venv")) for part in Path(root).parts):
                continue
            for file in files:
                if len(ingested) >= max_files:
                    break
                fpath = Path(root) / file
                if fpath.suffix.lower() in self.SUPPORTED_TEXT_EXTS or fpath.suffix.lower() in {".pdf", ".docx"}:
                    res = self.ingest_file(str(fpath))
                    if res.get("success"):
                        ingested.append(res["filename"])
                    else:
                        skipped += 1

        return {
            "success": True,
            "total_ingested": len(ingested),
            "skipped": skipped,
            "files": ingested
        }

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Sub-millisecond BM25 keyword & full-text search across all ingested documents.
        """
        clean_query = re.sub(r'[^\w\s]', ' ', query).strip()
        if not clean_query:
            return []

        # Split into search terms for FTS5
        terms = [f'"{term}"*' for term in clean_query.split() if len(term) > 1]
        fts_query = " OR ".join(terms) if terms else f'"{clean_query}"*'

        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT c.id, c.content, c.chunk_index, d.filename, d.path, bm25(chunks_fts) as rank
                    FROM chunks_fts
                    JOIN chunks c ON chunks_fts.rowid = c.id
                    JOIN documents d ON c.doc_id = d.id
                    WHERE chunks_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (fts_query, top_k))
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                # Fallback to LIKE if FTS query syntax fails
                cursor.execute("""
                    SELECT c.id, c.content, c.chunk_index, d.filename, d.path, 1.0 as rank
                    FROM chunks c
                    JOIN documents d ON c.doc_id = d.id
                    WHERE c.content LIKE ?
                    LIMIT ?
                """, (f"%{clean_query}%", top_k))
                rows = cursor.fetchall()

            for row in rows:
                results.append({
                    "chunk_id": row["id"],
                    "filename": row["filename"],
                    "path": row["path"],
                    "content": row["content"],
                    "rank": float(row["rank"])
                })

        return results

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents and chunk statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.filename, d.path, d.file_type, d.size_bytes, d.ingested_at,
                       COUNT(c.id) as chunk_count
                FROM documents d
                LEFT JOIN chunks c ON d.id = c.doc_id
                GROUP BY d.id
                ORDER BY d.ingested_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def clear(self) -> None:
        """Clear all indexed documents."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM documents;")
            conn.commit()
