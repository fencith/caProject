import sqlite3
import json
import os
from datetime import datetime

DB_PATH = r"D:/001/eText/eparser.db"


def init_db(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parse_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            parse_time TEXT,
            summary_json TEXT,
            header_json TEXT,
            sections_json TEXT,
            tar_info TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_result(result: dict, tar_info: dict | None = None, db_path: str = DB_PATH):
    init_db(db_path)
    summary_json = json.dumps(result, ensure_ascii=False)
    header_json = json.dumps(result.get("header", {}), ensure_ascii=False)
    sections_json = json.dumps(result.get("sections", []), ensure_ascii=False)
    tar_str = json.dumps(tar_info or {}, ensure_ascii=False)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO parse_results (filename, parse_time, summary_json, header_json, sections_json, tar_info) VALUES (?, ?, ?, ?, ?, ?)",
        (
            result.get("filename"),
            result.get("parse_time"),
            summary_json,
            header_json,
            sections_json,
            tar_str,
        ),
    )
    conn.commit()
    conn.close()


def query_results(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, parse_time, summary_json, tar_info FROM parse_results ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return rows
