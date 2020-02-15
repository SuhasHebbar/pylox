#!/usr/bin/env python
import sys
from pathlib import Path
from .lox import Lox

lox_interpreter = Lox()



def run_file(file_name):
    with open(file_name, 'r') as file:
        lox_interpreter.run(file.read())
        if lox_interpreter.had_error:
            sys.exit(65)


def run_prompt():
    import readline
    lox_history_filename = '.lox_history'
    lox_history_file = Path('.lox_history')

    if not lox_history_file.is_file():
        open(lox_history_file, 'w').close()

    readline.read_history_file('.lox_history')
    try:
        while True:
            print('> ', end='')
            lox_interpreter.run(input())
            lox_interpreter.had_error = False
    except (EOFError, KeyboardInterrupt) as e:
        print(f'\nShutting Down.\nReason: {repr(e)}')
    finally:
        readline.set_history_length(1000)
        readline.write_history_file('.lox_history')


if len(sys.argv) > 2:
    print('Usage: plox [script]')
    sys.exit(64)
elif len(sys.argv) == 2:
    run_file(sys.argv[1])
else:
    run_prompt()
