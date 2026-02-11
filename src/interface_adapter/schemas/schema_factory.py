from __future__ import annotations

import sys
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import (
    Any,
    Dict,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel, ConfigDict, create_model

NONE_TYPE = type(None)


def model_from_entity(
    name: str,
    entity_cls: Type[Any],
    *,
    type_map: Optional[Dict[Type[Any], Type[Any]]] = None,
    optional_all: bool = True,
) -> Type[BaseModel]:
    module = sys.modules[entity_cls.__module__]
    type_map = type_map or {}
    hints = get_type_hints(entity_cls, globalns=module.__dict__)
    field_defs: Dict[str, tuple[Any, Any]] = {}
    if is_dataclass(entity_cls):
        for field in dataclass_fields(entity_cls):
            field_name = field.name
            field_type = hints.get(field_name, field.type)
            if field.metadata.get("flatten"):
                _add_flattened_fields(
                    field_type, field_defs, type_map, optional_all, module.__dict__
                )
                continue
            field_type = _replace_types(field_type, type_map)
            if optional_all:
                field_type = _optionalize(field_type)
            field_defs[field_name] = (field_type, None)
    else:
        for field_name, field_type in hints.items():
            field_type = _replace_types(field_type, type_map)
            if optional_all:
                field_type = _optionalize(field_type)
            field_defs[field_name] = (field_type, None)
    model = create_model(name, __base__=BaseModel, **field_defs)
    model.model_config = ConfigDict(extra="allow")
    return model


def _optionalize(field_type: Any) -> Any:
    origin = get_origin(field_type)
    if origin is Union and type(None) in get_args(field_type):
        return field_type
    return Optional[field_type]


def _add_flattened_fields(
    field_type: Any,
    field_defs: Dict[str, tuple[Any, Any]],
    type_map: Dict[Type[Any], Type[Any]],
    optional_all: bool,
    globalns: Dict[str, Any],
) -> None:
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Union and args:
        field_type = next((arg for arg in args if arg is not NONE_TYPE), field_type)
    if not is_dataclass(field_type):
        return
    nested_hints = get_type_hints(field_type, globalns=globalns)
    for nested_name, nested_type in nested_hints.items():
        nested_type = _replace_types(nested_type, type_map)
        if optional_all:
            nested_type = _optionalize(nested_type)
        field_defs.setdefault(nested_name, (nested_type, None))


def _replace_types(field_type: Any, type_map: Dict[Type[Any], Type[Any]]) -> Any:
    if field_type in type_map:
        return type_map[field_type]
    origin = get_origin(field_type)
    if origin is None:
        return type_map.get(field_type, field_type)
    args = tuple(_replace_types(arg, type_map) for arg in get_args(field_type))
    if origin is Union:
        return Union[args]  # type: ignore[index]
    return origin[args]  # type: ignore[index]
