from dataclasses import dataclass
import os
from pathlib import Path
import pymysql
from pymysql.connections import Connection


@dataclass(frozen=True)
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    db: str


class MySQLConnectionFactory:
    def __init__(self, config: MySQLConfig) -> None:
        self.config = config

    @classmethod
    def from_env(cls) -> "MySQLConnectionFactory":
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        db = os.getenv("DB_NAME", "contacts")
        return cls(MySQLConfig(host, port, user, password, db))

    def connect(self) -> Connection:
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.db,
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4",
        )

    def ensure_schema(self, schema_path: str | Path) -> None:
        path = Path(schema_path)
        sql = path.read_text(encoding="utf-8")
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
        finally:
            conn.close()

    def __enter__(self) -> Connection:
        self._conn = self.connect()
        return self._conn

    def __exit__(self, exc_type, exc, tb) -> None:
        if hasattr(self, "_conn"):
            self._conn.close()
