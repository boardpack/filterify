<p align="center">
  <a href="https://filterify.boardpack.org/"><img src="https://filterify.boardpack.org/img/logo-white.png" alt="Filterify"></a>
</p>
<p align="center">
    <em>filterify is a pydantic-based library to handle filters from the query params.</em>
</p>
<p align="center">
    <a href="https://github.com/boardpack/filterify/actions?query=workflow%3ATest" target="_blank">
        <img src="https://github.com/boardpack/filterify/workflows/Test/badge.svg" alt="Test">
    </a>
    <a href="https://codecov.io/gh/boardpack/filterify" target="_blank">
        <img src="https://img.shields.io/codecov/c/github/boardpack/filterify?color=%2334D058" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/filterify" target="_blank">
        <img src="https://img.shields.io/pypi/v/filterify?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://camo.githubusercontent.com/d91ed7ac7abbd5a6102cbe988dd8e9ac21bde0a73d97be7603b891ad08ce3479/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f636f64652532307374796c652d626c61636b2d3030303030302e737667" data-canonical-src="https://img.shields.io/badge/code%20style-black-000000.svg" style="max-width:100%;"></a>
    <a href="https://pycqa.github.io/isort/" rel="nofollow"><img src="https://camo.githubusercontent.com/fe4a658dd745f746410f961ae45d44355db1cc0e4c09c7877d265c1380248943/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f253230696d706f7274732d69736f72742d2532333136373462313f7374796c653d666c6174266c6162656c436f6c6f723d656638333336" alt="Imports: isort" data-canonical-src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&amp;labelColor=ef8336" style="max-width:100%;"></a>
</p>

---

**Documentation**: <a href="https://filterify.boardpack.org" target="_blank">https://filterify.boardpack.org</a>

**Source Code**: <a href="https://github.com/boardpack/filterify" target="_blank">https://github.com/boardpack/filterify</a>

---

## Requirements

Python 3.8+

filterify has the next dependencies:

* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Installation

<div class="termy">

```console
$ pip install filterify

---> 100%
```

</div>

## First steps

To start to work with filterify, you just need to have some Pydantic model you want to have as filters.

Let's define simple `Address` and `Shipment` models. Then just pass the `Shipment` model to the `Filterify` constructor
and you will get a callable object to parse query params. By default, the parser returns a dictionary structure with
the parsing results.

```Python  hl_lines="18 20"
from pydantic import BaseModel
from filterify import Filterify


class Address(BaseModel):
    street: str
    city: str
    country: str


class Shipment(BaseModel):
    name: str
    sender: Address
    recipient: Address
    weight: float


model_filter = Filterify(Shipment)

print(model_filter('name=shoes&sender__country=US&recipient__country__ne=CA'))
# [
#     {
#         'field': [
#             'name'
#         ],
#         'value': 'shoes',
#         'operation': 'eq'
#     },
#     {
#         'field': [
#             'sender',
#             'country'
#         ],
#         'value': 'US',
#         'operation': 'eq'
#     },
#     {
#         'field': [
#             'recipient',
#             'country'
#         ],
#         'value': 'CA',
#         'operation': 'ne'
#     }
# ]

```
_(This script is complete, it should run "as is")_

Filterify supports nested models and uses `__` as a delimiter for the nested models and operations. If you want to
change it, pass the needed `delimiter` to the constructor as it's shown in the next example.

```Python  hl_lines="13"
from pydantic import BaseModel
from filterify import Filterify


class Address(BaseModel):
    country: str


class Shipment(BaseModel):
    sender: Address


model_filter = Filterify(Shipment, delimiter='$')

print(model_filter('sender$country$ne=US'))
# [
#     {
#         'field': [
#             'sender',
#             'country'
#         ],
#         'value': 'US',
#         'operation': 'ne'
#     }
# ]

```
_(This script is complete, it should run "as is")_

Also, by default unknown fields are ignored, but you can change this behavior by passing `False` to the constructor
parameter `ignore_unknown_name`.

```Python  hl_lines="9"
from pydantic import BaseModel
from filterify import Filterify


class User(BaseModel):
    name: str


model_filter = Filterify(User, ignore_unknown_name=False)

print(model_filter('sender=US'))
# filterify.exceptions.UnknownFieldError: Filter name is not presented in the model: sender

```
_(This script is complete, it should run "as is")_

## Ordering option

You can add an `ordering` field that accepts all model field names. Currently, it's used a django-like style when desc
is passed as `-field_name`.

```Python  hl_lines="14"
from pydantic import BaseModel
from filterify import Filterify


class Address(BaseModel):
    country: str


class Shipment(BaseModel):
    name: str
    sender: Address


model_filter = Filterify(Shipment, ordering=True)

print(model_filter('ordering=unknown_field'))
# raises standard pydantic ValidationError with the next message:
# unexpected value; permitted: 'name', '-name', 'sender__country', '-sender__country'

```
_(This script is complete, it should run "as is")_

If you want to change the accepted field name list, you can pass a list instead of the `True` value.

```Python  hl_lines="14"
from pydantic import BaseModel
from filterify import Filterify


class Address(BaseModel):
    country: str


class Shipment(BaseModel):
    name: str
    sender: Address


model_filter = Filterify(Shipment, ordering=['name'])

print(model_filter('ordering=unknown_field'))
# raises standard pydantic ValidationError with the next message:
# unexpected value; permitted: 'name', '-name'

```
_(This script is complete, it should run "as is")_

## Usage with FastAPI

Most validation work is done by pydantic, so filterify can be easily used with FastAPI.
The internal validation model is wrapped by `fastapi.Depends` and exposed by the `as_dependency` method.

```Python  hl_lines="29 35"
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from filterify import Filterify


class Address(BaseModel):
    street: str
    city: str
    country: str


class Shipment(BaseModel):
    name: str
    sender: Address
    recipient: Address
    weight: float
    length: float
    height: float


shipment_filter = Filterify(Shipment)


app = FastAPI()


@app.get('/shipments', dependencies=[shipment_filter.as_dependency()])
def shipments():
    return []


@app.get('/another_shipments')
def another_shipments(filters=shipment_filter.as_dependency()):
    print(filters)
    return []


if __name__ == '__main__':
    uvicorn.run(app)

```
_(This script is complete, it should run "as is")_

## Acknowledgments

Special thanks to [Sebastián Ramírez](https://github.com/tiangolo) and his [FastAPI](https://github.com/tiangolo/fastapi) project,  some scripts and documentation structure and parts were used from there.

## License

This project is licensed under the terms of the MIT license.
