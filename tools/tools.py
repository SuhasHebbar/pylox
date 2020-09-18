import re
import sys
from pathlib import Path
from typing import List, Sized

expr_template = [
    'Literal | value: Any',
    'Unary | operator: Token, expr: Expr',
    'Binary | operator: Token, left: Expr, right: Expr',
    'Grouping | expr: Expr',
    'Variable | name: Token',
    'Assign | identifier: Token, value: Expr',
    'Logical | operator: Token, left: Expr, right: Expr',
    'Call | callee: Expr, paren: Token, args: List[Expr]',
    'Get | expr: Expr, name: Token',
    'SetProp | expr: Expr, name: Token, value: Expr',
    'ThisExpr | keyword: Token',
    'SuperExpr | keyword: Token, method: Token'
]

stmt_template = [
    'Expression | expr: Expr',
    'Print | expr: Expr',
    'Var | name: Token, initializer: Optional[Expr]',
    'Block | statements: List[Stmt]',
    'Function | name: Token, params: List[Token], body: Block',
    'IfElse | condition: Expr, then_statement: Stmt, else_statement: Stmt',
    "WhileLoop | condition: Expr, body: Stmt",
    'ReturnStmt | keyword: Token, value: Optional[Expr]',
    'ClassDecl | name: Token, superclass: Optional[Variable], methods: List[Function]'
]

camelCase_to_snake_case_regex = re.compile(r'(?<!^)(?=[A-Z])')


def main(argv):

    # Assumes that the generate AST script is called as `python {script_name} {file_name}`
    if len(argv) != 2:
        print('Usage: python {script_name} {file_name})', file=sys.stderr)
        sys.exit(1)

    with open(argv[1], 'w') as ofile:
        ast = '''from abc import ABC, abstractmethod
from typing import Any, List, Optional
from lox.token import Token
'''
        ast += '\n\n'
        ast += generate_ast_types('Expr', expr_template)
        ast += generate_ast_types('Stmt', stmt_template)
        ofile.write(ast)



def generate_ast_types(parent_class, templates: List[str]) -> str:
    parent_class_declaration = f'''
class {parent_class}(ABC):
    @abstractmethod
    def perform_operation(self, operation: {parent_class}Operation):
        pass


'''

    ast = parent_class_declaration
    class_list = []
    for template in templates:
        class_, *init_arguments_list = map(lambda x: x.strip(' '), template.split('|'))
        class_list.append(class_)
        assert len(init_arguments_list) == 1
        init_arguments = init_arguments_list[0]
        class_template = ''
        class_template += f'class {class_}({parent_class}):\n'
        class_template += f'    def __init__(self, {init_arguments}):\n'
        attributes = map(lambda x: x.split(': '), init_arguments.split(', '))
        for attr_name, *_ in attributes:
            class_template += f'        self.{attr_name} = {attr_name}\n'

        class_template += '\n'
        class_template += f'''    def perform_operation(self, operation: {parent_class}Operation):
        return operation.on_{camelCase_to_snake_case(class_)}(self)
'''
        ast += class_template
        ast += '\n\n'

    ast_pre = f'class {parent_class}Operation(ABC):\n'
    for class_ in class_list:
        ast_pre += f'   @abstractmethod\n'
        ast_pre += f'   def on_{camelCase_to_snake_case(class_)}(self, {class_.lower()}: \'{class_}\'):\n'
        ast_pre += f'       pass\n\n'
    ast_pre += ast

    return ast_pre


def camelCase_to_snake_case(name: str):
    return camelCase_to_snake_case_regex.sub('_', name).lower()


if __name__ == '__main__':
    main(sys.argv)
