from collections import deque
from typing import Any, Dict, Optional, Tuple, Type

from pydantic import root_validator, create_model, BaseModel
from pydantic.main import ModelMetaclass

__all__ = ['prepare_validation_model']


def _preprocess(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    def _get_field_type(name: str):
        field_type = cls.__fields__[name].outer_type_
        if hasattr(field_type, '__origin__'):
            return field_type.__origin__

        return field_type

    for field_name, value in values.items():
        if not value:
            continue
        if issubclass(_get_field_type(field_name), list):
            values[field_name] = [item.strip() for item in value.split(',')]

    return values


def prepare_validation_model(model: Type[BaseModel], delimiter: str) -> Type[BaseModel]:
    class OptionalFieldsModel(model, metaclass=AllOptionalMeta):
        pass

    return create_model(
        'InternalModel',
        __validators__={
            'preprocess': root_validator(pre=True, allow_reuse=True)(_preprocess),
        },
        **_prepare_field_definitions(OptionalFieldsModel, delimiter),
    )


def _prepare_field_definitions(model: Type[BaseModel], delimiter: str) -> Dict[str, Tuple[Any, None]]:
    result: Dict[str, Tuple[Any, None]] = {}
    q = deque([((name,), field) for name, field in model.__fields__.items()])

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
