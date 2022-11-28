from typing import Any, Dict, List, Tuple, Type, Union

from pydantic import BaseModel

__all__ = ["Validator", "Parser", "Filter"]


class Validator:
    delimiter: str
    ordering: Union[bool, List[str]]

    def __init__(self, delimiter: str, ordering: Union[bool, List[str]]):
        self.delimiter = delimiter
        self.ordering = ordering

    def parse(self, model: Type[BaseModel]) -> Type[BaseModel]:
        raise NotImplementedError()


class Filter:
    _value: Any
    _field: Union[str, List[str]]

    def __init__(self, field: str, value: Any, delimiter: str):
        self._value = value

        self._field = [field]
        if delimiter in field:
            self._field = field.split(delimiter)

    def value(self) -> Any:
        return {
            "field": self._field,
            "value": self._value,
            "operation": self.operation(),
        }

    @classmethod
    def operation(cls) -> str:
        raise NotImplementedError()

    def name(self) -> str:
        raise NotImplementedError()


class Parser:
    delimiter: str
    validation_model: Type[BaseModel]
    ignore_unknown_name: bool = True

    def __init__(
        self,
        validation_model: Type[BaseModel],
        delimiter: str,
        ignore_unknown_name: bool = True,
    ):
        self.validation_model = validation_model
        self.delimiter = delimiter
        self.ignore_unknown_name = ignore_unknown_name

    def parse(
        self, raw_qs: str
    ) -> Tuple[Dict[Tuple[str, str], Any], Dict[Tuple[str, str], Type[Filter]]]:
        raise NotImplementedError()
