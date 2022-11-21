from urllib.parse import parse_qs
from typing import Any, Dict, List, Tuple, Type, Union

from pydantic.main import BaseModel, ModelField

from .filters import base as filters_base


__all__ = ['parse']


def parse(
    raw_qs: str,
    validation_model: Type[BaseModel],
    delimiter: str,
) -> Tuple[Dict[str, Any], Dict[str, Type[filters_base.Filter]]]:
    raw_result: Dict[str, Any] = {}
    operations: Dict[str, Type[filters_base.Filter]] = {}

    for raw_name, raw_value in parse_qs(raw_qs).items():
        if not raw_value:
            continue

        value = _parse_list_or_value(raw_value[0])

        if raw_name in validation_model.__fields__:
            raw_result[raw_name] = value
            operations[raw_name] = filters_base.Equal
            continue

        name, operation = raw_name.rsplit(delimiter, maxsplit=1)

        field = validation_model.__fields__.get(name)
        if not field:
            raise ValueError(f'Filter name cannot be handled: {raw_name}')

        raw_result[name] = value
        operations[name] = _get_operation(operation, field)

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


def _parse_list_or_value(value: str) -> Union[str, List[str]]:
    list_delimiter = ','
    if list_delimiter in value:
        return value.split(list_delimiter)

    return value
