from lox.token import Token
import lox.interpreter
from lox.util import LoxRuntimeError


class Environment:
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value):
        self.values[name] = value

    def assign(self, token: Token, value):
        name = token.lexeme
        if name in self.values:
            self.values[name] = value
        elif self.enclosing is not None:
            self.enclosing.assign(token, value)
        else:
            raise LoxRuntimeError(token, f'Undefined variable {name}.')

    def assign_at(self, depth: int, token: Token, value):
        self.ancestor(depth).assign(token, value)

    def get(self, token: Token):
        name = token.lexeme
        if name in self.values:
            return self.values[name]
        elif self.enclosing is not None:
            return self.enclosing.get(token)
        else:
            raise LoxRuntimeError(token, f'Undefined variable \'{name}\'.')

    def get_at(self, depth, name: str):
        env = self.ancestor(depth).values
        if name in env:
            return env[name]

    def ancestor(self, depth):
        curr = self
        for _ in range(depth):
            curr = curr.enclosing
        return curr


