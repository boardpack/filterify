from abc import ABC
from typing import Any, Dict, List, Type

from filterify.protocols import FilterProtocol


__all__ = [
    'Filter', 'EqualFilter', 'NotEqualFilter', 'GreaterThanFilter', 'LessThanFilter',
    'GreaterThanOrEqualFilter', 'LessThanOrEqualFilter', 'InFilter', 'NotInFilter',
    'register_base_filter',
]


class Filter(FilterProtocol, ABC):
    def __init__(self, field: str, value: Any, delimiter: str):
        self._value = value

        self._field = [field]
        if delimiter in field:
            self._field = field.split(delimiter)

    def value(self) -> Any:
        return {
            'field': self._field,
            'value': self._value,
            'operation': self.operation(),
        }


class EqualFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'eq'

    def name(self) -> str:
        return 'Equals'


class NotEqualFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'ne'

    def name(self) -> str:
        return 'Not Equals'


class GreaterThanFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'gt'

    def name(self) -> str:
        return 'Greater than'


class LessThanFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'lt'

    def name(self) -> str:
        return 'Less than'


class GreaterThanOrEqualFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'gte'

    def name(self) -> str:
        return 'Greater than or equal'


class LessThanOrEqualFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'lte'

    def name(self) -> str:
        return 'Less than or equal'


class InFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'in'

    def name(self) -> str:
        return 'In'


class NotInFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'not_in'

    def name(self) -> str:
        return 'Not in'


FILTER_MAPPING: Dict[Any, List[Type[Filter]]] = {
    int: [
        EqualFilter, NotEqualFilter, GreaterThanFilter, LessThanFilter, GreaterThanOrEqualFilter,
        LessThanOrEqualFilter, InFilter, NotInFilter,
    ],
    float: [
        EqualFilter, NotEqualFilter, GreaterThanFilter, LessThanFilter, GreaterThanOrEqualFilter,
        LessThanOrEqualFilter, InFilter, NotInFilter,
    ],
    bool: [EqualFilter, NotEqualFilter],
    str: [EqualFilter, NotEqualFilter, InFilter, NotInFilter],
    list: [EqualFilter, NotEqualFilter, InFilter, NotInFilter],
}


def register_base_filter(type_list: List[Any], *filters: Type[Filter]) -> None:
    for type_ in type_list:
        if type_ not in FILTER_MAPPING:
            FILTER_MAPPING[type_] = []

        for filter_ in filters:
            if filter_ not in FILTER_MAPPING[type_]:
                FILTER_MAPPING[type_].append(filter_)
