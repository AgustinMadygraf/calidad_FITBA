from typing import Optional

from .deps import (
    get_categoria_fiscal_gateway,
    get_cliente_gateway,
    get_comprobante_venta_gateway,
    get_deposito_gateway,
    get_identificacion_tributaria_gateway,
    get_lista_precio_gateway,
    get_moneda_gateway,
    get_producto_compra_gateway,
    get_producto_gateway,
    get_remito_gateway,
    get_vendedor_gateway,
)


class GatewayProvider:
    def __init__(self) -> None:
        self._cliente_gateway: Optional[object] = None
        self._categoria_fiscal_gateway: Optional[object] = None
        self._remito_gateway: Optional[object] = None
        self._producto_gateway: Optional[object] = None
        self._producto_compra_gateway: Optional[object] = None
        self._deposito_gateway: Optional[object] = None
        self._identificacion_tributaria_gateway: Optional[object] = None
        self._lista_precio_gateway: Optional[object] = None
        self._moneda_gateway: Optional[object] = None
        self._vendedor_gateway: Optional[object] = None
        self._comprobante_venta_gateway: Optional[object] = None

    def reset(self) -> None:
        self._cliente_gateway = None
        self._categoria_fiscal_gateway = None
        self._remito_gateway = None
        self._producto_gateway = None
        self._producto_compra_gateway = None
        self._deposito_gateway = None
        self._identificacion_tributaria_gateway = None
        self._lista_precio_gateway = None
        self._moneda_gateway = None
        self._vendedor_gateway = None
        self._comprobante_venta_gateway = None

    def _get_or_build(self, attr_name: str, factory) -> object:
        value = getattr(self, attr_name)
        if value is None:
            value = factory()
            setattr(self, attr_name, value)
        return value

    @property
    def cliente_gateway(self) -> object:
        return self._get_or_build("_cliente_gateway", get_cliente_gateway)

    @cliente_gateway.setter
    def cliente_gateway(self, value: object) -> None:
        self._cliente_gateway = value

    @property
    def categoria_fiscal_gateway(self) -> object:
        return self._get_or_build(
            "_categoria_fiscal_gateway", get_categoria_fiscal_gateway
        )

    @categoria_fiscal_gateway.setter
    def categoria_fiscal_gateway(self, value: object) -> None:
        self._categoria_fiscal_gateway = value

    @property
    def remito_gateway(self) -> object:
        return self._get_or_build("_remito_gateway", get_remito_gateway)

    @remito_gateway.setter
    def remito_gateway(self, value: object) -> None:
        self._remito_gateway = value

    @property
    def producto_gateway(self) -> object:
        return self._get_or_build("_producto_gateway", get_producto_gateway)

    @producto_gateway.setter
    def producto_gateway(self, value: object) -> None:
        self._producto_gateway = value

    @property
    def producto_compra_gateway(self) -> object:
        return self._get_or_build(
            "_producto_compra_gateway", get_producto_compra_gateway
        )

    @producto_compra_gateway.setter
    def producto_compra_gateway(self, value: object) -> None:
        self._producto_compra_gateway = value

    @property
    def deposito_gateway(self) -> object:
        return self._get_or_build("_deposito_gateway", get_deposito_gateway)

    @deposito_gateway.setter
    def deposito_gateway(self, value: object) -> None:
        self._deposito_gateway = value

    @property
    def identificacion_tributaria_gateway(self) -> object:
        return self._get_or_build(
            "_identificacion_tributaria_gateway",
            get_identificacion_tributaria_gateway,
        )

    @identificacion_tributaria_gateway.setter
    def identificacion_tributaria_gateway(self, value: object) -> None:
        self._identificacion_tributaria_gateway = value

    @property
    def lista_precio_gateway(self) -> object:
        return self._get_or_build("_lista_precio_gateway", get_lista_precio_gateway)

    @lista_precio_gateway.setter
    def lista_precio_gateway(self, value: object) -> None:
        self._lista_precio_gateway = value

    @property
    def moneda_gateway(self) -> object:
        return self._get_or_build("_moneda_gateway", get_moneda_gateway)

    @moneda_gateway.setter
    def moneda_gateway(self, value: object) -> None:
        self._moneda_gateway = value

    @property
    def vendedor_gateway(self) -> object:
        return self._get_or_build("_vendedor_gateway", get_vendedor_gateway)

    @vendedor_gateway.setter
    def vendedor_gateway(self, value: object) -> None:
        self._vendedor_gateway = value

    @property
    def comprobante_venta_gateway(self) -> object:
        return self._get_or_build(
            "_comprobante_venta_gateway", get_comprobante_venta_gateway
        )

    @comprobante_venta_gateway.setter
    def comprobante_venta_gateway(self, value: object) -> None:
        self._comprobante_venta_gateway = value


gateway_provider = GatewayProvider()
