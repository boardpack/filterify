from pydantic import BaseModel
from filterify import Filterify


class User(BaseModel):
    name: str


model_filter = Filterify(User, ignore_unknown_name=False)

print(model_filter('sender=US'))
# filterify.exceptions.UnknownFieldError: Filter name is not presented in the model: sender
