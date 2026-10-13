
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "prism_data"
FILES = DATA / "files"
DB = DATA / "history.sqlite3"

DATA.mkdir(exist_ok=True)
FILES.mkdir(exist_ok=True)

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT DEFAULT '',
            content TEXT DEFAULT '',
            file_path TEXT DEFAULT ''
        )
    """)
    conn.commit()
    return conn

def save_item(kind, title, details="", content="", file_path=""):
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO history
            (created_at, kind, title, details, content, file_path)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(timespec="seconds"),
             kind, title, details, content, file_path)
        )
        return cur.lastrowid

def list_items(kind="All"):
    with connect() as conn:
        if kind == "All":
            rows = conn.execute(
                "SELECT * FROM history ORDER BY id DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM history WHERE kind=? ORDER BY id DESC",
                (kind,)
            ).fetchall()
        return [dict(row) for row in rows]

def get_item(item_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM history WHERE id=?", (item_id,)
        ).fetchone()
        return dict(row) if row else None

def save_file(name, data, prefix="file"):
    safe_name = Path(name).name.replace(" ", "_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = FILES / f"{prefix}_{stamp}_{safe_name}"
    path.write_bytes(data)
    return str(path)

def delete_item(item_id):
    item = get_item(item_id)
    with connect() as conn:
        conn.execute("DELETE FROM history WHERE id=?", (item_id,))
    if item and item["file_path"]:
        path = Path(item["file_path"]).resolve()
        if path.is_file() and FILES.resolve() in path.parents:
            path.unlink()
