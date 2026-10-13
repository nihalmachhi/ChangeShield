import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


class Store:
    def __init__(self, path="data/changeshield.sqlite3"):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, payload TEXT)"
            )

    def connect(self):
        return sqlite3.connect(self.path)

    def save(self, payload):
        identifier = str(uuid4())
        created = datetime.now(UTC).isoformat()
        with self.connect() as db:
            db.execute(
                "INSERT INTO analyses VALUES (?,?,?)", (identifier, created, json.dumps(payload))
            )
        return {"id": identifier, "created_at": created, **payload}

    def get(self, identifier):
        with self.connect() as db:
            row = db.execute(
                "SELECT created_at,payload FROM analyses WHERE id=?", (identifier,)
            ).fetchone()
        return {"id": identifier, "created_at": row[0], **json.loads(row[1])} if row else None

    def list(self):
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,created_at,payload FROM analyses ORDER BY created_at DESC"
            ).fetchall()
        return [{"id": r[0], "created_at": r[1], **json.loads(r[2])} for r in rows]
