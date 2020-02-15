from .scanner import Scanner

class Lox:
    def __init__(self):
        self.had_error = False

    def run(self, code: str):
        scanner = Scanner(code)
        try:
            tokens = scanner.scan_tokens()
        except Exception as e:
            self.error(scanner.line, repr(e))
            tokens = []

        for token in tokens:
            print(token)


    def error(self, line: int, message: str):
        self.report(line, '', message)

    def report(self, line: int, where: str, message: str):
        print(f'[line: {line}] Error{where}: {message}')
        self.had_error = True






