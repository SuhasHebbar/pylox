#!/usr/bin/env python
import sys
from . import Lox

lox_interpreter = Lox()


def run_file(file_name):
    with open(file_name, 'r') as file:
        lox_interpreter.run(file.read())


def run_prompt():
    while True:
        print('> ', end='')
        lox_interpreter.run(input())


if len(sys.argv) > 2:
    print('Usage: plox [script]')
    sys.exit(64)
elif len(sys.argv) == 2:
    run_file(sys.argv[0])
else:
    run_prompt()
