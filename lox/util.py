from enum import Enum

from lox.token import Token


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
    METHOD = 'method'
    INITIALIZER = 'initializer'
    NONE = 'none'


class ClassType(Enum):
    CLASS = 'class'
    NONE = 'none'


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, msg: str):
        super(RuntimeError, self).__init__(msg)
        self.token = token
