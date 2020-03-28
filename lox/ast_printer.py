from lox import util
from lox.ast import ExprOperation, Binary, Grouping, Literal, Unary


class AstPrinter(ExprOperation):
    def on_binary(self, binary: Binary):
        return f'({binary.operator.lexeme} {binary.left.perform_operation(self)} {binary.right.perform_operation(self)})'

    def on_grouping(self, grouping: Grouping):
        return grouping.expr.perform_operation(self)

    def on_literal(self, literal: Literal):
        return util.stringified(literal.value)

    def on_unary(self, unary: Unary):
        return f'({unary.operator.lexeme} {unary.expr.perform_operation(self)})'
