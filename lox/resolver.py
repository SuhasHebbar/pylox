from typing import Any, Dict, List

from lox.ast import StmtOperation, ExprOperation, Block, Stmt, Var, Expr, Variable, Assign, Function, Unary, Binary, \
    Grouping, Logical, Expression, Print, IfElse, WhileLoop, ReturnStmt, Call, ClassDecl, Get, SetProp, ThisExpr, \
    SuperExpr
from lox.interpreter import Interpreter
from lox.token import Token
from lox.util import FunctionKind, ClassType


class Resolver(ExprOperation, StmtOperation):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.error_reporter = interpreter.error_reporter
        self.scopes: List[Dict[str, bool]] = []
        self.current_function = FunctionKind.NONE
        self.current_class = ClassType.NONE

    def resolve_stmts(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, statement: Stmt):
        statement.perform_operation(self)

    def resolve_expr(self, expr: Expr):
        expr.perform_operation(self)

    def resolve_function(self, function: Function, kind: FunctionKind):
        enclosing_fun = self.current_function
        self.current_function = kind

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve_stmts(function.body.statements)
        self.end_scope()

        self.current_function = enclosing_fun

    def resolve_local(self, expr, token):
        for (i, scope) in enumerate(reversed(self.scopes)):
            if token.lexeme in scope:
                self.interpreter.resolve(expr, i)
                break

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) != 0:
            scope = self.scopes[-1]
            if name.lexeme in scope:
                self.error_reporter.parser_error(name, 'Variable with this name has already been declared in this scope.')
            scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) != 0:
            self.scopes[-1][name.lexeme] = True

    def on_this_expr(self, thisexpr: ThisExpr):
        if self.current_class is ClassType.NONE:
            self.error_reporter.parser_error(thisexpr.keyword, 'Cannot use \'this\' outside a class.')

        self.resolve_local(thisexpr, thisexpr.keyword)

    def on_get(self, get: Get):
        self.resolve_expr(get.expr)

    def on_set_prop(self, setprop: SetProp):
        self.resolve_expr(setprop.value)
        self.resolve_expr(setprop.expr)

    def on_class_decl(self, classdecl: ClassDecl):
        self.declare(classdecl.name)
        self.define(classdecl.name)

        if classdecl.superclass is not None:
            if classdecl.superclass.name.lexeme == classdecl.name.lexeme:
                self.error_reporter.parser_error(classdecl.superclass.name, 'A class cannot inherit from itself.')
            self.resolve_expr(classdecl.superclass)

            self.begin_scope()
            self.scopes[-1]['super'] = True


        self.begin_scope()

        self.current_class = ClassType.CLASS if classdecl.superclass is None else ClassType.SUBCLASS
        self.scopes[-1]['this'] = True

        for method in classdecl.methods:
            function_kind = FunctionKind.INITIALIZER if method.name.lexeme == 'init' else FunctionKind.METHOD
            self.resolve_function(method, function_kind)

        self.current_class = ClassType.NONE
        self.end_scope()
        if classdecl.superclass is not None:
            self.end_scope()

    def on_super_expr(self, superexpr: SuperExpr):
        if self.current_class is ClassType.NONE:
            self.error_reporter.parser_error(superexpr.keyword, 'Cannot use \'super\' outside class.')
        elif self.current_class is ClassType.CLASS:
            self.error_reporter.parser_error(superexpr.keyword, 'Cannot use \'super\' in a class with no superclass.')
        self.resolve_local(superexpr, superexpr.keyword)

    def on_literal(self, literal):
        pass

    def on_unary(self, unary: Unary):
        self.resolve_expr(unary.expr)

    def on_binary(self, binary: Binary):
        self.resolve_expr(binary.left)
        self.resolve_expr(binary.right)

    def on_grouping(self, grouping: Grouping):
        self.resolve_expr(grouping.expr)

    def on_variable(self, variable: Variable):
        lexeme = variable.name.lexeme
        if len(self.scopes) != 0:
            scope = self.scopes[-1]
            if lexeme in scope and scope[lexeme] == False:
                self.error_reporter.parser_error(variable.name, 'Cannot read local variable in its own initializer.')

        self.resolve_local(variable, variable.name)

    def on_assign(self, assign: Assign):
        self.resolve_expr(assign.value)
        self.resolve_local(assign, assign.identifier)

    def on_logical(self, logical: Logical):
        self.resolve_expr(logical.left)
        self.resolve_expr(logical.right)

    def on_call(self, call: Call):
        self.resolve_expr(call.callee)
        for arg in call.args:
            self.resolve_expr(arg)

    def on_expression(self, expression: Expression):
        self.resolve_expr(expression.expr)

    def on_print(self, print: Print):
        self.resolve_expr(print.expr)

    def on_var(self, var: Var):
        self.declare(var.name)

        if var.initializer is not None:
            self.resolve_expr(var.initializer)

        self.define(var.name)

    def on_block(self, block: Block):
        self.begin_scope()
        self.resolve_stmts(block.statements)
        self.end_scope()

    def on_function(self, function: Function):
        self.declare(function.name)
        self.define(function.name)

        self.resolve_function(function, FunctionKind.FUNCTION)

    def on_if_else(self, ifelse: IfElse):
        self.resolve_expr(ifelse.condition)
        self.resolve_stmt(ifelse.then_statement)
        self.resolve_stmt(ifelse.else_statement)

    def on_while_loop(self, whileloop: WhileLoop):
        self.resolve_expr(whileloop.condition)
        self.resolve_stmt(whileloop.body)

    def on_return_stmt(self, returnstmt: ReturnStmt):
        if self.current_function is FunctionKind.NONE:
            self.error_reporter.parser_error(returnstmt.keyword, 'Cannot return from top-level code.')

        if returnstmt.value is not None:
            if self.current_function is FunctionKind.INITIALIZER:
                self.error_reporter.parser_error(returnstmt.keyword, 'Cannot return a value from an initializer.')
            self.resolve_expr(returnstmt.value)

