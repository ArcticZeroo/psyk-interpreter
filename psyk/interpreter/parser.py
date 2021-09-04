from .errors import ParsingError
from .ast_nodes import *
from ..rply import ParserGenerator
from ..rply import Token


def parse_intermediate(tokens, possible_tokens, code=None, debug=False):
    """
    Here we're going to take our input token stream and try to parse it:
    that is to say we're going to try to build a tree from the bottom
    up from our input token stream using (behind the scenes) a pushdown
    automata.
    """

    pg = ParserGenerator(possible_tokens)

    # If there is an error parsing, this function gets executed
    @pg.error
    def error_handler(p):
        raise ParsingError(f'There was a problem parsing {p}')

    @pg.production('start : command_list')
    def start(p):
        children = p[0]
        return CommandListNode(children)

    @pg.production('command_list : command EOC command_list')
    def commands_many_one_or_more(p):
        to_return = p[0] + p[2]
        return to_return

    @pg.production('command_list : ')
    def commands_many_none(p):
        return []

    @pg.production('command : statement')
    @pg.production('command : ')
    def command(p):
        return [p[0]] if len(p) > 0 else []

    @pg.production('number_int : INT')
    @pg.production('number_int : SVAR')
    def number_int(p):
        return p[0].value

    @pg.production('number : number_int')
    @pg.production('number : FLOAT')
    def number(p):
        return p[0].value if isinstance(p[0], Token) else p[0]

    @pg.production('scalar : number')
    @pg.production('scalar : CHAR')
    def value_or_svar(p):
        return p[0].value if isinstance(p[0], Token) else p[0]

    @pg.production('statement : VAL_COPY scalar SVAR')
    @pg.production('statement : VAL_COPY scalar AVAR')
    @pg.production('statement : VAL_COPY AVAR AVAR')
    def val_copy(p):
        if isinstance(p[1], Token):
            p[1] = p[1].value
        children = [p[1], p[2].value]
        return ValCopyNode(children)

    @pg.production('statement : OUT_NUM INT')
    @pg.production('statement : OUT_NUM FLOAT')
    @pg.production('statement : OUT_NUM SVAR')
    def print_num(p):
        children = [p[1].value]
        return PrintNumNode(children)

    @pg.production('statement : OUT_CHAR CHAR')
    @pg.production('statement : OUT_CHAR SVAR')
    def print_char(p):
        children = [p[1].value]
        return PrintCharNode(children)

    @pg.production('statement : IN_CHAR SVAR')
    def in_char(p):
        children = [p[1].value]
        return InputCharNode(children)

    @pg.production('statement : ADD number number SVAR')
    @pg.production('statement : SUB number number SVAR')
    @pg.production('statement : MUL number number SVAR')
    @pg.production('statement : DIV number number SVAR')
    @pg.production('statement : IDIV number number SVAR')
    @pg.production('statement : MOD number number SVAR')
    def binary_expr(p):
        children = [p[0].value, p[1], p[2], p[3].value]
        return MathBinaryOpNode(children)

    @pg.production('statement : TEST_LESS number number SVAR')
    @pg.production('statement : TEST_GTR number number SVAR')
    @pg.production('statement : TEST_EQU number number SVAR')
    @pg.production('statement : TEST_NEQU number number SVAR')
    def bin_compare(p):
        children = [p[0].value, p[1], p[2], p[3].value]
        return CompareBinaryOpNode(children)

    @pg.production('statement : JUMP LABEL_USE')
    def uncond_jump(p):
        children = [p[1].value]
        return JumpUncondNode(children)

    @pg.production('statement : JUMP_IF_0 SVAR LABEL_USE')
    @pg.production('statement : JUMP_IF_NE0 SVAR LABEL_USE')
    def cond_jump(p):
        children = [p[0].value, p[1].value, p[2].value]
        return JumpCondNode(children)

    @pg.production('statement : RANDOM SVAR')
    def random(p):
        children = [p[1].value]
        return InputMysteryNode(children)

    @pg.production('statement : PUSH scalar')
    @pg.production('statement : PUSH AVAR')
    def push(p):
        raise NotImplementedError('PUSH is not implemented.')

    @pg.production('statement : POP SVAR')
    @pg.production('statement : POP AVAR')
    def pop(p):
        raise NotImplementedError('POP is not implemented.')

    @pg.production('statement : AR_GET_NDX AVAR number_int SVAR')
    def get_array_ndx(p):
        children = [p[1].value, p[2], p[3].value]
        return ArrayGetNdx(children)

    @pg.production('statement : AR_SET_NDX AVAR number_int number')
    def set_array_ndx(p):
        children = [p[1].value, p[2], p[3]]
        return ArraySetNdx(children)

    @pg.production('statement : AR_GET_SZ AVAR SVAR')
    def get_array_size(p):
        children = [p[1].value, p[2].value]
        return ArrayGetSize(children)

    @pg.production('statement : AR_SET_SZ AVAR number_int')
    def set_array_size(p):
        children = [p[1].value, p[2]]
        return ArraySetSize(children)

    @pg.production('statement : AR_COPY AVAR AVAR')
    def array_copy(p):
        children = [p[1].value, p[2].value]
        return ArrayCopy(children)

    @pg.production('statement : LABEL_MARK')
    def label_mark(*_):
        pass

    parser = pg.build()  # Build the parser from the ParserGenerator
    return parser.parse(iter(tokens))  # Actually do the parse
