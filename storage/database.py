import sqlite3
from datetime import datetime, timezone
from typing import Any

from config import DB_PATH
from storage.models import Document


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL DEFAULT '',
                file_size INTEGER NOT NULL DEFAULT 0,
                raw_text TEXT NOT NULL DEFAULT '',
                cleaned_text TEXT NOT NULL DEFAULT '',
                structured_data TEXT NOT NULL DEFAULT '{}',
                processing_time REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)"
        )


def insert_document(doc: Document) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO documents (filename, file_type, file_size, raw_text,
                                   cleaned_text, structured_data, processing_time,
                                   created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.filename,
                doc.file_type,
                doc.file_size,
                doc.raw_text,
                doc.cleaned_text,
                str(doc.structured_data),
                doc.processing_time,
                doc.created_at,
            ),
        )
        return cur.lastrowid


def search_documents(query: str = "", limit: int = 50) -> list[Document]:
    with get_connection() as conn:
        if query:
            rows = conn.execute(
                """
                SELECT * FROM documents
                WHERE filename LIKE ? OR raw_text LIKE ? OR cleaned_text LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_doc(r) for r in rows]


def get_document(doc_id: int) -> Document | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
        return _row_to_doc(row) if row else None


def delete_document(doc_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cur.rowcount > 0


def _row_to_doc(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        filename=row["filename"],
        file_type=row["file_type"],
        file_size=row["file_size"],
        raw_text=row["raw_text"],
        cleaned_text=row["cleaned_text"],
        structured_data=__import__("json").loads(row["structured_data"]),
        processing_time=row["processing_time"],
        created_at=row["created_at"],
    )
