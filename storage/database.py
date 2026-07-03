import json
import sqlite3
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
                filename TEXT NOT NULL DEFAULT '',
                file_type TEXT NOT NULL DEFAULT '',
                file_size INTEGER NOT NULL DEFAULT 0,
                doc_type TEXT NOT NULL DEFAULT '',
                processing_status TEXT NOT NULL DEFAULT '',
                raw_text TEXT NOT NULL DEFAULT '',
                cleaned_text TEXT NOT NULL DEFAULT '',
                structured_data TEXT NOT NULL DEFAULT '{}',
                processing_time REAL NOT NULL DEFAULT 0.0,
                performance_metrics TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )
            """
        )
        _migrate_add_column(conn, "doc_type", "TEXT NOT NULL DEFAULT ''")
        _migrate_add_column(conn, "processing_status", "TEXT NOT NULL DEFAULT ''")
        _migrate_add_column(conn, "performance_metrics", "TEXT NOT NULL DEFAULT '{}'")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents(doc_type)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status)"
        )


def _migrate_add_column(conn: sqlite3.Connection, col: str, col_def: str) -> None:
    try:
        conn.execute(f"ALTER TABLE documents ADD COLUMN {col} {col_def}")
    except sqlite3.OperationalError:
        pass


def insert_document(doc: Document) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO documents (filename, file_type, file_size, doc_type,
                                   processing_status, raw_text, cleaned_text,
                                   structured_data, processing_time,
                                   performance_metrics, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.filename,
                doc.file_type,
                doc.file_size,
                doc.doc_type,
                doc.processing_status,
                doc.raw_text,
                doc.cleaned_text,
                json.dumps(doc.structured_data),
                doc.processing_time,
                json.dumps(doc.performance_metrics),
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
                WHERE filename LIKE ? OR doc_type LIKE ? OR raw_text LIKE ?
                   OR cleaned_text LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_doc(r) for r in rows]


def search_documents_filtered(
    query: str = "",
    doc_type_filter: str = "",
    file_type_filter: str = "",
    status_filter: str = "",
    date_filter: str = "",
    limit: int = 50,
) -> list[Document]:
    conditions: list[str] = []
    params: list[Any] = []

    if query:
        conditions.append(
            "(filename LIKE ? OR doc_type LIKE ? OR file_type LIKE ? "
            "OR raw_text LIKE ? OR cleaned_text LIKE ? OR structured_data LIKE ?)"
        )
        like = f"%{query}%"
        params.extend([like] * 6)

    if doc_type_filter:
        conditions.append("doc_type = ?")
        params.append(doc_type_filter)

    if file_type_filter:
        conditions.append("file_type = ?")
        params.append(file_type_filter)

    if status_filter:
        conditions.append("processing_status = ?")
        params.append(status_filter)

    if date_filter:
        conditions.append("created_at LIKE ?")
        params.append(f"{date_filter}%")

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sql = f"SELECT * FROM documents {where} ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_doc(r) for r in rows]


def get_all_documents(limit: int = 0) -> list[Document]:
    sql = "SELECT * FROM documents ORDER BY created_at DESC"
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
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


def get_analytics() -> dict[str, Any]:
    result: dict[str, Any] = {
        "total_documents": 0,
        "documents_by_type": {},
        "documents_by_file_type": {},
        "documents_by_status": {},
        "avg_processing_time": 0.0,
        "avg_extraction_time": 0.0,
        "total_characters": 0,
        "most_common_doc_type": "N/A",
        "recent_uploads": [],
        "success_rate": 0.0,
    }
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        result["total_documents"] = row[0] or 0

        for r in conn.execute(
            "SELECT doc_type, COUNT(*) as cnt FROM documents WHERE doc_type != '' GROUP BY doc_type ORDER BY cnt DESC"
        ).fetchall():
            result["documents_by_type"][r["doc_type"]] = r["cnt"]

        for r in conn.execute(
            "SELECT file_type, COUNT(*) as cnt FROM documents WHERE file_type != '' GROUP BY file_type ORDER BY cnt DESC"
        ).fetchall():
            result["documents_by_file_type"][r["file_type"]] = r["cnt"]

        for r in conn.execute(
            "SELECT processing_status, COUNT(*) as cnt FROM documents WHERE processing_status != '' GROUP BY processing_status"
        ).fetchall():
            result["documents_by_status"][r["processing_status"]] = r["cnt"]

        row = conn.execute("SELECT AVG(processing_time) FROM documents WHERE processing_time > 0").fetchone()
        result["avg_processing_time"] = round(row[0] or 0.0, 2)

        row = conn.execute("SELECT SUM(LENGTH(cleaned_text)) FROM documents").fetchone()
        result["total_characters"] = row[0] or 0

        extract_times: list[float] = []
        for r in conn.execute("SELECT performance_metrics FROM documents WHERE performance_metrics != '{}'").fetchall():
            pm = _load_structured_data(r["performance_metrics"])
            et = pm.get("extract_time", 0)
            if et > 0:
                extract_times.append(et)
        if extract_times:
            result["avg_extraction_time"] = round(sum(extract_times) / len(extract_times), 3)

        if result["documents_by_type"]:
            result["most_common_doc_type"] = max(result["documents_by_type"], key=result["documents_by_type"].get)

        for r in conn.execute(
            "SELECT filename, doc_type, created_at FROM documents ORDER BY created_at DESC LIMIT 10"
        ).fetchall():
            result["recent_uploads"].append({
                "filename": r["filename"],
                "doc_type": r["doc_type"],
                "created_at": r["created_at"],
            })

        total = result["total_documents"]
        if total > 0:
            complete = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE processing_status = 'complete'"
            ).fetchone()[0] or 0
            result["success_rate"] = round(complete / total * 100, 1)

    return result


def _load_structured_data(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        import ast
        result = ast.literal_eval(raw)
        if isinstance(result, dict):
            return result
    except Exception:
        pass
    return {}


def _row_to_doc(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        filename=row["filename"],
        file_type=row["file_type"],
        file_size=row["file_size"],
        doc_type=row["doc_type"] if "doc_type" in row.keys() else "",
        processing_status=row["processing_status"] if "processing_status" in row.keys() else "",
        raw_text=row["raw_text"],
        cleaned_text=row["cleaned_text"],
        structured_data=_load_structured_data(row["structured_data"]),
        processing_time=row["processing_time"],
        performance_metrics=_load_structured_data(row["performance_metrics"]),
        created_at=row["created_at"],
    )
