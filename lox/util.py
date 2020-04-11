from enum import Enum


def stringified(val):
    if isinstance(val, str):
        return f'{val}'
    elif isinstance(val, float):
        return f'{val:g}'
    elif isinstance(val, bool):
        return str(val).lower()
    elif val is None:
        return 'nil'
    else:
        return val


class ReturnValue(Exception):
    def __init__(self, val):
        self.val = val


class FunctionKind(Enum):
    FUNCTION = 'function'
    NONE = 'none'
