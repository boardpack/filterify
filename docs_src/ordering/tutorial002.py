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
