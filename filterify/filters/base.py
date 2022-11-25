from typing import Any, Dict, List, Type


__all__ = [
    'Filter', 'Equal', 'NotEqual', 'GreaterThan', 'LessThan',
    'GreaterThanOrEqual', 'LessThanOrEqual', 'In', 'NotIn',
    'register_base_filter',
]


class Filter:
    def __init__(self, field: str, value: Any, delimiter: str):
        self._value = value

        self._field = [field]
        if delimiter in field:
            self._field = field.split(delimiter)

    @classmethod
    def operation(cls) -> str:
        raise NotImplementedError()

    def name(self) -> str:
        raise NotImplementedError()

    def value(self):
        return {
            'field': self._field,
            'value': self._value,
            'operation': self.operation(),
        }


class Equal(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'eq'

    def name(self) -> str:
        return 'Equals'


class NotEqual(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'ne'

    def name(self) -> str:
        return 'Not Equals'


class GreaterThan(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'gt'

    def name(self) -> str:
        return 'Greater than'


class LessThan(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'lt'

    def name(self) -> str:
        return 'Less than'


class GreaterThanOrEqual(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'gte'

    def name(self) -> str:
        return 'Greater than or equal'


class LessThanOrEqual(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'lte'

    def name(self) -> str:
        return 'Less than or equal'


class In(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'in'

    def name(self) -> str:
        return 'In'


class NotIn(Filter):
    @classmethod
    def operation(cls) -> str:
        return 'not_in'

    def name(self) -> str:
        return 'Not in'


FILTER_MAPPING: Dict[Any, List[Type[Filter]]] = {
    int: [Equal, NotEqual, GreaterThan, LessThan, GreaterThanOrEqual, LessThanOrEqual, In, NotIn],
    float: [Equal, NotEqual, GreaterThan, LessThan, GreaterThanOrEqual, LessThanOrEqual, In, NotIn],
    bool: [Equal, NotEqual],
    str: [Equal, NotEqual, In, NotIn],
    list: [Equal, NotEqual, In, NotIn],
}


def register_base_filter(type_list: List[Any], *filters: Type[Filter]) -> None:
    for type_ in type_list:
        if type_ not in FILTER_MAPPING:
            FILTER_MAPPING[type_] = []

        for filter_ in filters:
            if filter_ not in FILTER_MAPPING[type_]:
                FILTER_MAPPING[type_].append(filter_)
