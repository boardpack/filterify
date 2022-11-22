from urllib.parse import parse_qs
from typing import Any, Dict, Tuple, Type

from pydantic.main import BaseModel, ModelField

from .filters import base as filters_base
from .exceptions import UnknownFieldError


__all__ = ['parse']


def parse(
    raw_qs: str,
    validation_model: Type[BaseModel],
    delimiter: str,
    ignore_unknown_name: bool = True,
) -> Tuple[Dict[Tuple[str, str], Any], Dict[Tuple[str, str], Type[filters_base.Filter]]]:
    raw_result: Dict[Tuple[str, str], Any] = {}
    operations: Dict[Tuple[str, str], Type[filters_base.Filter]] = {}

    for raw_name, raw_value in parse_qs(raw_qs).items():
        if not raw_value:
            continue

        value = raw_value[0]

        if raw_name in validation_model.__fields__:
            operation = filters_base.Equal.operation()
            raw_result[(raw_name, operation)] = value
            operations[(raw_name, operation)] = filters_base.Equal
            continue

        if delimiter not in raw_name:
            if ignore_unknown_name:
                continue

            raise UnknownFieldError(raw_name)

        name, operation = raw_name.rsplit(delimiter, maxsplit=1)

        field = validation_model.__fields__.get(name)
        if not field:
            if ignore_unknown_name:
                continue

            raise UnknownFieldError(raw_name)

        raw_result[(name, operation)] = value
        operations[(name, operation)] = _get_operation(operation, field)

    return raw_result, operations


def _get_operation(operation: str, field: ModelField) -> Type[filters_base.Filter]:
    field_type = field.outer_type_
    if field.is_complex():
        field_type = field.outer_type_.__origin__
    if field_type not in filters_base.FILTER_MAPPING:
        raise ValueError(f'Unsupported filter type: {field_type}')

    for filter_item in filters_base.FILTER_MAPPING[field_type]:
        if filter_item.operation() == operation:
            return filter_item
    else:
        raise ValueError(f'Unsupported operation for the {field_type}: {operation}')
