"""
Path: src/infrastructure/memory/identificacion_tributaria_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.identificacion_tributaria_gateway import (
    IdentificacionTributariaGateway,
)


_DEFAULT_IDENTIFICACIONES_TRIBUTARIAS: List[Dict[str, Any]] = [
    {"codigo": "ACTA_NACIMIENTO", "nombre": "Acta nacimiento", "id": 41, "ID": 41},
    {"codigo": "CDI", "nombre": "CDI", "id": 36, "ID": 36},
    {
        "codigo": "CERTIFICADO_DE_MIGRACION",
        "nombre": "Certificado de Migracion",
        "id": 45,
        "ID": 45,
    },
    {"codigo": "CI_BS_AS_RNP", "nombre": "CI Bs. As. RNP", "id": 43, "ID": 43},
    {"codigo": "CI_BUENOS_AIRES", "nombre": "CI Buenos Aires", "id": 12, "ID": 12},
    {"codigo": "CI_CATAMARCA", "nombre": "CI Catamarca", "id": 13, "ID": 13},
    {"codigo": "CI_CHACO", "nombre": "CI Chaco", "id": 26, "ID": 26},
    {"codigo": "CI_CHUBUT", "nombre": "CI Chubut", "id": 27, "ID": 27},
    {"codigo": "CI_CORDOBA", "nombre": "CI Cordoba", "id": 14, "ID": 14},
    {"codigo": "CI_CORRIENTES", "nombre": "CI Corrientes", "id": 15, "ID": 15},
    {"codigo": "CI_ENTRE_RIOS", "nombre": "CI Entre Rios", "id": 16, "ID": 16},
    {"codigo": "CI_EXTRANJERA", "nombre": "CI Extranjera", "id": 39, "ID": 39},
    {"codigo": "CI_FORMOSA", "nombre": "CI Formosa", "id": 28, "ID": 28},
    {"codigo": "CI_JUJUY", "nombre": "CI Jujuy", "id": 17, "ID": 17},
    {"codigo": "CI_LA_PAMPA", "nombre": "CI La Pampa", "id": 31, "ID": 31},
    {"codigo": "CI_LA_RIOJA", "nombre": "CI La Rioja", "id": 19, "ID": 19},
    {"codigo": "CI_MENDOZA", "nombre": "CI Mendoza", "id": 18, "ID": 18},
    {"codigo": "CI_MISIONES", "nombre": "CI Misiones", "id": 29, "ID": 29},
    {"codigo": "CI_NEUQUEN", "nombre": "CI Neuquen", "id": 30, "ID": 30},
    {
        "codigo": "CI_POLICIA_FEDERAL",
        "nombre": "CI Policia Federal",
        "id": 11,
        "ID": 11,
    },
    {"codigo": "CI_RIO_NEGRO", "nombre": "CI Rio Negro", "id": 32, "ID": 32},
    {"codigo": "CI_SALTA", "nombre": "CI Salta", "id": 20, "ID": 20},
    {"codigo": "CI_SAN_JUAN", "nombre": "CI San Juan", "id": 21, "ID": 21},
    {"codigo": "CI_SAN_LUIS", "nombre": "CI San Luis", "id": 22, "ID": 22},
    {"codigo": "CI_SANTA_CRUZ", "nombre": "CI Santa Cruz", "id": 33, "ID": 33},
    {"codigo": "CI_SANTA_FE", "nombre": "CI Santa Fe", "id": 23, "ID": 23},
    {
        "codigo": "CI_SANTIAGO_DEL_ESTERO",
        "nombre": "CI Santiago del Estero",
        "id": 24,
        "ID": 24,
    },
    {
        "codigo": "CI_TIERRA_DEL_FUEGO",
        "nombre": "CI Tierra del Fuego",
        "id": 34,
        "ID": 34,
    },
    {"codigo": "CI_TUCUMAN", "nombre": "CI Tucuman", "id": 25, "ID": 25},
    {"codigo": "CUIL", "nombre": "CUIL", "id": 35, "ID": 35},
    {"codigo": "CUIT", "nombre": "CUIT", "id": 9, "ID": 9},
    {"codigo": "DNI", "nombre": "DNI", "id": 10, "ID": 10},
    {"codigo": "EN_TRAMITE", "nombre": "En tramite", "id": 40, "ID": 40},
    {"codigo": "LC", "nombre": "LC", "id": 38, "ID": 38},
    {"codigo": "LE", "nombre": "LE", "id": 37, "ID": 37},
    {"codigo": "PASAPORTE", "nombre": "Pasaporte", "id": 42, "ID": 42},
    {
        "codigo": "SIN_IDENTIFICARVENTA_GLOBAL_DIARIA",
        "nombre": "Sin identificar/venta global diaria",
        "id": 44,
        "ID": 44,
    },
    {
        "codigo": "USADO_POR_ANSES_PARA_PADRON",
        "nombre": "Usado por Anses para Padron",
        "id": 46,
        "ID": 46,
    },
]


class InMemoryIdentificacionTributariaGateway(IdentificacionTributariaGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_IDENTIFICACIONES_TRIBUTARIAS
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, identificacion_tributaria_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if item.get("ID") == identificacion_tributaria_id:
                return dict(item)
            if item.get("id") == identificacion_tributaria_id:
                return dict(item)
        return None
