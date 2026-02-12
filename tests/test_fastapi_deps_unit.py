from src.infrastructure.fastapi import deps


class _FakeGateway:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def test_get_read_cache_enabled_uses_is_prod(monkeypatch):
    monkeypatch.setattr(deps, "is_prod", lambda: True)
    assert deps._get_read_cache_enabled() is False

    monkeypatch.setattr(deps, "is_prod", lambda: False)
    assert deps._get_read_cache_enabled() is True


def test_get_token_gateway_factory(monkeypatch):
    class FakeTokenGateway:
        pass

    monkeypatch.setattr(deps, "HttpxTokenGateway", FakeTokenGateway)

    gateway = deps.get_token_gateway()

    assert isinstance(gateway, FakeTokenGateway)


def test_gateway_factories_forward_enable_get_cache(monkeypatch):
    monkeypatch.setattr(deps, "_get_read_cache_enabled", lambda: True)

    for factory_name, gateway_attr in [
        ("get_cliente_gateway", "XubioClienteGateway"),
        ("get_categoria_fiscal_gateway", "XubioCategoriaFiscalGateway"),
        ("get_remito_gateway", "XubioRemitoGateway"),
        ("get_producto_gateway", "XubioProductoGateway"),
        ("get_deposito_gateway", "XubioDepositoGateway"),
        ("get_identificacion_tributaria_gateway", "XubioIdentificacionTributariaGateway"),
        ("get_lista_precio_gateway", "XubioListaPrecioGateway"),
        ("get_moneda_gateway", "XubioMonedaGateway"),
        ("get_comprobante_venta_gateway", "XubioComprobanteVentaGateway"),
    ]:
        monkeypatch.setattr(deps, gateway_attr, _FakeGateway)
        gateway = getattr(deps, factory_name)()
        assert isinstance(gateway, _FakeGateway)
        assert gateway.kwargs["enable_get_cache"] is True


def test_producto_compra_factory_sets_config(monkeypatch):
    monkeypatch.setattr(deps, "_get_read_cache_enabled", lambda: False)
    monkeypatch.setattr(deps, "XubioProductoGateway", _FakeGateway)

    gateway = deps.get_producto_compra_gateway()

    assert isinstance(gateway, _FakeGateway)
    assert gateway.kwargs["enable_get_cache"] is False
    config = gateway.kwargs["config"]
    assert config.primary_bean == "ProductoCompraBean"
    assert config.fallback_bean is None
