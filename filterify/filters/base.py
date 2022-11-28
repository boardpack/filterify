from abc import ABC
from typing import Any, Dict, List, Type

from filterify.protocols import FilterProtocol


__all__ = [
    'Filter', 'EqualFilter', 'NotEqualFilter', 'GreaterThanFilter', 'LessThanFilter',
    'GreaterThanOrEqualFilter', 'LessThanOrEqualFilter',
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


class LikeFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'contains'

    def name(self) -> str:
        return 'Like'


class NotLikeFilter(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'not_contains'

    def name(self) -> str:
        return 'Not like'


FILTER_MAPPING: Dict[Any, List[Type[Filter]]] = {
    int: [
        EqualFilter, NotEqualFilter, GreaterThanFilter, LessThanFilter, GreaterThanOrEqualFilter,
        LessThanOrEqualFilter,
    ],
    float: [
        EqualFilter, NotEqualFilter, GreaterThanFilter, LessThanFilter, GreaterThanOrEqualFilter,
        LessThanOrEqualFilter,
    ],
    bool: [EqualFilter, NotEqualFilter],
    str: [EqualFilter, NotEqualFilter, LikeFilter, NotLikeFilter],
    list: [EqualFilter, NotEqualFilter],
}
