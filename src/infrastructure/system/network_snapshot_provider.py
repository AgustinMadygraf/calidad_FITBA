from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from pathlib import Path

from src.use_cases.network_audit_models import NetworkSnapshot


class SystemNetworkSnapshotProvider:
    def collect_snapshot(self) -> NetworkSnapshot:
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        default_iface = self._run_default_iface()
        default_gw = self._run_default_gw()
        lan_cidr = self._run_lan_cidr(default_iface)
        lan_ip = lan_cidr.split("/", 1)[0] if lan_cidr else ""
        mac_addr = self._read_text(f"/sys/class/net/{default_iface}/address").strip()

        if not default_iface:
            default_iface = "unknown"
        if not default_gw:
            default_gw = "unknown"
        if not lan_cidr:
            lan_cidr = "unknown"
        if not lan_ip:
            lan_ip = "unknown"
        if not mac_addr:
            mac_addr = "unknown"

        return NetworkSnapshot(
            timestamp_utc=now_utc,
            hostname=hostname,
            fqdn=fqdn,
            default_iface=default_iface,
            default_gw=default_gw,
            lan_ip=lan_ip,
            lan_cidr=lan_cidr,
            mac_addr=mac_addr,
        )

    def _run_default_iface(self) -> str:
        output = os.popen("ip route show default 2>/dev/null").read().strip()
        if not output:
            return ""
        parts = output.split()
        if len(parts) < 5:
            return ""
        return parts[4]

    def _run_default_gw(self) -> str:
        output = os.popen("ip route show default 2>/dev/null").read().strip()
        if not output:
            return ""
        parts = output.split()
        if len(parts) < 3:
            return ""
        return parts[2]

    def _run_lan_cidr(self, iface: str) -> str:
        if not iface:
            return ""
        output = os.popen(
            f"ip -4 addr show dev {iface} 2>/dev/null | awk '/inet / {{print $2; exit}}'"
        ).read().strip()
        return output

    def _read_text(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except OSError:
            return ""
