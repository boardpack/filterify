from typing import List, Iterable, Type

import pytest
from pydantic import BaseModel, ValidationError

from filterify import Filterify


def _get_field_list(fields: Iterable[str], desc: bool = False, n: int = -1) -> List[str]:
    fields = [name for name in fields]
    fields = fields[:len(fields) if n == -1 else n]
    if desc:
        fields = [allowed_name for name in fields for allowed_name in (name, f'-{name}')]
    return fields


@pytest.fixture
def model() -> Type[BaseModel]:
    class Shipment(BaseModel):
        name: str
        weight: float
        length: float
        height: float

    return Shipment


@pytest.mark.parametrize(
    'n', [-1, 2],
    ids=('all-fields', 'fields-part'),
)
def test_ordering(model: Type[BaseModel], n: int):
    field_list = _get_field_list(model.__fields__, n=n)

    model_filter = Filterify(model, ordering=True if n == -1 else field_list)

    with pytest.raises(ValidationError) as exc:
        model_filter('ordering=unknown_field')

    allowed_field_list = ', '.join(f"'{name}'" for name in _get_field_list(model.__fields__, desc=True, n=n))
    assert exc.value.errors()[0]['msg'].endswith(f': {allowed_field_list}')
