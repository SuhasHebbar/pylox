from typing import List, Any, Dict

from lox.ast import Function
from lox.callable import Callable, LoxCallable
from lox.token import Token
from lox.util import LoxRuntimeError


class LoxClass(Callable):
    def __init__(self, name, superclass, methods: Dict[str, LoxCallable]):
        self.methods = methods
        self.superclass = superclass
        self.name = name

    def __str__(self):
        return f'<Class {self.name}>'

    def arity(self) -> int:
        initializer = self.find_method('init')
        if initializer is not None:
            return initializer.arity()
        else:
            return 0

    def call(self, interpreter, args: List[Any]):
        instance = LoxInstance(self)
        initializer = self.find_method('init')
        if initializer is not None:
            initializer.bind(instance).call(interpreter, args)
        return instance

    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        else:
            method = self.superclass.find_method(name) if self.superclass is not None else None
            if method is not None:
                return method
            else:
                return None


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    def __str__(self):
        return f'<{str(self.klass)[1:-1]} instance>'

    def get(self, name: Token):
        key = name.lexeme

        if key in self.fields:
            return self.fields[key]
        else:
            method = self.klass.find_method(key)
            if method is not None:
                return method.bind(self)
            else:
                raise LoxRuntimeError(name, f'Undefined property \'{key}\'.')

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value
