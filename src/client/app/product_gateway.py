from __future__ import annotations

from src.interface_adapter.controller.cli.product_gateway import (  # noqa: F401
    LocalFastApiProductGateway,
    ProductGateway,
    XubioDirectProductGateway,
    map_product_screen,
)

__all__ = [
    "LocalFastApiProductGateway",
    "ProductGateway",
    "XubioDirectProductGateway",
    "map_product_screen",
]
