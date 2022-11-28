from typing import Any, Dict, Protocol, List, Tuple, Type, Union

from pydantic import BaseModel


__all__ = ['ValidatorProtocol', 'ParserProtocol', 'FilterProtocol']


class ValidatorProtocol(Protocol):
    delimiter: str
    ordering: Union[bool, List[str]]

    def parse(self, model: Type[BaseModel]) -> Type[BaseModel]:
        raise NotImplementedError


class FilterProtocol(Protocol):
    _value: Any
    _field: Union[str, List[str]]

    @classmethod
    def operation(cls) -> str:
        raise NotImplementedError()

    def name(self) -> str:
        raise NotImplementedError()

    def value(self) -> Any:
        raise NotImplementedError()


class ParserProtocol(Protocol):
    delimiter: str
    validation_model: Type[BaseModel]
    ignore_unknown_name: bool = True

    def parse(self, raw_qs: str) -> Tuple[Dict[Tuple[str, str], Any], Dict[Tuple[str, str], Type[FilterProtocol]]]:
        raise NotImplementedError
