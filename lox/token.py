from .token_type import TokenType


class Token:
    def __init__(self, type: TokenType, lexeme, literal, line):
        self.line = line
        self.literal = literal
        self.lexeme = lexeme
        self.type = type

    def __str__(self):
        return f'type: {self.type}, lexeme: {self.lexeme}, line: {self.line}'
