from .interpreter import Interpreter
from .parser import Parser
from .resolver import Resolver
from .scanner import Scanner
from .token import Token
from .token_type import TokenType as TT
from .util import LoxRuntimeError


class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run(self, code: str):
        scanner = Scanner(code, self)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens, self)
        statements = parser.parse()

        resolver = Resolver(self.interpreter)
        resolver.resolve_stmts(statements)

        if self.had_error or statements is None:
            return
        else:
            self.interpreter.evaluate(statements)

    def error(self, line: int, message: str):
        self.report(line, '', message)

    def parser_error(self, token: Token, msg: str):
        if token.type == TT.EOF:
            self.report(token.line, ' at End', msg)
        else:
            self.report(token.line, f' at \'{token.lexeme}\'', msg)

    def runtime_error(self, runtime_error: LoxRuntimeError):
        print(f'{repr(runtime_error)} \n[line: {runtime_error.token.line}]')
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str):
        print(f'[line: {line}] Error{where}: {message}')
        self.had_error = True






