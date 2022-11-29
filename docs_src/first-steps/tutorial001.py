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
