from typing import Protocol, List, Type, Union

from pydantic import BaseModel


__all__ = ['ValidatorProtocol']


class ValidatorProtocol(Protocol):
    delimiter: str
    ordering: Union[bool, List[str]]

    def parse(self, model: Type[BaseModel]) -> Type[BaseModel]:
        raise NotImplementedError
