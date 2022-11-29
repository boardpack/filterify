__all__ = ["UnknownFieldError", "UnknownTypeError", "UnknownOperationError"]


class UnknownFieldError(ValueError):
    def __init__(self, name: str):
        super().__init__(f"Filter name is not presented in the model: {name}")


class UnknownTypeError(ValueError):
    def __init__(self, name: str):
        super().__init__(f"Unknown field type: {name}")


class UnknownOperationError(ValueError):
    def __init__(self, field_type: str, operation: str):
        super().__init__(f"Unknown operation for the {field_type}: {operation}")
