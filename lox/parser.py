import sys
from typing import List

from .ast import Binary, Expr, Unary, Literal, Grouping, Print, Expression, Var, Variable, Assign, Block, Stmt, IfElse, \
    Logical, WhileLoop
from .token import Token
from .token_type import TokenType as TT


class Parser:
    class ParseError(Exception):
        def __init__(self, msg: str):
            super(Exception, self).__init__(msg)

    def __init__(self, tokens: List[Token], error_reporter):
        self.tokens = tokens
        self.curr = 0
        self.error_reporter = error_reporter

    def parse(self):
        if len(self.tokens) <= 1:
            return None

        try:
            statements = []
            while not self.at_end():
                statements.append(self.declaration())
            return statements
        except self.ParseError:
            return None
        except Exception as e:
            print(f'There seems to be a problem. {repr(e)}', sys.stderr)

    def at_end(self):
        return self.curr >= len(self.tokens) or self.tokens[self.curr].type == TT.EOF

    def peek(self):
        return self.tokens[self.curr]

    def match(self, *types: TT):
        for type in types:
            if self.check(type):
                self.advance()
                return True

    def check(self, type: TT):
        return not self.at_end() and self.peek().type == type

    def advance(self):
        if self.at_end():
            return None
        else:
            self.curr += 1
            return self.tokens[self.curr - 1]

    def previous(self):
        return self.tokens[self.curr - 1]

    def statement(self) -> Stmt:
        if self.match(TT.PRINT):
            return self.print_statement()
        elif self.match(TT.LEFT_BRACE):
            return self.block()
        elif self.match(TT.IF):
            return self.ifelse_statement()
        elif self.match(TT.WHILE):
            return self.while_statement()
        elif self.match(TT.FOR):
            return self.for_statement()
        else:
            return self.expr_statement()

    def print_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TT.SEMICOLON, 'Expected semicolon at end of statement.')
        return Print(expr)

    def expr_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TT.SEMICOLON, 'Expected semicolon at end of statement.')
        return Expression(expr)


    def for_statement(self):
        self.consume(TT.LEFT_PAREN, 'Expected opening parenthesis for for loop.')
        initializer = None
        if self.match(TT.VAR):
            initializer = self.var_declaration()
        elif not self.match(TT.SEMICOLON):
            initializer = self.expr_statement()

        condition = Literal(True)

        if not self.match(TT.SEMICOLON):
            condition = self.expr_statement().expr

        post_body_expr = None
        if not self.check(TT.RIGHT_PAREN):
            post_body_expr = self.expression()

        self.consume(TT.RIGHT_PAREN, 'Expected closing parenthesis for for loop.')

        body = self.statement()
        body = Block([body, Expression(post_body_expr)])

        while_loop = WhileLoop(condition, body)

        return Block([initializer, while_loop])

    def while_statement(self):
        self.consume(TT.LEFT_PAREN, 'Expected opening parenthesis for while loop.')
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, 'Expected closing parenthesis for while loop.')

        body = self.statement()
        return WhileLoop(condition, body)

    def ifelse_statement(self):
        self.consume(TT.LEFT_PAREN, 'Expected opening parenthesis for conditional.')
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, 'Expected closing parenthesis for conditional.')

        then_statement = self.statement()
        else_statement = None

        if self.match(TT.ELSE):
            else_statement = self.statement()

        return IfElse(condition, then_statement, else_statement)

    def declaration(self) -> Stmt:
        try:
            if self.match(TT.VAR):
                return self.var_declaration()
            else:
                return self.statement()
        except Parser.ParseError as e:
            self.synchronize()
            return None

    def block(self) -> Block:
        statements = []
        while not self.check(TT.RIGHT_BRACE) and not self.at_end():
            statements.append(self.declaration())

        self.consume(TT.RIGHT_BRACE, 'Expected "}" at end of block')
        return Block(statements)

    def var_declaration(self) -> Var:
        token = self.consume(TT.IDENTIFIER, 'Expected variable name.')
        initializer = None

        if self.match(TT.EQUAL):
            initializer = self.expression()

        self.consume(TT.SEMICOLON, 'Expected semicolon at end of statement')
        return Var(token, initializer)

    def expression(self) -> Expr:
        return self.assign()

    def assign(self) -> Expr:
        expr = self.or_()
        if self.match(TT.EQUAL):
            if type(expr) is Variable:
                assignment_expr = self.expression()
                return Assign(expr.name, assignment_expr)
            else:
                raise self.error(self.previous(), 'Invalid assignment target')
        else:
            return expr

    def or_(self) -> Expr:
        expr = self.and_()

        while self.match(TT.OR):
            operator = self.previous()
            rhs = self.and_()
            expr = Logical(operator, expr, rhs)

        return expr

    def and_(self) -> Expr:
        expr = self.equality()

        while self.match(TT.AND):
            operator = self.previous()
            rhs = self.equality()
            expr = Logical(operator, expr, rhs)

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = self.previous()
            rhs = self.comparison()
            expr = Binary(operator, expr, rhs)

        return expr

    def comparison(self) -> Expr:
        expr = self.addition()

        while self.match(TT.GREATER_EQUAL, TT.GREATER, TT.LESS_EQUAL, TT.LESS):
            operator = self.previous()
            rhs = self.addition()
            expr = Binary(operator, expr, rhs)

        return expr

    def addition(self) -> Expr:
        expr = self.multiplication()

        while self.match(TT.PLUS, TT.MINUS):
            operator = self.previous()
            rhs = self.multiplication()
            expr = Binary(operator, expr, rhs)

        return expr

    def multiplication(self) -> Expr:
        expr = self.unary()

        while self.match(TT.STAR, TT.SLASH):
            operator = self.previous()
            rhs = self.unary()
            expr = Binary(operator, expr, rhs)

        return expr

    def unary(self) -> Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            rhs = self.unary()
            return Unary(operator, rhs)
        else:
            return self.primary()

    def primary(self) -> Expr:
        if self.match(TT.FALSE):
            return Literal(False)
        elif self.match(TT.TRUE):
            return Literal(True)
        elif self.match(TT.NIL):
            return Literal(None)
        elif self.match(TT.NUMBER, TT.STRING):
            return Literal(self.previous().literal)
        elif self.match(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, 'Expected \')\'')
            return Grouping(expr)
        elif self.match(TT.IDENTIFIER):
            return Variable(self.previous())
        else:
            raise self.error(self.peek(), 'Expected Literal/Grouping.')

    def consume(self, type: TT, error_msg: str):
        if self.match(type):
            return self.previous()
        else:
            raise self.error(self.peek(), error_msg)

    def error(self, token: TT, msg: str):
        self.error_reporter.parser_error(token, msg)
        return Parser.ParseError(msg)

    def synchronize(self):
        self.advance()

        while not self.at_end():
            if self.previous().type == TT.EOF:
                return

            bndry_tokens = [
                TT.CLASS,
                TT.FUN,
                TT.FOR,
                TT.VAR,
                TT.IF,
                TT.WHILE,
                TT.PRINT,
                TT.RETURN
            ]
            if self.peek().type in bndry_tokens:
                return
            else:
                self.advance()


