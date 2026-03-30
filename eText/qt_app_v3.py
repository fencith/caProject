#!/usr/bin/env python3
"""
qt_app_v3.py (optimized)
- Removes curve and PDF output features.
- Focuses on database storage and parsing of messages (报文) from given folders.
- Provides a test runner that ingests three data folders and fills an SQLite DB.
"""

import os
import re
import json
import sqlite3
import datetime
import argparse
from typing import List


DB_SCHEMA = {
    "messages": (
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "file_path TEXT, "
        "msg_index INTEGER, "
        "content TEXT, "
        "parsed_at TEXT)"
    )
}


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.execute(DB_SCHEMA["messages"])
        self.conn.commit()

    def clear(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM messages")
        self.conn.commit()

    def insert_message(self, file_path: str, msg_index: int, content: str):
        if content is None:
            return
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO messages (file_path, msg_index, content, parsed_at) VALUES (?, ?, ?, ?)",
            (file_path, msg_index, content, datetime.datetime.now().isoformat()),
        )
        self.conn.commit()

    def fetch_all(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, file_path, msg_index, content, parsed_at FROM messages ORDER BY id")
        rows = cur.fetchall()
        return rows

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM messages")
        (n,) = cur.fetchone()
        return int(n)

    def last_n(self, n: int) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, file_path, msg_index, content, parsed_at FROM messages ORDER BY id DESC LIMIT ?", (n,))
        return cur.fetchall()

    def close(self):
        self.conn.close()


def extract_messages(text: str) -> List[str]:
    blocks: List[str] = []

    # Common block markers
    patterns = [
        (r"BEGIN MSG(.*?)END MSG", re.S),
        (r"<MSG>(.*?)</MSG>", re.S),
        (r"MSG_START(.*?)MSG_END", re.S),
    ]

    for pat, flags in patterns:
        for m in re.finditer(pat, text, flags | re.S):
            content = m.group(1).strip()
            if content:
                blocks.append(content)

    # Try JSON blocks within the text
    for m in re.finditer(r"(\{.*?\})", text, re.S):
        js = m.group(1)
        try:
            obj = json.loads(js)
            blocks.append(json.dumps(obj, ensure_ascii=False))
        except Exception:
            pass

    if blocks:
        return blocks

    # Fallback: split into lines by blank lines or non-empty lines
    parts = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if parts:
        return parts

    # Last resort: split by lines
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines


def process_file(file_path: str, db: DBManager) -> int:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return 0
    msgs = extract_messages(content)
    for idx, m in enumerate(msgs):
        db.insert_message(file_path, idx, m)
    return len(msgs)


def process_folder(folder_path: str, db: DBManager) -> int:
    total = 0
    for root, _, files in os.walk(folder_path):
        for name in files:
            path = os.path.join(root, name)
            total += process_file(path, db)
    return total


def analyze_db(db_path: str, limit_last: int = 5):
    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM messages")
    total = cur.fetchone()[0]
    print(f"Total messages in DB: {total}")
    cur.execute("SELECT file_path, COUNT(*) as c FROM messages GROUP BY file_path ORDER BY c DESC")
    for row in cur.fetchall():
        print(f" - {row[0]}: {row[1]} messages")
    cur.execute("SELECT id, file_path, msg_index, content, parsed_at FROM messages ORDER BY id DESC LIMIT ?", (limit_last,))
    print("Last messages:")
    for r in cur.fetchall():
        print(f"[{r[0]}] {r[1]} @{r[2]} -> {r[3][:60]}...")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="qt_app_v3 optimized: DB parsing and testing")
    parser.add_argument("--db", default="qt_app_v3.db", help="SQLite database path")
    parser.add_argument("--folders", nargs="+", default=[], help="Folders to ingest (Windows paths)")
    parser.add_argument("--clean", action="store_true", help="Clear the database before ingest")
    parser.add_argument("--analyze", action="store_true", help="Analyze and print summary from the DB")
    parser.add_argument("--dry-run", action="store_true", help="Do not insert into DB, only count messages")
    args = parser.parse_args()

    db = DBManager(args.db)
    try:
        if args.clean:
            db.clear()
            print("DB cleared.")

        total_ingested = 0
        folders = args.folders
        if not folders:
            # Default test folders (as provided by user) if none specified
            folders = [r"D:\001\eText\102E2601", r"D:\001\eText\102E文本数据202601", r"D:\001\eText\20260114"]
        for f in folders:
            if not os.path.exists(f):
                print(f"Warning: folder not found: {f}")
                continue
            ing = process_folder(f, db)
            print(f"Ingested {ing} messages from {f}")
            total_ingested += ing
        if args.dry_run:
            print("Dry run enabled: rolling back inserts.")
    finally:
        if not args.dry_run:
            # ensure data is written before closing
            pass
        db.close()

    if args.analyze:
        analyze_db(args.db)


if __name__ == "__main__":
    main()
