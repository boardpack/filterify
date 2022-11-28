from typing import Any, Dict, List, Tuple, Type, Union

from pydantic.main import BaseModel

from .parser import DefaultParser
from .validation import DefaultValidator
from .protocols import ValidatorProtocol, ParserProtocol, FilterProtocol


__all__ = ['Filterify']


class Filterify:
    delimiter: str = '__'
    ignore_unknown_name: bool = True
    ordering: Union[bool, List[str]] = False
    _validation_model: Type[BaseModel]
    _parser: ParserProtocol

    def __init__(
        self,
        model: Type[BaseModel],
        delimiter: Union[str, None] = None,
        ignore_unknown_name: bool = True,
        ordering: Union[bool, List[str]] = False,
        validator_class: Type[ValidatorProtocol] = DefaultValidator,
        parser_class: Type[ParserProtocol] = DefaultParser,
    ):
        self.model = model
        self.ignore_unknown_name = ignore_unknown_name
        self.ordering = ordering

        if delimiter:
            self.delimiter = delimiter

        validator = validator_class(delimiter=self.delimiter, ordering=self.ordering)
        self._validation_model = validator.parse(model)
        self._parser = parser_class(
            validation_model=self._validation_model,
            delimiter=self.delimiter,
            ignore_unknown_name=self.ignore_unknown_name,
        )

    def __call__(self, raw_qs: str) -> List[Dict[str, Any]]:
        data = self._parser.parse(raw_qs)
        parsed_data: Dict[Tuple[str, str], Any] = data[0]
        filters: Dict[Tuple[str, str], Type[FilterProtocol]] = data[1]

        result: List[Dict[str, Any]] = []
        for (field, operation), filter_class in filters.items():
            validated_data = self._validation_model(**{field: parsed_data[(field, operation)]})
            field_filter = filter_class(field=field, value=getattr(validated_data, field), delimiter=self.delimiter)
            result.append(field_filter.value())

        return result

    def as_dependency(self):
        from .dependency import create_dependency
        return create_dependency(self._validation_model)
