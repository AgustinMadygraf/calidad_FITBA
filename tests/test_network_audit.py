from src.infrastructure.sqlite3.network_audit_repository import SqliteNetworkAuditRepository
from src.use_cases.network_audit import record_network_audit
from src.use_cases.network_audit_models import NetworkSnapshot


def _snap(ts: str, ip: str, iface: str = "enp4s0", gw: str = "10.0.0.1"):
    return NetworkSnapshot(
        timestamp_utc=ts,
        hostname="host1",
        fqdn="host1.local",
        default_iface=iface,
        default_gw=gw,
        lan_ip=ip,
        lan_cidr=f"{ip}/24",
        mac_addr="aa:bb:cc:dd:ee:ff",
    )


def test_record_snapshot_creates_db_and_detects_no_change(monkeypatch, tmp_path):
    db_path = tmp_path / "network_audit.sqlite3"
    class _Provider:
        def collect_snapshot(self):
            return _snap("2026-02-24T10:00:00Z", "10.176.61.33")

    result = record_network_audit(_Provider(), SqliteNetworkAuditRepository(str(db_path)))

    assert result.changed_ip is False
    assert result.changed_iface is False
    assert result.changed_gw is False
    assert result.previous is None
    assert result.current.lan_ip == "10.176.61.33"
    assert db_path.exists()


def test_record_snapshot_detects_ip_change(monkeypatch, tmp_path):
    db_path = tmp_path / "network_audit.sqlite3"
    class _Provider1:
        def collect_snapshot(self):
            return _snap("2026-02-24T10:00:00Z", "10.176.61.33")

    record_network_audit(_Provider1(), SqliteNetworkAuditRepository(str(db_path)))

    class _Provider2:
        def collect_snapshot(self):
            return _snap("2026-02-24T11:00:00Z", "10.176.61.44")

    result = record_network_audit(_Provider2(), SqliteNetworkAuditRepository(str(db_path)))

    assert result.changed_ip is True
    assert result.changed_iface is False
    assert result.changed_gw is False
    assert result.previous is not None
    assert result.previous.lan_ip == "10.176.61.33"
    assert result.current.lan_ip == "10.176.61.44"
