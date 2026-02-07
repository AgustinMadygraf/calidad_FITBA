from __future__ import annotations

def test_sync_push_marks_local_as_synced(client) -> None:
    create_resp = client.post(
        "/terminal/execute",
        json={
            "session_id": "test",
            "command": "CREATE product",
            "args": {"external_id": "p-10", "name": "Producto A"},
        },
    )
    assert create_resp.status_code == 200

    sync_resp = client.post("/sync/push/product")
    assert sync_resp.status_code == 200
    assert sync_resp.json()["status"] == "ok"

    from src.infrastructure.db.session import SessionLocal
    from src.infrastructure.repositories.integration_record_repository import (
        IntegrationRecordRepository,
    )

    db = SessionLocal()
    try:
        repo = IntegrationRecordRepository(db)
        record = repo.get_by_external_id("product", "p-10")
        assert record is not None
        assert record.status == "synced"
    finally:
        db.close()
