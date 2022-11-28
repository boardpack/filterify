from urllib.parse import parse_qs
from typing import Any, Dict, Tuple, Type

from pydantic.main import BaseModel, ModelField

from .protocols import ParserProtocol, FilterProtocol
from .filters import base as filters_base
from .exceptions import UnknownFieldError


__all__ = ['DefaultParser']


class DefaultParser(ParserProtocol):
    def __init__(self, validation_model: Type[BaseModel], delimiter: str, ignore_unknown_name: bool = True):
        self.validation_model = validation_model
        self.delimiter = delimiter
        self.ignore_unknown_name = ignore_unknown_name

    def parse(self, raw_qs: str) -> Tuple[Dict[Tuple[str, str], Any], Dict[Tuple[str, str], Type[FilterProtocol]]]:
        raw_result: Dict[Tuple[str, str], Any] = {}
        operations: Dict[Tuple[str, str], Type[FilterProtocol]] = {}

        for raw_name, raw_value in parse_qs(raw_qs).items():
            if not raw_value:
                continue

            value = raw_value[0]

            if raw_name in self.validation_model.__fields__:
                operation = filters_base.EqualFilter.operation()
                raw_result[(raw_name, operation)] = value
                operations[(raw_name, operation)] = filters_base.EqualFilter
                continue

            if self.delimiter not in raw_name:
                if self.ignore_unknown_name:
                    continue

                raise UnknownFieldError(raw_name)

            name, operation = raw_name.rsplit(self.delimiter, maxsplit=1)

            field = self.validation_model.__fields__.get(name)
            if not field:
                if self.ignore_unknown_name:
                    continue

                raise UnknownFieldError(raw_name)

            raw_result[(name, operation)] = value
            operations[(name, operation)] = self._get_filter(operation, field)

        return raw_result, operations

    @staticmethod
    def _get_filter(operation: str, field: ModelField) -> Type[FilterProtocol]:
        field_type = field.outer_type_
        if field.is_complex():
            field_type = field.outer_type_.__origin__
        if field_type not in filters_base.FILTER_MAPPING:
            raise ValueError(f'Unsupported field type: {field_type}')

        for filter_item in filters_base.FILTER_MAPPING[field_type]:
            if filter_item.operation() == operation:
                return filter_item
        else:
            raise ValueError(f'Unsupported operation for the {field_type}: {operation}')
