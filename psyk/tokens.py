def math_operator(s: str):
    return f'THE {s} OF'


def logical_operator(s: str):
    return f'{s} OF'


def math_token(name: str):
    return f'MATH_{name}'


def logic_token(name: str):
    return f'LOGIC_{name}'


def math_nary(name: str):
    return f'{name} ALL OF'


NARY_OP = 'NARY_OP'
UNARY_OP = 'UNARY_OP'
BINARY_OP = 'BINARY_OP'


class Tokens:
    SCALAR_TYPE = 'SCALAR_TYPE'
    SCALAR_ARRAY_TYPE = 'SCALAR_ARRAY_TYPE'
    CHAR_LITERAL = 'CHAR_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    INT_LITERAL = 'INT_LITERAL'
    BOOL_LITERAL = 'BOOL_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'

    DECLARE = 'DECLARE'
    ASSIGN = 'ASSIGN'

    MATH_NARY_OP = math_token(NARY_OP)
    MATH_UNARY_OP = math_token(UNARY_OP)
    MATH_BINARY_OP = math_token(BINARY_OP)

    LOGIC_NARY_OP = logic_token(NARY_OP)
    LOGIC_UNARY_OP = logic_token(UNARY_OP)
    LOGIC_BINARY_OP = logic_token(BINARY_OP)

    COMPARE_BINARY_OP = 'COMPARE_BINARY_OP'

    COMMENT = 'COMMENT'
    QUESTION_MARK = 'QUESTION_MARK'

    # Flow Control
    IF = 'IF'
    ELSE = 'ELSE'
    CONTROL_FLOW_END = 'CONTROL_FLOW_END'
    WHILE = 'WHILE'
    BREAK = 'BREAK'
    FOR_EACH = 'FOR_EACH'
    LOOP_CONTINUATION = 'LOOP_CONTINUATION'

    # Arrays
    ARRAY_INDEX = 'ARRAY_INDEX'
    ARRAY_SIZE = 'ARRAY_SIZE'

    # Identity tokens
    AND = 'AND'
    AN = 'AN'
    AS = 'AS'
    A = 'A'
    BE = 'BE'
    BY = 'BY'
    INTO = 'INTO'
    MYSTERY = 'MYSTERY'
    OF = 'OF'
    OR = 'OR'
    SHOW = 'SHOW'
    SUMMONED = 'SUMMONED'
    REVEAL = 'REVEAL'
    THAN = 'THAN'
    THE = 'THE'
    TOGETHER = 'TOGETHER'
    WITH = 'WITH'

    # Other tokens
    IDENTIFIER = 'IDENTIFIER'
    EOC = 'EOC'

    ERROR = 'ERROR'

    # Virtual Tokens - these are strings that can be used to match tokens, but aren't tokens themselves
    MATH_ADD = math_operator('JOINING')
    MATH_SUB = math_operator('REDUCTION')
    MATH_MUL = math_operator('CROSS')
    MATH_DIV = math_operator('SPLIT')
    MATH_NEGATE = math_operator('NEGATION')
    MATH_MIN = math_operator('LESSER')
    MATH_MAX = math_operator('GREATER')
    MATH_INTEGER_DIV = math_operator('WHOLE SPLIT')
    MATH_INTEGER_MOD = math_operator('WHOLE SPLIT REMAINDER')

    LOGICAL_AND = logical_operator('BOTH')
    LOGICAL_OR = logical_operator('EITHER')
    LOGICAL_XOR = logical_operator('ONE')
    LOGICAL_NEGATE = logical_operator('THE OPPOSITE')
    LOGICAL_ALL_TRUE = logical_operator('THE ENTIRETY')
    LOGICAL_ANY_TRUE = logical_operator('SOME')

    COMPARE_EQUAL = 'SELFSAME'
    COMPARE_LESS_THAN = 'LESSER'
    COMPARE_GREATER_THAN = 'GREATER'

    MIN = math_operator('LESSER')
    MAX = math_operator('GREATER')

    PLURAL = 'S'


MATH_BINARY_OP_TO_JOIN_TOKEN = {
    Tokens.MATH_ADD:         Tokens.AND,
    Tokens.MATH_SUB:         Tokens.BY,
    Tokens.MATH_MUL:         Tokens.WITH,
    Tokens.MATH_DIV:         Tokens.INTO,
    Tokens.MATH_INTEGER_DIV: Tokens.INTO,
    Tokens.MATH_INTEGER_MOD: Tokens.INTO,
}

LOGIC_BINARY_OP_TO_JOIN_TOKEN = {
    Tokens.LOGICAL_AND: Tokens.AND,
    Tokens.LOGICAL_OR:  Tokens.OR,
    Tokens.LOGICAL_XOR: Tokens.OR,
}

COMPARE_BINARY_OP_TO_JOIN_TOKEN = {
    Tokens.COMPARE_EQUAL:        Tokens.AND,
    Tokens.COMPARE_LESS_THAN:    Tokens.THAN,
    Tokens.COMPARE_GREATER_THAN: Tokens.THAN
}

# Tokens whose pattern equals their name
IDENTITY_TOKENS = [
    Tokens.AND,
    Tokens.AN,
    Tokens.AS,
    Tokens.A,
    Tokens.BE,
    Tokens.BY,
    Tokens.INTO,
    Tokens.MYSTERY,
    Tokens.OF,
    Tokens.OR,
    Tokens.REVEAL,
    Tokens.SUMMONED,
    Tokens.SHOW,
    Tokens.THAN,
    Tokens.THE,
    Tokens.TOGETHER,
    Tokens.WITH,
]

TYPE_NAMES = [
    'GLYPH', 'NUMBER', 'REAL', 'TRUTH'
]
