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
