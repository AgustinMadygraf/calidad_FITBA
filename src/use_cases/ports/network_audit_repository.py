from typing import Optional, Protocol

from src.use_cases.network_audit_models import AuditInsertResult, NetworkSnapshot


class NetworkAuditRepository(Protocol):  # pylint: disable=too-few-public-methods
    def save_snapshot(self, snapshot: NetworkSnapshot) -> AuditInsertResult: ...

    def get_last_status(self) -> Optional[AuditInsertResult]: ...
