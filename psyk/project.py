from typing import Iterable

from psyk.context import CompilerContext
from psyk.ast_nodes import ASTNode
from psyk.intermediate_output import IntermediateOutput
from psyk.symbol_table import CompilerSymbolTable
from psyk.lexer import build_lexer
from psyk.parser import build_parser
from psyk.rply import Token


def lex_psyk(code: str) -> Iterable[Token]:
    """
    :param code: a string containing (possibly invalid) Psyk source code
    :return: a list (or generator) of RPLY Tokens created from the source code
    """
    return build_lexer().lex(code)


def parse_psyk(code: str) -> ASTNode:
    lexer = build_lexer()
    tokens = lexer.lex(code)
    parser = build_parser(lexer.possible_tokens)
    return parser.parse(tokens, code)


def psyk_to_intermediate(code: str):
    ast_root = parse_psyk(code)
    symbol_table = CompilerSymbolTable()
    output = IntermediateOutput(symbol_table)
    ast_root.compile(CompilerContext(symbol_table, output))
    return output.serialize()
