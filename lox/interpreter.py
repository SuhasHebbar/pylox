from typing import List

from . import util
from .ast import Expr, ExprOperation, Binary, Grouping, Literal, Unary, StmtOperation, Stmt, Variable, Var, Assign, \
    Block
from .environment import Environment
from .token import Token
from .token_type import TokenType as TT


class Interpreter(ExprOperation, StmtOperation):
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter
        self.environment = Environment()

    def on_block(self, block: Block):
        parent_env = self.environment

        # Create new environment on entering Block and overriede current environment
        self.environment = Environment(parent_env)

        try:
            statements = block.statements
            for statement in statements:
                statement.perform_operation(self)
        finally:
            # Set environment back to parent environment on leaving block.
            self.environment = parent_env

    def on_assign(self, assign: Assign):
        value = self._evaluate(assign.value)
        self.environment.assign(assign.identifier, value)

    def on_variable(self, variable: Variable):
        return self.environment.get(variable.name)

    def on_var(self, var: Var):
        initializer_value = self._evaluate(var.initializer)
        self.environment.define(var.name.lexeme, initializer_value)

    class RuntimeError(RuntimeError):
        def __init__(self, token: Token, msg: str):
            super(RuntimeError, self).__init__(msg)
            self.token = token

    def evaluate(self, statements: List[Stmt]):
        try:
            for statement in statements:
                statement.perform_operation(self)
        except Interpreter.RuntimeError as e:
            self.error_reporter.runtime_error(e)

    def _evaluate(self, expr: Expr):
        if expr is not None:
            return expr.perform_operation(self)
        else:
            return None

    def on_binary(self, binary: Binary):
        operator_token = binary.operator
        operator = operator_token.type
        lhs = self._evaluate(binary.left)
        rhs = self._evaluate(binary.right)

        if operator == TT.EQUAL_EQUAL:
            return lhs == rhs
        elif operator == TT.BANG_EQUAL:
            return lhs != rhs
        elif operator == TT.GREATER:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs > rhs
        elif operator == TT.GREATER_EQUAL:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs >= rhs
        elif operator == TT.LESS:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs < rhs
        elif operator == TT.LESS_EQUAL:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs <= rhs
        elif operator == TT.MINUS:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs - rhs
        elif operator == TT.PLUS:
            Interpreter.check_numorstring_operands(operator_token, lhs, rhs)
            return lhs + rhs
        elif operator == TT.SLASH:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs / rhs
        elif operator == TT.STAR:
            Interpreter.check_number_operands(operator_token, lhs, rhs)
            return lhs * rhs
        else:
            raise Interpreter.RuntimeError(binary.operator, f'Unexpected operand {operator}')

    def on_grouping(self, grouping: Grouping):
        return self._evaluate(grouping.expr)

    def on_literal(self, literal: Literal):
        return literal.value

    def on_unary(self, unary: Unary):
        operator = unary.operator.type
        expr_val = self._evaluate(unary.expr)

        if operator == TT.MINUS:
            if not isinstance(expr_val, float):
                raise Interpreter.RuntimeError(unary.operator, 'Expected number for unary operator -.')
            return -expr_val
        elif operator == TT.BANG:
            return not expr_val
        else:
            raise Interpreter.RuntimeError(unary.operator, f'Unexpected {operator}. Expected - or !')

    def on_print(self, printstmt):
        print(util.stringified(self._evaluate(printstmt.expr)))

    def on_expression(self, exprstmt):
        self._evaluate(exprstmt.expr)

    @staticmethod
    def check_number_operands(operator: Token, lhs, rhs):
        if (not isinstance(lhs, float)) and (not isinstance(rhs, float)):
            raise Interpreter.RuntimeError(operator, f'Expected number operands for operator: {operator.lexeme}')

    @staticmethod
    def check_numorstring_operands(operator: Token, lhs, rhs):
        if isinstance(lhs, float) and isinstance(rhs, float):
            return

        if isinstance(lhs, str) and isinstance(rhs, str):
            return

        raise Interpreter.RuntimeError(operator, f'Expected either only number or string operands for operator: {operator.lexeme}')









