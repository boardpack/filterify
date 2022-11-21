from typing import Any, Dict, List, Type, Union

from pydantic.main import BaseModel

from . import parser
from .validation import prepare_validation_model
from .filters import base as filters_base


__all__ = ['Filterify']


class Filterify:
    delimiter: str = '__'

    def __init__(self, model: Type[BaseModel], delimiter: Union[str, None] = None):
        self.model = model

        if delimiter:
            self.delimiter = delimiter

        self._validation_model = prepare_validation_model(self.model, self.delimiter)

    def __call__(self, raw_qs: str) -> List[Dict[str, Any]]:
        data = parser.parse(raw_qs, self._validation_model, self.delimiter)
        parsed_data: Dict[str, Any] = data[0]
        operations: Dict[str, Type[filters_base.Filter]] = data[1]

        validated_data = self._validation_model(**parsed_data)

        return [
            operation(field=field, value=getattr(validated_data, field), delimiter=self.delimiter).value()
            for field, operation in operations.items()
        ]
