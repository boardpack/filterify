from typing import List

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
    packages: List[str]


shipment_filter = Filterify(Shipment)


app = FastAPI()


@app.get('/shipments', dependencies=[shipment_filter.as_dependency()])
def shipments():
    return []


if __name__ == '__main__':
    uvicorn.run(app)
