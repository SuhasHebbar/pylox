from abc import ABC, abstractmethod
from typing import Any, List
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

   @abstractmethod
   def on_variable(self, variable):
       pass

   @abstractmethod
   def on_assign(self, assign):
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


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def perform_operation(self, operation: ExprOperation):
        return operation.on_variable(self)


class Assign(Expr):
    def __init__(self, identifier: Token, value: Expr):
        self.identifier = identifier
        self.value = value

    def perform_operation(self, operation: ExprOperation):
        return operation.on_assign(self)


class StmtOperation(ABC):
   @abstractmethod
   def on_expression(self, expression):
       pass

   @abstractmethod
   def on_print(self, print):
       pass

   @abstractmethod
   def on_var(self, var):
       pass

   @abstractmethod
   def on_block(self, block):
       pass


class Stmt(ABC):
    @abstractmethod
    def perform_operation(self, operation: StmtOperation):
        pass


class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def perform_operation(self, operation: StmtOperation):
        return operation.on_expression(self)


class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def perform_operation(self, operation: StmtOperation):
        return operation.on_print(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def perform_operation(self, operation: StmtOperation):
        return operation.on_var(self)


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def perform_operation(self, operation: StmtOperation):
        return operation.on_block(self)


