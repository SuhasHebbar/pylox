from typing import List, Any

from . import util
from .callable import Callable, Clock, LoxCallable
from .lox_class import LoxClass, LoxInstance
from .ast import Expr, ExprOperation, Binary, Grouping, Literal, Unary, StmtOperation, Stmt, Variable, Var, Assign, \
    Block, IfElse, Logical, WhileLoop, Call, Function, ReturnStmt, ClassDecl, Get, SetProp, ThisExpr
from .environment import Environment
from .token import Token
from .token_type import TokenType as TT
from .util import ReturnValue, LoxRuntimeError


class Interpreter(ExprOperation, StmtOperation):
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        self.globals.define('clock', Clock())

    def on_return_stmt(self, returnstmt: ReturnStmt):
        return_value = None
        if returnstmt.value:
            return_value = self._evaluate(returnstmt.value)

        raise ReturnValue(return_value)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def lookup_variable(self, token: Token, expr: Expr):
        if expr in self.locals:
            depth = self.locals[expr]
            return self.environment.get_at(depth, token.lexeme)
        else:
            return self.globals.get(token)

    def on_class_decl(self, classdecl: ClassDecl):
        self.environment.define(classdecl.name.lexeme, None)

        methods = {}
        for method in classdecl.methods:
            methods[method.name.lexeme] = LoxCallable(method, self.environment, method.name.lexeme == 'init')

        klass = LoxClass(classdecl.name.lexeme, methods)
        self.environment.assign(classdecl.name, klass)

    def on_this_expr(self, thisexpr: ThisExpr):
        return self.lookup_variable(thisexpr.keyword, thisexpr)

    def on_function(self, function: Function):
        name = function.name.lexeme
        self.environment.define(name, LoxCallable(function, self.environment))

    def on_get(self, get: Get):
        lhs = self._evaluate(get.expr)

        if isinstance(lhs, LoxInstance):
            return lhs.get(get.name)
        else:
            raise LoxRuntimeError(get.name, 'Only instances have properties.')

    def on_call(self, call: Call):
        callee = self._evaluate(call.callee)

        args = []
        for arg in call.args:
            args.append(self._evaluate(arg))

        if not isinstance(callee, Callable):
            raise LoxRuntimeError(call.paren, 'Can only call functions or classes')

        if len(args) != callee.arity():
            raise LoxRuntimeError(call.paren, f'Expected {callee.arity()} arguments but got {len(args)}.')

        return callee.call(self, args)

    def on_while_loop(self, whileloop: WhileLoop):
        condition = whileloop.condition
        body = whileloop.body

        while self._evaluate(condition):
            body.perform_operation(self)

    def on_logical(self, logical: Logical):
        lhs = self._evaluate(logical.left)
        operator = logical.operator

        if operator.type == TT.AND:
            if lhs:
                return self._evaluate(logical.right)
            else:
                return lhs
        elif operator.type == TT.OR:
            if lhs:
                return lhs
            else:
                return self._evaluate(logical.right)
        else:
            raise LoxRuntimeError(operator, 'Unexpected token in place of logical operator')

    def on_if_else(self, ifelse: IfElse):
        condition_val = self._evaluate(ifelse.condition)

        if condition_val:
            then_stmt = ifelse.then_statement
            if then_stmt is not None:
                then_stmt.perform_operation(self)
        else:
            else_stmt = ifelse.else_statement
            if else_stmt is not None:
                else_stmt.perform_operation(self)

    def on_block(self, block: Block):
        parent_env = self.environment

        # Create new environment on entering Block.
        environment = Environment(parent_env)
        self.execute_block(block, environment)

    def execute_block(self, block, environment):
        parent_env = self.environment
        self.environment = environment

        try:
            statements = block.statements
            for statement in statements:
                statement.perform_operation(self)
        finally:
            # Set environment back to parent environment on leaving block.
            self.environment = parent_env

    def on_assign(self, assign: Assign):
        value = self._evaluate(assign.value)
        if assign in self.locals:
            depth = self.locals[assign]
            self.environment.assign_at(depth, assign.identifier, value)
        else:
            self.globals.assign(assign.identifier, value)

    def on_variable(self, variable: Variable):
        return self.lookup_variable(variable.name, variable)

    def on_var(self, var: Var):
        initializer_value = self._evaluate(var.initializer)
        self.environment.define(var.name.lexeme, initializer_value)


    def evaluate(self, statements: List[Stmt]):
        try:
            for statement in statements:
                statement.perform_operation(self)
        except LoxRuntimeError as e:
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
            raise LoxRuntimeError(binary.operator, f'Unexpected operand {operator}')

    def on_grouping(self, grouping: Grouping):
        return self._evaluate(grouping.expr)

    def on_literal(self, literal: Literal):
        return literal.value

    def on_unary(self, unary: Unary):
        operator = unary.operator.type
        expr_val = self._evaluate(unary.expr)

        if operator == TT.MINUS:
            if not isinstance(expr_val, float):
                raise LoxRuntimeError(unary.operator, 'Expected number for unary operator -.')
            return -expr_val
        elif operator == TT.BANG:
            return not expr_val
        else:
            raise LoxRuntimeError(unary.operator, f'Unexpected {operator}. Expected - or !')

    def on_print(self, printstmt):
        print(util.stringified(self._evaluate(printstmt.expr)))

    def on_expression(self, exprstmt):
        self._evaluate(exprstmt.expr)

    def on_set_prop(self, setprop: SetProp):
        object = self._evaluate(setprop.expr)

        if isinstance(object, LoxInstance):
            val = self._evaluate(setprop.value)
            object.set(setprop.name, val)
            return val
        else:
            raise LoxRuntimeError(setprop.name, 'Only instances have fields.')

    @staticmethod
    def check_number_operands(operator: Token, lhs, rhs):
        if (not isinstance(lhs, float)) and (not isinstance(rhs, float)):
            raise LoxRuntimeError(operator, f'Expected number operands for operator: {operator.lexeme}')

    @staticmethod
    def check_numorstring_operands(operator: Token, lhs, rhs):
        if isinstance(lhs, float) and isinstance(rhs, float):
            return

        if isinstance(lhs, str) and isinstance(rhs, str):
            return

        raise LoxRuntimeError(operator, f'Expected either only number or string operands for operator: {operator.lexeme}')














