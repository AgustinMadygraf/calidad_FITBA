from __future__ import annotations

import sys
from dataclasses import dataclass, fields as dataclass_fields, is_dataclass
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


@dataclass(frozen=True)
class _FieldBuildContext:
    field_defs: Dict[str, tuple[Any, Any]]
    type_map: Dict[Type[Any], Type[Any]]
    optional_all: bool
    globalns: Dict[str, Any]


def model_from_entity(
    name: str,
    entity_cls: Type[Any],
    *,
    type_map: Optional[Dict[Type[Any], Type[Any]]] = None,
    optional_all: bool = True,
) -> Type[BaseModel]:
    module = sys.modules[entity_cls.__module__]
    field_defs: Dict[str, tuple[Any, Any]] = {}
    ctx = _FieldBuildContext(field_defs, type_map or {}, optional_all, module.__dict__)
    _build_field_defs(entity_cls, ctx)
    model = create_model(name, __base__=BaseModel, **ctx.field_defs)
    model.model_config = ConfigDict(extra="allow")
    return model


def _build_field_defs(entity_cls: Type[Any], ctx: _FieldBuildContext) -> None:
    hints = get_type_hints(entity_cls, globalns=ctx.globalns)
    if is_dataclass(entity_cls):
        _add_dataclass_fields(entity_cls, hints, ctx)
    else:
        _add_hint_fields(hints, ctx)


def _add_dataclass_fields(
    entity_cls: Type[Any],
    hints: Dict[str, Any],
    ctx: _FieldBuildContext,
) -> None:
    for field in dataclass_fields(entity_cls):
        field_name = field.name
        field_type = hints.get(field_name, field.type)
        if field.metadata.get("flatten"):
            _add_flattened_fields(field_type, ctx)
            continue
        _define_field(field_name, field_type, ctx)


def _add_hint_fields(hints: Dict[str, Any], ctx: _FieldBuildContext) -> None:
    for field_name, field_type in hints.items():
        _define_field(field_name, field_type, ctx)


def _define_field(
    field_name: str,
    field_type: Any,
    ctx: _FieldBuildContext,
    *,
    if_missing: bool = False,
) -> None:
    field_type = _replace_types(field_type, ctx.type_map)
    if ctx.optional_all:
        field_type = _optionalize(field_type)
    if if_missing:
        ctx.field_defs.setdefault(field_name, (field_type, None))
    else:
        ctx.field_defs[field_name] = (field_type, None)


def _optionalize(field_type: Any) -> Any:
    origin = get_origin(field_type)
    if origin is Union and type(None) in get_args(field_type):
        return field_type
    return Optional[field_type]


def _add_flattened_fields(
    field_type: Any,
    ctx: _FieldBuildContext,
) -> None:
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Union and args:
        field_type = next((arg for arg in args if arg is not NONE_TYPE), field_type)
    if not is_dataclass(field_type):
        return
    nested_hints = get_type_hints(field_type, globalns=ctx.globalns)
    for nested_name, nested_type in nested_hints.items():
        _define_field(
            nested_name,
            nested_type,
            ctx,
            if_missing=True,
        )


def _replace_types(field_type: Any, type_map: Dict[Type[Any], Type[Any]]) -> Any:
    if field_type in type_map:
        return type_map[field_type]
    origin = get_origin(field_type)
    if origin is None:
        result = type_map.get(field_type, field_type)
    else:
        args = tuple(_replace_types(arg, type_map) for arg in get_args(field_type))
        result = Union[args] if origin is Union else origin[args]  # type: ignore[index]
    return result
