from typing import Any, Dict, List, Tuple, Type, Union

from pydantic.main import BaseModel

from . import parser
from .validation import prepare_validation_model
from .filters import base as filters_base


__all__ = ['Filterify']


class Filterify:
    delimiter: str = '__'
    ignore_unknown_name: bool = True
    ordering: Union[bool, List[str]] = False

    def __init__(
        self,
        model: Type[BaseModel],
        delimiter: Union[str, None] = None,
        ignore_unknown_name: bool = True,
        ordering: Union[bool, List[str]] = False,
    ):
        self.model = model
        self.ignore_unknown_name = ignore_unknown_name
        self.ordering = ordering

        if delimiter:
            self.delimiter = delimiter

        self._validation_model = prepare_validation_model(
            model=self.model,
            delimiter=self.delimiter,
            ordering=self.ordering,
        )

    def __call__(self, raw_qs: str) -> List[Dict[str, Any]]:
        data = parser.parse(
            raw_qs,
            self._validation_model,
            self.delimiter,
            ignore_unknown_name=self.ignore_unknown_name,
        )
        parsed_data: Dict[Tuple[str, str], Any] = data[0]
        filters: Dict[Tuple[str, str], Type[filters_base.Filter]] = data[1]

        result: List[Dict[str, Any]] = []
        for (field, operation), filter_class in filters.items():
            validated_data = self._validation_model(**{field: parsed_data[(field, operation)]})
            field_filter = filter_class(field=field, value=getattr(validated_data, field), delimiter=self.delimiter)
            result.append(field_filter.value())

        return result

    def as_dependency(self):
        from .dependency import create_dependency
        return create_dependency(self._validation_model)
