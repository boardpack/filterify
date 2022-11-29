from typing import Any, Dict, Tuple, Type
from urllib.parse import parse_qs

from pydantic.fields import ModelField

from .base import Filter, Parser
from .exceptions import UnknownFieldError, UnknownOperationError, UnknownTypeError
from .filters import base as filters_base

__all__ = ["DefaultParser"]


class DefaultParser(Parser):
    def parse(
        self, raw_qs: str
    ) -> Tuple[Dict[Tuple[str, str], Any], Dict[Tuple[str, str], Type[Filter]]]:
        raw_result: Dict[Tuple[str, str], Any] = {}
        operations: Dict[Tuple[str, str], Type[Filter]] = {}

        for raw_name, raw_value in parse_qs(raw_qs).items():
            if not raw_value:
                continue

            name, operation = raw_name, filters_base.EqualFilter.operation()
            if name not in self.validation_model.__fields__:
                if self.delimiter in name:
                    name, operation = name.rsplit(self.delimiter, maxsplit=1)

                if name not in self.validation_model.__fields__:
                    if self.ignore_unknown_name:
                        continue

                    raise UnknownFieldError(raw_name)

            value = raw_value[0]
            field = self.validation_model.__fields__[name]
            field_type = self._get_field_type(field)

            raw_result[(name, operation)] = value
            operations[(name, operation)] = self._get_filter(operation, field_type)

        return raw_result, operations

    @staticmethod
    def _get_field_type(field: ModelField) -> Any:
        result = field.outer_type_
        if field.is_complex():
            result = field.outer_type_.__origin__
        if result not in filters_base.FILTER_MAPPING:
            raise UnknownTypeError(result)

        return result

    @staticmethod
    def _get_filter(operation: str, field_type: Any) -> Type[Filter]:
        for filter_item in filters_base.FILTER_MAPPING[field_type]:
            if filter_item.operation() == operation:
                return filter_item
        else:
            raise UnknownOperationError(field_type, operation)
