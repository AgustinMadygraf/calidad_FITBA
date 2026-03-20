from typing import Optional

from src.use_cases.network_audit_models import AuditInsertResult
from src.use_cases.ports.network_audit_repository import NetworkAuditRepository
from src.use_cases.ports.network_snapshot_provider import NetworkSnapshotProvider


def record_network_audit(
    snapshot_provider: NetworkSnapshotProvider,
    repository: NetworkAuditRepository,
) -> AuditInsertResult:
    snapshot = snapshot_provider.collect_snapshot()
    return repository.save_snapshot(snapshot)


def get_last_network_audit_status(
    repository: NetworkAuditRepository,
) -> Optional[AuditInsertResult]:
    return repository.get_last_status()
