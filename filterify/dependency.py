from typing import Any, Type

from pydantic import BaseModel

try:
    from fastapi import Depends, Query
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "fastapi is not installed, you cannot use the 'as_dependency' method.\n"
        "To install, run: pip install fastapi"
    ) from e


__all__ = ["create_dependency"]


def create_dependency(model: Type[BaseModel]) -> Any:
    for field in model.__fields__.values():
        field.field_info = Query(...)

    return Depends(model)
