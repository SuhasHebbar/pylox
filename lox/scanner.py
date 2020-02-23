from typing import List, Optional

from .token import Token
from .token_type import TokenType as TT


class Scanner:
    def __init__(self, source: str, error_reporter):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.error_reporter = error_reporter

    def scan_tokens(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TT.EOF, None, None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        if c == '(':
            self.add_token(TT.LEFT_PAREN)
        elif c == ')':
            self.add_token(TT.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TT.LEFT_BRACE)
        elif c == '}':
            self.add_token(TT.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TT.COMMA)
        elif c == '.':
            self.add_token(TT.DOT)
        elif c == '-':
            self.add_token(TT.MINUS)
        elif c == '+':
            self.add_token(TT.PLUS)
        elif c == ';':
            self.add_token(TT.SEMICOLON)
        elif c == '*':
            self.add_token(TT.STAR)
        elif c == '/':
            if self.match('/'):
                while not (self.peek() == '\n' or self.at_end()):
                    self.advance()
            else:
                self.add_token(TT.SLASH)
        elif c == '!':
            if self.match('='):
                self.add_token(TT.BANG_EQUAL)
            else:
                self.add_token(TT.BANG)
        elif c == '=':
            if self.match('='):
                self.add_token(TT.EQUAL_EQUAL)
            else:
                self.add_token(TT.EQUAL)
        elif c == '>':
            if self.match('='):
                self.add_token(TT.GREATER_EQUAL)
            else:
                self.add_token(TT.GREATER)
        elif c == '<':
            if self.match('='):
                self.add_token(TT.LESS_EQUAL)
            else:
                self.add_token(TT.LESS)
        elif c.isnumeric():
            self.consume_digits()

            if self.match('.'):
                self.consume_digits()

            self.add_token(TT.NUMBER, float(self.get_lexeme()))
        elif c == '"':
            while (not self.at_end()) and self.peek() != '"':
                self.advance()
            self.current += 1
            self.add_token(TT.STRING, self.source[self.start + 1: self.current - 1])
        elif c.isalpha():
            while (not self.at_end()) and self.peek().isalnum():
                self.advance()

            lexeme = self.get_lexeme()
            if lexeme in keywords:
                self.add_token(keywords[lexeme])
            else:
                self.add_token(TT.IDENTIFIER)
        elif c == '\n':
            self.line += 1
        elif c in [' ', '\r', '\t']:
            pass
        else:
            self.error_reporter.error(self.line, f'Invalid character {c}.')

    def add_token(self, token: TT, literal = None):
        lexeme = self.get_lexeme()
        self.tokens.append(Token(token, lexeme, literal, self.line))

    def get_lexeme(self):
        return self.source[self.start: self.current]

    def consume_digits(self):
        while (peek := self.peek()) is not None and peek.isnumeric():
            self.advance()

    def peek(self) -> Optional[str]:
        if self.at_end():
            return None
        else:
            return self.source[self.current]

    def match(self, c: str):
        if self.at_end():
            return False

        if self.source[self.current] == c:
            self.current += 1
            return True
        else:
            return False

    def advance(self):
        if self.at_end():
            self.error_reporter.error(self.line, 'Currently past the end of string. No more characters to scan')

        self.current += 1
        return self.source[self.current - 1]

    def at_end(self):
        return self.current >= len(self.source)


keywords = {
    'and': TT.AND,
    'class': TT.CLASS,
    'else': TT.ELSE,
    'false': TT.FALSE,
    'fun': TT.FUN,
    'for': TT.FOR,
    'if': TT.IF,
    'nil': TT.NIL,
    'or': TT.OR,
    'print': TT.PRINT,
    'return': TT.RETURN,
    'super': TT.SUPER,
    'this': TT.THIS,
    'true': TT.TRUE,
    'var': TT.VAR,
    'while': TT.WHILE
}
