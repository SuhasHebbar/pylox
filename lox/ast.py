from abc import ABC, abstractmethod
from typing import Any
from lox.token import Token


class ExprOperation(ABC):
   @abstractmethod
   def onLiteral(self, literal):
       pass

   @abstractmethod
   def onUnary(self, unary):
       pass

   @abstractmethod
   def onBinary(self, binary):
       pass

   @abstractmethod
   def onGrouping(self, grouping):
       pass


class Expr(ABC):
    @abstractmethod
    def perform_operation(self, operation: ExprOperation):
        pass


class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def perform_operation(self, operation: ExprOperation):
        return operation.onLiteral(self)


class Unary(Expr):
    def __init__(self, operator: Token, expr: Expr):
        self.operator = operator
        self.expr = expr

    def perform_operation(self, operation: ExprOperation):
        return operation.onUnary(self)


class Binary(Expr):
    def __init__(self, operator: Token, left: Expr, right: Expr):
        self.operator = operator
        self.left = left
        self.right = right

    def perform_operation(self, operation: ExprOperation):
        return operation.onBinary(self)


class Grouping(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

    def perform_operation(self, operation: ExprOperation):
        return operation.onGrouping(self)


