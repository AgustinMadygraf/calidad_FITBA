import httpx
import pytest

from src.infrastructure.httpx import xubio_crud_helpers as crud
from src.use_cases.errors import ExternalServiceError


class DummyLogger:
    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None


def _http_error() -> httpx.HTTPError:
    request = httpx.Request("GET", "https://xubio.local")
    return httpx.ConnectError("boom", request=request)


def test_list_items_success(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(200, json=[{"id": 1}]),
    )
    items = crud.list_items(
        url="https://xubio.local/items",
        timeout=1.0,
        label="items",
        logger=DummyLogger(),
    )
    assert items == [{"id": 1}]


def test_list_items_wraps_http_error(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(_http_error()),
    )
    with pytest.raises(ExternalServiceError):
        crud.list_items(
            url="https://xubio.local/items",
            timeout=1.0,
            label="items",
            logger=DummyLogger(),
        )


def test_get_item_variants(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(404, json={}),
    )
    assert crud.get_item(url="https://x/item/1", timeout=1.0, logger=DummyLogger()) is None

    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(200, json={"id": 1}),
    )
    assert crud.get_item(url="https://x/item/1", timeout=1.0, logger=DummyLogger()) == {
        "id": 1
    }


def test_get_item_wraps_http_error(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(_http_error()),
    )
    with pytest.raises(ExternalServiceError):
        crud.get_item(url="https://x/item/1", timeout=1.0, logger=DummyLogger())


def test_get_item_with_fallback_variants(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(404, json={}),
    )
    assert (
        crud.get_item_with_fallback(
            url="https://x/item/1",
            timeout=1.0,
            logger=DummyLogger(),
            fallback=lambda: {"id": 99},
        )
        is None
    )

    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(500, json={}),
    )
    assert crud.get_item_with_fallback(
        url="https://x/item/1",
        timeout=1.0,
        logger=DummyLogger(),
        fallback=lambda: {"id": 2},
    ) == {"id": 2}

    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(200, json={"id": 3}),
    )
    assert crud.get_item_with_fallback(
        url="https://x/item/1",
        timeout=1.0,
        logger=DummyLogger(),
        fallback=lambda: None,
    ) == {"id": 3}


def test_get_item_with_fallback_wraps_http_error(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(_http_error()),
    )
    with pytest.raises(ExternalServiceError):
        crud.get_item_with_fallback(
            url="https://x/item/1",
            timeout=1.0,
            logger=DummyLogger(),
            fallback=lambda: None,
        )


def test_create_update_patch_delete_variants(monkeypatch):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda method, *_args, **_kwargs: httpx.Response(
            200, json={"method": method.lower()}
        ),
    )
    assert crud.create_item(
        url="https://x/items",
        timeout=1.0,
        data={"name": "n"},
        logger=DummyLogger(),
    ) == {"method": "post"}
    assert crud.update_item(
        url="https://x/items/1",
        timeout=1.0,
        data={"name": "u"},
        logger=DummyLogger(),
    ) == {"method": "put"}
    assert crud.patch_item(
        url="https://x/items/1",
        timeout=1.0,
        data={"name": "p"},
        logger=DummyLogger(),
    ) == {"method": "patch"}
    assert (
        crud.delete_item(url="https://x/items/1", timeout=1.0, logger=DummyLogger())
        is True
    )

    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(404, json={}),
    )
    assert (
        crud.update_item(
            url="https://x/items/1",
            timeout=1.0,
            data={},
            logger=DummyLogger(),
        )
        is None
    )
    assert (
        crud.patch_item(
            url="https://x/items/1",
            timeout=1.0,
            data={},
            logger=DummyLogger(),
        )
        is None
    )
    assert (
        crud.delete_item(url="https://x/items/1", timeout=1.0, logger=DummyLogger())
        is False
    )


@pytest.mark.parametrize(
    "fn_name, kwargs",
    [
        (
            "create_item",
            {"url": "https://x/items", "timeout": 1.0, "data": {}, "logger": DummyLogger()},
        ),
        (
            "update_item",
            {
                "url": "https://x/items/1",
                "timeout": 1.0,
                "data": {},
                "logger": DummyLogger(),
            },
        ),
        (
            "patch_item",
            {
                "url": "https://x/items/1",
                "timeout": 1.0,
                "data": {},
                "logger": DummyLogger(),
            },
        ),
        ("delete_item", {"url": "https://x/items/1", "timeout": 1.0, "logger": DummyLogger()}),
    ],
)
def test_mutation_helpers_wrap_http_error(monkeypatch, fn_name, kwargs):
    monkeypatch.setattr(
        crud,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(_http_error()),
    )
    fn = getattr(crud, fn_name)
    with pytest.raises(ExternalServiceError):
        fn(**kwargs)

