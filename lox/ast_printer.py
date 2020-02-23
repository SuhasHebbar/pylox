from lox.ast import ExprOperation, Binary, Grouping, Literal, Unary


class AstPrinter(ExprOperation):
    def onBinary(self, binary: Binary):
        return f'({binary.operator.lexeme} {binary.left.perform_operation(self)} {binary.right.perform_operation(self)})'

    def onGrouping(self, grouping: Grouping):
        return grouping.expr.perform_operation(self)

    def onLiteral(self, literal: Literal):
        val = literal.value
        if isinstance(val, str):
            return f'\'{val}\''
        elif isinstance(val, float):
            return f'{val:g}'
        elif isinstance(val, bool):
            return str(val).lower()
        elif val == None:
            return 'nil'
        else:
            return literal.value

    def onUnary(self, unary: Unary):
        return f'({unary.operator.lexeme} {unary.expr.perform_operation(self)})'
