from abc import ABC, abstractmethod
import time
from typing import List, Any

from lox.ast import Function
from lox.environment import Environment


class Callable(ABC):
    @abstractmethod
    def call(self, interpreter, args: List[Any]):
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class LoxCallable(Callable):
    def __init__(self, declaration: Function):
        self.declaration = declaration

    def call(self, interpreter, args: List[Any]):
        environment = Environment(interpreter.environment)

        for token, expression in zip(self.declaration.params, args):
            environment.define(token.lexeme, expression)

        interpreter.execute_block(self.declaration.body, environment)

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f'<function {self.declaration.name.lexeme}>'

class Clock(Callable):
    def call(self, interpreter, args: List[Any]):
        return int(time.time())

    def arity(self) -> int:
        return 0

    def __str__(self):
        return '<native_fn>'
