from typing import Any, Type, Dict, List

import pytest
from pydantic import BaseModel

from filterify import Filterify
from filterify.exceptions import UnknownFieldError


@pytest.fixture
def user_model() -> Type[BaseModel]:
    class User(BaseModel):
        name: str
        age: int
        height: float
        colors: List[str]

    return User


@pytest.mark.parametrize(
    'query_params, expected', [
        (
            'name=John&age=10',
            [
                {'field': ['name'], 'value': 'John', 'operation': 'eq'},
                {'field': ['age'], 'value': 10, 'operation': 'eq'},
            ],
        ),
        ('height=150.5', [{'field': ['height'], 'value': 150.5, 'operation': 'eq'}]),
        ('colors=blue,red,green', [{'field': ['colors'], 'value': ['blue', 'red', 'green'], 'operation': 'eq'}]),
        ('colors__in=blue,red,green', [{'field': ['colors'], 'value': ['blue', 'red', 'green'], 'operation': 'in'}]),
        (
            'name=John&age=10&height=150.5&colors=blue,red,green',
            [
                {
                    'field': ['name'],
                    'value': 'John',
                    'operation': 'eq',
                },
                {
                    'field': ['age'],
                    'value': 10,
                    'operation': 'eq',
                },
                {
                    'field': ['height'],
                    'value': 150.5,
                    'operation': 'eq',
                },
                {
                    'field': ['colors'],
                    'value': ['blue', 'red', 'green'],
                    'operation': 'eq',
                },
            ],
        ),
        ('name__ne=John', [{'field': ['name'], 'value': 'John', 'operation': 'ne'}]),
        ('height__ne=150.5', [{'field': ['height'], 'value': 150.5, 'operation': 'ne'}]),
        ('age__ne=10', [{'field': ['age'], 'value': 10, 'operation': 'ne'}]),
        ('age__gt=10', [{'field': ['age'], 'value': 10, 'operation': 'gt'}]),
        ('age__lt=10', [{'field': ['age'], 'value': 10, 'operation': 'lt'}]),
        ('age__gte=10', [{'field': ['age'], 'value': 10, 'operation': 'gte'}]),
        ('age__lte=10', [{'field': ['age'], 'value': 10, 'operation': 'lte'}]),
        ('age__lte=10&age__gte=1', [
            {'field': ['age'], 'value': 10, 'operation': 'lte'},
            {'field': ['age'], 'value': 1, 'operation': 'gte'},
        ]),
        ('unknown=10', []),
        ('unknown__lte=10', []),
    ]
)
def test_model_filter(
    user_model: Type[BaseModel],
    query_params: str,
    expected: List[Dict[str, Any]],
):
    model_filter = Filterify(user_model)
    assert model_filter(query_params) == expected


@pytest.mark.parametrize(
    'query_params, expected', [
        (
            'user__age__lte=10',
            [{'field': ['user', 'age'], 'value': 10, 'operation': 'lte'}],
        ),
    ]
)
def test_nested_model(
    user_model: Type[BaseModel],
    query_params: str,
    expected: List[Dict[str, Any]],
):
    class AnotherModel(BaseModel):
        user: user_model

    model_filter = Filterify(AnotherModel)
    assert model_filter(query_params) == expected


@pytest.mark.parametrize(
    'query_params, expected', [
        (
            'data__user__age__lte=10',
            [{'field': ['data', 'user', 'age'], 'value': 10, 'operation': 'lte'}],
        ),
    ]
)
def test_nested_model_2_level(
    user_model: Type[BaseModel],
    query_params: str,
    expected: List[Dict[str, Any]],
):
    class UserContainerFilter(BaseModel):
        user: user_model

    class Model(BaseModel):
        data: UserContainerFilter

    model_filter = Filterify(Model)
    assert model_filter(query_params) == expected


def test_unknown_field_name_exception(user_model: Type[BaseModel]):
    model_filter = Filterify(user_model, ignore_unknown_name=False)

    with pytest.raises(UnknownFieldError):
        assert model_filter('unknown=10')
