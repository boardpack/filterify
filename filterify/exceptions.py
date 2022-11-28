__all__ = ["UnknownFieldError"]


class UnknownFieldError(ValueError):
    def __init__(self, name: str):
        super().__init__(f"Filter name is not presented in the model: {name}")
