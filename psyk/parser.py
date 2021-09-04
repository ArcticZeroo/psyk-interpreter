from typing import Iterable, Dict, Mapping, Type, List

import psyk.ast_nodes as ast_nodes
import psyk.type_system as type_system
from psyk.intermediate_output import TOKEN_TO_OPERATION
from psyk.rply import Token
from psyk.rply_utils.exceptions import ParsingException
from psyk.rply_utils.parser import Parser
from psyk.tokens import Tokens, MATH_BINARY_OP_TO_JOIN_TOKEN, LOGIC_BINARY_OP_TO_JOIN_TOKEN, \
    COMPARE_BINARY_OP_TO_JOIN_TOKEN, UNARY_OP, BINARY_OP, NARY_OP


def return_tokens(tokens):
    return tokens


def define_optional(parser: Parser, name: str, token: str):
    parser.empty_production(name)
    parser.empty_production(f'{name} : {token}')


def return_token_name(tokens: Mapping[int, Token]):
    return tokens[0].name


def register_operator_joins(parser: Parser, source: Dict[str, str], name: str):
    for join_operator_token in set(source.values()):
        parser.production(f'{name} : {join_operator_token}')(return_token_name)


def verify_operator_join(source: Dict[str, str], operation: Token, operator_join: str):
    expected_join_operator = source.get(operation.value) or source.get(Tokens.ERROR) or Tokens.AND
    if operator_join != expected_join_operator:
        raise ParsingException(f'Join operator {operator_join} was expected to be {expected_join_operator}')


def build_parser_program(parser: Parser):
    @parser.production('program_command_list : program')
    def start_program(children):
        (program,) = children
        return ast_nodes.CommandList(program)

    @parser.production('program : ')
    def program_empty(*_):
        return []

    @parser.production('program : command')
    def program_single_command(children):
        (command,) = children
        # command can be empty due to the EOC requirement
        if command is None:
            return []
        return [command]

    @parser.production(f'program : program command')
    def program_list(children):
        (program, command) = children
        return (program
                if command is None
                else program + [command])

    @parser.production(f'command : statement {Tokens.EOC}')
    @parser.production(f'command : expr {Tokens.EOC}')
    def command_statement_or_expr(children):
        (statement_or_expr, _) = children
        return statement_or_expr

    parser.empty_production(f'command : {Tokens.EOC}')


def build_parser_assignment(parser: Parser):
    @parser.production(f'statement : {Tokens.DECLARE} {Tokens.A} type {Tokens.AS} identifier',
                       precedence=Tokens.SCALAR_TYPE)
    def statement_declare_without_assign(children):
        (_, _, type_data, _, identifier) = children
        return ast_nodes.ExprDeclaration((identifier, type_data, None))

    @parser.production(f'statement : {Tokens.DECLARE} {Tokens.A} type expr {Tokens.AS} identifier',
                       precedence=Tokens.SCALAR_TYPE)
    def statement_declare_with_assign(children):
        (_, _, type_name, value_expr, _, identifier) = children
        return ast_nodes.ExprDeclaration((identifier, type_name, value_expr))

    @parser.production(f'statement : {Tokens.DECLARE} expr array_type {Tokens.AS} identifier',
                       precedence=Tokens.SCALAR_ARRAY_TYPE)
    def statement_declare_array_without_assign(children):
        (_, size_expr, array_type_token, _, identifier) = children
        return ast_nodes.ExprArrayDeclaration((identifier, array_type_token, None, size_expr))

    @parser.production(f'statement : {Tokens.DECLARE} expr array_type expr_list {Tokens.AS} identifier',
                       precedence=Tokens.SCALAR_ARRAY_TYPE)
    def statement_declare_array_with_assign(children):
        (_, size_expr, array_type_token, initial_value_expr_list, _, identifier) = children
        return ast_nodes.ExprArrayDeclaration((identifier, array_type_token, initial_value_expr_list, size_expr))

    @parser.production(f'expr :  {Tokens.ASSIGN} identifier {Tokens.BE} expr')
    def expr_assignment(children):
        (_, identifier_name, _, value_expr) = children
        return ast_nodes.ExprAssignment((identifier_name, value_expr))


def build_parser_math_or_logic(parser: Parser, operator_to_join_map: Dict[str, str], name: str):
    name_upper = name.upper()
    name_lower = name.lower()
    name_camel = name.capitalize()

    def token(suffix: str):
        return f'{name_upper}_{suffix}'

    def node_class(suffix: str) -> Type[ast_nodes.Expr]:
        return getattr(ast_nodes, f'Expr{name_camel}{suffix.capitalize()}')

    operator_join_name = f'{name_lower}_operator_join'

    expr_unary_class = node_class('Unary')
    expr_binary_class = node_class('Binary')
    expr_nary_class = node_class('Nary')

    @parser.production(f'expr : {token(UNARY_OP)} expr')
    def expr_unary(children):
        (operation, expr) = children
        return expr_unary_class((TOKEN_TO_OPERATION[operation.value], expr))

    @parser.production(f'expr : {token(BINARY_OP)} expr {operator_join_name} expr')
    def expr_binary(children):
        (operation, left_expr, join_operator_str, right_expr) = children
        verify_operator_join(operator_to_join_map, operation, join_operator_str)
        return expr_binary_class((left_expr, TOKEN_TO_OPERATION[operation.value], right_expr))

    @parser.production(f'expr : {token(NARY_OP)} expr_list {Tokens.TOGETHER}')
    def expr_nary(children):
        (operation, expr_list, _) = children
        return expr_nary_class((TOKEN_TO_OPERATION[operation.value], expr_list))

    register_operator_joins(parser, operator_to_join_map, operator_join_name)


def build_parser_math(parser: Parser):
    build_parser_math_or_logic(parser, MATH_BINARY_OP_TO_JOIN_TOKEN, 'math')


def build_parser_logic(parser: Parser):
    build_parser_math_or_logic(parser, LOGIC_BINARY_OP_TO_JOIN_TOKEN, 'logic')


def build_parser_compare(parser: Parser):
    @parser.production(f'expr : {Tokens.COMPARE_BINARY_OP} expr compare_operator_join expr')
    def expr_compare(children):
        (operation, left_expr, join_operator_str, right_expr) = children
        verify_operator_join(COMPARE_BINARY_OP_TO_JOIN_TOKEN, operation, join_operator_str)
        return ast_nodes.ExprCompareBinary((left_expr, TOKEN_TO_OPERATION[operation.value], right_expr))

    register_operator_joins(parser, COMPARE_BINARY_OP_TO_JOIN_TOKEN, 'compare_operator_join')


def build_parser_io(parser: Parser):
    @parser.production(f'expr : {Tokens.SUMMONED}')
    def expr_summon(*_):
        return ast_nodes.ExprReadInput()

    @parser.production(f'expr : {Tokens.MYSTERY}')
    def expr_mystery(*_):
        return ast_nodes.ExprMystery()

    @parser.production(f'expr : {Tokens.SHOW} expr_list')
    @parser.production(f'expr : {Tokens.REVEAL} expr_list')
    def expr_print(children):
        (print_type_token, expr_list) = children
        if print_type_token.name == Tokens.SHOW:
            return ast_nodes.StatementPrint((expr_list,))
        return ast_nodes.StatementPrintWithNewline((expr_list,))


def build_parser_control_flow(parser: Parser):
    @parser.production(f'condition : expr {Tokens.QUESTION_MARK}')
    def condition(children):
        (condition_expr, _) = children
        return ast_nodes.ExprCondition((condition_expr,))

    @parser.production(f'statement : {Tokens.IF} condition program_command_list {Tokens.CONTROL_FLOW_END}')
    def if_statement(children):
        (_, condition_expr, if_body, _) = children
        return ast_nodes.StatementIfElse((condition_expr, if_body, None))

    @parser.production(
        f'statement : {Tokens.IF} condition program_command_list {Tokens.ELSE} program_command_list {Tokens.CONTROL_FLOW_END}')
    def if_else_statement(children):
        (_, condition_expr, if_body, _, else_body, _) = children
        return ast_nodes.StatementIfElse((condition_expr, if_body, else_body))

    @parser.production(f'statement : {Tokens.WHILE} condition program_command_list {Tokens.CONTROL_FLOW_END}')
    def while_loop_statement(children):
        (_, condition_expr, body, _) = children
        return ast_nodes.StatementWhile((condition_expr, body))

    @parser.production(f'statement : {Tokens.BREAK}')
    def while_loop_break_statement(children):
        return ast_nodes.StatementBreak()

    @parser.production(f'statement : {Tokens.FOR_EACH} expr {Tokens.AS} identifier {Tokens.LOOP_CONTINUATION} program_command_list {Tokens.CONTROL_FLOW_END}')
    def for_each_statement(children):
        (_, iterable_expr, _, identifier_expr, _, body, _) = children
        return ast_nodes.StatementForEach((iterable_expr, identifier_expr, body))


def build_parser_arrays(parser: Parser):
    @parser.production(f'expr : {Tokens.ARRAY_SIZE} identifier')
    def expr_array_size(children):
        (_, array_expr) = children
        return ast_nodes.ExprArraySize((array_expr,))


def build_parser_types(parser: Parser):
    @parser.production(f'expr : scalar_literal')
    def expr_scalar_literal(children):
        (value,) = children
        return value

    @parser.production(f'scalar_literal : {Tokens.INT_LITERAL}')
    @parser.production(f'scalar_literal : {Tokens.FLOAT_LITERAL}')
    @parser.production(f'scalar_literal : {Tokens.CHAR_LITERAL}')
    @parser.production(f'scalar_literal : {Tokens.BOOL_LITERAL}')
    def expr_scalar_literal(children):
        (token,) = children
        scalar_type_data = type_system.from_scalar_type_name(token.name)
        return ast_nodes.ExprLiteral((token.value, scalar_type_data))

    @parser.production(f'expr : identifier')
    def expr_identifier(children):
        (value,) = children
        return value

    define_optional(parser, 'optional_and', Tokens.AND)

    @parser.production(f'expr_list : expr optional_and expr_list')
    def expr_list_continuation(children):
        (current_element, _, rest_of_list) = children
        return [current_element] + rest_of_list

    @parser.production(f'expr_list : expr')
    def expr_list_one(children):
        (current_element,) = children
        return [current_element]

    @parser.production(f'type : {Tokens.SCALAR_TYPE}')
    @parser.production(f'array_type : {Tokens.SCALAR_ARRAY_TYPE}')
    def scalar_type_name(children):
        (token,) = children
        return type_system.from_scalar_type_name(token.value)

    @parser.production(f'identifier : {Tokens.THE} {Tokens.IDENTIFIER}')
    def identifier(children):
        (_, identifier_token) = children
        return ast_nodes.ExprIdentifier((identifier_token.value,))

    @parser.production(f'identifier : {Tokens.THE} {Tokens.IDENTIFIER} {Tokens.ARRAY_INDEX} expr')
    def identifier_array_index(children):
        (_, identifier_token, _, index_expr) = children
        return ast_nodes.ExprArrayIndexIdentifier((identifier_token.value, index_expr))


def build_parser(possible_tokens: Iterable[str]) -> Parser:
    parser = Parser(possible_tokens, [
        ('left', [Tokens.EOC, Tokens.AND]),
        ('left', [Tokens.SCALAR_TYPE, Tokens.IDENTIFIER]),
        ('left', [Tokens.SCALAR_ARRAY_TYPE, Tokens.ARRAY_INDEX]),
    ])

    parser_builders = [
        build_parser_program, build_parser_assignment, build_parser_math, build_parser_logic, build_parser_compare,
        build_parser_io, build_parser_control_flow, build_parser_arrays, build_parser_types
    ]

    for parser_builder in parser_builders:
        parser_builder(parser)

    return parser
