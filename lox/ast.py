from abc import ABC, abstractmethod
from typing import Any
from lox.token import Token


class ExprOperation(ABC):
    @abstractmethod
    def on_literal(self, literal):
        pass

    @abstractmethod
    def on_unary(self, unary):
        pass

    @abstractmethod
    def on_binary(self, binary):
        pass

    @abstractmethod
    def on_grouping(self, grouping):
        pass


class Expr(ABC):
    @abstractmethod
    def perform_operation(self, operation: ExprOperation):
        pass


class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def perform_operation(self, operation: ExprOperation):
        return operation.on_literal(self)


class Unary(Expr):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr

    def perform_operation(self, operation: ExprOperation):
        return operation.on_unary(self)


class Binary(Expr):
    def __init__(self, operator: Token, left: Expr, right: Expr):
        self.operator = operator
        self.left = left
        self.right = right

    def perform_operation(self, operation: ExprOperation):
        return operation.on_binary(self)


class Grouping(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

    def perform_operation(self, operation: ExprOperation):
        return operation.on_grouping(self)


