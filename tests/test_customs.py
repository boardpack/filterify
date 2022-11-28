from typing import Type
from copy import deepcopy

import pytest
from pydantic import BaseModel

from filterify import Filterify
from filterify.filters import base as filters_base
from filterify.filters.base import register_base_filter


@pytest.fixture
def refresh_filter_types() -> None:
    filter_mapping = deepcopy(filters_base.FILTER_MAPPING)
    yield
    filters_base.FILTER_MAPPING = filter_mapping


@pytest.fixture
def custom_type() -> Type:
    class MyType(int):
        pass

    return MyType


@pytest.fixture
def custom_filter() -> Type[filters_base.Filter]:
    class MyFilter(filters_base.Filter):
        @classmethod
        def operation(cls) -> str:
            return 'filter'

        @classmethod
        def name(cls) -> str:
            return 'Custom Filter'

    return MyFilter


def test_custom_filter(refresh_filter_types: None, custom_filter: Type[filters_base.Filter]):
    class User(BaseModel):
        name: str

    register_base_filter([str], custom_filter)

    model_filter = Filterify(User)
    result = model_filter('name__filter=example')
    assert result[0]['operation'] == custom_filter.operation()


def test_custom_type(refresh_filter_types: None, custom_type: Type):
    class User(BaseModel):
        name: custom_type

    register_base_filter([custom_type], filters_base.EqualFilter)

    model_filter = Filterify(User)
    assert model_filter('name=15') == [{'field': ['name'], 'value': 15, 'operation': 'eq'}]
