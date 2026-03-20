from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NetworkSnapshot:
    timestamp_utc: str
    hostname: str
    fqdn: str
    default_iface: str
    default_gw: str
    lan_ip: str
    lan_cidr: str
    mac_addr: str


@dataclass(frozen=True)
class AuditInsertResult:
    db_path: str
    changed_ip: bool
    changed_iface: bool
    changed_gw: bool
    current: NetworkSnapshot
    previous: Optional[NetworkSnapshot]
