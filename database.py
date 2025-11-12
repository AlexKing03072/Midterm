# database.py
import sqlite3
from typing import List, Dict, Tuple

DB_FILENAME = "books.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS llm_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    author TEXT,
    price INTEGER,
    link TEXT
);
"""


def init_db(db_path: str = DB_FILENAME) -> None:
    """
    初始化資料庫，建立 books 資料表（若不存在）。
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()
    except sqlite3.Error as e:
        print(f"資料庫初始化失敗: {e}")


def insert_books(books: List[Dict], db_path: str = DB_FILENAME) -> int:
    """
    將多筆書籍資料寫入資料庫。

    Args:
        books (List[Dict]): 書籍資料列表。
        db_path (str): SQLite 資料庫路徑。

    Returns:
        int: 新增的筆數。
    """
    inserted = 0
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            for b in books:
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO llm_books (title, author, price, link) VALUES (?, ?, ?, ?)",
                        (b.get("title", "N/A"), b.get("author", "N/A"),
                        int(b.get("price", 0) or 0), b.get("link", ""))
                    )
                    if cur.rowcount == 1:
                        inserted += 1
                except Exception:
                    continue
            conn.commit()
    except sqlite3.Error as e:
        print(f"寫入資料庫失敗: {e}")
    return inserted


def _query(sql: str, params: Tuple = (), db_path: str = DB_FILENAME) -> List[Dict]:
    """
    執行查詢，回傳 dict list。
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as e:
        print(f"查詢資料庫失敗: {e}")
        return []


def query_by_title(keyword: str, db_path: str = DB_FILENAME) -> List[Dict]:
    kw = f"%{keyword}%"
    return _query("SELECT * FROM llm_books WHERE title LIKE ? ORDER BY id", (kw,), db_path)


def query_by_author(keyword: str, db_path: str = DB_FILENAME) -> List[Dict]:
    kw = f"%{keyword}%"
    return _query("SELECT * FROM llm_books WHERE author LIKE ? ORDER BY id", (kw,), db_path)
