from typing import Protocol

from src.use_cases.network_audit_models import NetworkSnapshot


class NetworkSnapshotProvider(Protocol):  # pylint: disable=too-few-public-methods
    def collect_snapshot(self) -> NetworkSnapshot: ...
