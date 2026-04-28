import sqlite3
import time
from pathlib import Path


class EventDatabase:
    def __init__(self, db_path: str | Path = "events.db") -> None:
        self.db_path = str(db_path)
        self.initDb()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        return conn

    def initDb(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )

    def log(self, message: str, timestamp: int | None = None) -> None:
        timestamp = timestamp or int(time.time())

        with self.connect() as conn:
            conn.execute(
                "INSERT INTO events (timestamp, message) VALUES (?, ?)",
                (timestamp, message),
            )

    def fetch_all(self) -> list[tuple[int, float, str]]:
        with self.connect() as conn:
            cur = conn.execute(
                "SELECT id, timestamp, message FROM events ORDER BY id DESC",
            )
            return cur.fetchall()

    def clear(self) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM events")


eventDb = EventDatabase()
