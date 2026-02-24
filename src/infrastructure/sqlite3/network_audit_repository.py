from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from src.use_cases.network_audit_models import AuditInsertResult, NetworkSnapshot


class SqliteNetworkAuditRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def save_snapshot(self, snapshot: NetworkSnapshot) -> AuditInsertResult:
        self._ensure_parent_dir()
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_schema(conn)
            previous = self._fetch_last(conn)
            conn.execute(
                """
                INSERT INTO network_audit_records (
                    timestamp_utc, hostname, fqdn, default_iface, default_gw, lan_ip, lan_cidr, mac_addr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.timestamp_utc,
                    snapshot.hostname,
                    snapshot.fqdn,
                    snapshot.default_iface,
                    snapshot.default_gw,
                    snapshot.lan_ip,
                    snapshot.lan_cidr,
                    snapshot.mac_addr,
                ),
            )
            conn.commit()
        return AuditInsertResult(
            db_path=self.db_path,
            changed_ip=bool(previous and previous.lan_ip != snapshot.lan_ip),
            changed_iface=bool(previous and previous.default_iface != snapshot.default_iface),
            changed_gw=bool(previous and previous.default_gw != snapshot.default_gw),
            current=snapshot,
            previous=previous,
        )

    def get_last_status(self) -> Optional[AuditInsertResult]:
        if not Path(self.db_path).exists():
            return None
        with sqlite3.connect(self.db_path) as conn:
            self._ensure_schema(conn)
            current = self._fetch_last(conn)
            if current is None:
                return None
            previous = self._fetch_previous(conn)
        return AuditInsertResult(
            db_path=self.db_path,
            changed_ip=bool(previous and previous.lan_ip != current.lan_ip),
            changed_iface=bool(previous and previous.default_iface != current.default_iface),
            changed_gw=bool(previous and previous.default_gw != current.default_gw),
            current=current,
            previous=previous,
        )

    def _ensure_parent_dir(self) -> None:
        parent = Path(self.db_path).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS network_audit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                hostname TEXT NOT NULL,
                fqdn TEXT NOT NULL,
                default_iface TEXT NOT NULL,
                default_gw TEXT NOT NULL,
                lan_ip TEXT NOT NULL,
                lan_cidr TEXT NOT NULL,
                mac_addr TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_network_audit_timestamp
            ON network_audit_records(timestamp_utc)
            """
        )

    def _fetch_last(self, conn: sqlite3.Connection) -> Optional[NetworkSnapshot]:
        row = conn.execute(
            """
            SELECT timestamp_utc, hostname, fqdn, default_iface, default_gw, lan_ip, lan_cidr, mac_addr
            FROM network_audit_records
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        return NetworkSnapshot(*row)

    def _fetch_previous(self, conn: sqlite3.Connection) -> Optional[NetworkSnapshot]:
        row = conn.execute(
            """
            SELECT timestamp_utc, hostname, fqdn, default_iface, default_gw, lan_ip, lan_cidr, mac_addr
            FROM network_audit_records
            ORDER BY id DESC
            LIMIT 1 OFFSET 1
            """
        ).fetchone()
        if row is None:
            return None
        return NetworkSnapshot(*row)
