from collections import deque
from typing import Any, Dict, Deque, List, Literal, Optional, Tuple, Type, Union

from pydantic import root_validator, create_model, BaseModel
from pydantic.main import ModelMetaclass, ModelField

__all__ = ['prepare_validation_model']


def prepare_validation_model(
    model: Type[BaseModel],
    delimiter: str,
    ordering: Union[bool, List[str]]
) -> Type[BaseModel]:
    class OptionalFieldsModel(model, metaclass=AllOptionalMeta):
        pass

    fields: Dict[str, Tuple[Any, None]] = _prepare_field_definitions(OptionalFieldsModel, delimiter)
    if ordering:
        fields['ordering'] = _prepare_ordering_field(list(fields), ordering)

    return create_model(
        'InternalModel',
        __validators__={
            'preprocess': root_validator(pre=True, allow_reuse=True)(_preprocess),
        },
        **fields,
    )


class AllOptionalMeta(ModelMetaclass):
    def __new__(mcs, name: str, bases: Tuple[type], namespaces: Dict[str, Any], **kwargs):
        annotations: dict = namespaces.get('__annotations__', {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break

                annotations.update(base_.__annotations__)

        namespaces['__annotations__'] = {
            field: value if field.startswith('__') else Optional[value]
            for field, value in annotations.items()
        }

        return super().__new__(mcs, name, bases, namespaces, **kwargs)


def _get_field_type(cls: Type[BaseModel], name: str):
    field_type = cls.__fields__[name].outer_type_
    if hasattr(field_type, '__origin__'):
        return field_type.__origin__

    return field_type


def _preprocess(cls: Type[BaseModel], values: Dict[str, Any]) -> Dict[str, Any]:
    for field_name, value in values.items():
        if not value:
            continue
        if issubclass(_get_field_type(cls, field_name), list):
            values[field_name] = [item.strip() for item in value.split(',')]

    return values


def _prepare_field_definitions(model: Type[BaseModel], delimiter: str) -> Dict[str, Tuple[Any, None]]:
    result: Dict[str, Tuple[Any, None]] = {}
    q: Deque[Tuple, ModelField] = deque([((name,), field) for name, field in model.__fields__.items()])

    while q:
        item: Tuple[Tuple[str, ...], Any] = q.popleft()
        name, field = item

        # TODO: refactor is_pydantic_model
        try:
            is_pydantic_model = issubclass(field.outer_type_, BaseModel)
        except:
            is_pydantic_model = False

        if is_pydantic_model:
            q.extend(
                ((*name, sub_name), sub_field)
                for sub_name, sub_field in field.outer_type_.__fields__.items()
            )
            continue

        result[delimiter.join(name)] = field.outer_type_, None

    return result


def _prepare_ordering_field(field_names: List[str], ordering: Union[bool, List[str]]) -> Tuple[Type, None]:
    accepted_field_names = field_names
    if isinstance(ordering, list):
        accepted_field_names = [name for name in field_names if name in ordering]

    result = tuple(accepted for name in accepted_field_names for accepted in (name, f'-{name}'))
    return List[Literal[result]], None
