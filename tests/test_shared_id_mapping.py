from src.shared.id_mapping import extract_int_id, first_non_none, match_any_id


def test_match_any_id_uses_keys():
    item = {"ID": 5, "id": 7, "clienteId": 9}
    assert match_any_id(item, 5, ("ID",)) is True
    assert match_any_id(item, 7, ("id",)) is True
    assert match_any_id(item, 9, ("clienteId",)) is True
    assert match_any_id(item, 10, ("ID", "id", "clienteId")) is False


def test_extract_int_id_returns_first_int():
    item = {"id": "7", "ID": 3, "clienteId": 4}
    assert extract_int_id(item, ("id", "ID", "clienteId")) == 3
    assert extract_int_id(item, ("clienteId", "ID")) == 4


def test_first_non_none():
    assert first_non_none(None, 0, 2) == 0
    assert first_non_none(None, None, "x") == "x"
    assert first_non_none(None, None) is None
