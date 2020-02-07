class Lox:
    def run(self, code: str):
        scanner = Scanner(code)
        scanner.scan_tokens()


class Scanner:
    def __init__(self, source: str):
        self.source = source

    def scan_tokens(self):
        pass
