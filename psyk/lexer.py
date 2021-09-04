import re

from psyk.rply_utils.lexer import Lexer
from psyk.tokens import Tokens, IDENTITY_TOKENS, TYPE_NAMES

ALLOWED_CHARS = r'(%(n|t|%|\')|[^\'])'

def build_lexer() -> Lexer:
    lexer = Lexer()

    lexer.add(Tokens.SCALAR_ARRAY_TYPE, rf'({"|".join(type_name + Tokens.PLURAL for type_name in TYPE_NAMES)})')
    lexer.add(Tokens.SCALAR_TYPE, rf'({"|".join(TYPE_NAMES)})')
    lexer.add(Tokens.CHAR_LITERAL, rf'\'{ALLOWED_CHARS}\'')
    lexer.add(Tokens.STRING_LITERAL, rf'"{ALLOWED_CHARS}*"')
    lexer.add(Tokens.FLOAT_LITERAL, r'-?\d+\.\d+')
    lexer.add(Tokens.INT_LITERAL, r'-?\d+')
    lexer.add(Tokens.BOOL_LITERAL, r'TRUE|FALSE')
    lexer.add(Tokens.DECLARE, r'NAME')
    lexer.add(Tokens.ASSIGN, r'MAKE')
    lexer.add(Tokens.MATH_NARY_OP, r'THE (JOINING|CROSS) OF ALL OF')
    lexer.add(Tokens.MATH_UNARY_OP, r'THE NEGATION OF')
    lexer.add(Tokens.MATH_BINARY_OP,
              r'THE (JOINING|REDUCTION|CROSS|SPLIT|LESSER|GREATER|WHOLE SPLIT|WHOLE SPLIT REMAINDER) OF')
    lexer.add(Tokens.LOGIC_UNARY_OP, r'THE OPPOSITE OF')
    lexer.add(Tokens.LOGIC_BINARY_OP, r'(BOTH|EITHER|ONE) OF')
    lexer.add(Tokens.LOGIC_NARY_OP, r'(THE ENTIRETY|SOME) OF')
    lexer.add(Tokens.COMPARE_BINARY_OP, r'(SELFSAME|LESSER|GREATER)')
    lexer.add(Tokens.QUESTION_MARK, r'[?]')
    lexer.add(Tokens.FOR_EACH, r'PLUCK EACH FROM')
    lexer.add(Tokens.LOOP_CONTINUATION, r':')
    lexer.add(Tokens.IF, r'SHOULD')
    lexer.add(Tokens.ELSE, r'LEST')
    lexer.add(Tokens.WHILE, r'WHILST')
    lexer.add(Tokens.BREAK, r'FLEE')
    lexer.add(Tokens.CONTROL_FLOW_END, r'SO IT IS')
    lexer.add(Tokens.ARRAY_SIZE, r'THE SIZE OF')

    for token in IDENTITY_TOKENS:
        lexer.add_identity(token)

    lexer.add(Tokens.IDENTIFIER, r'[a-zA-Z][a-zA-Z_]*')
    lexer.add(Tokens.EOC, r'[\.!]')

    lexer.add(Tokens.ARRAY_INDEX, r'\'')
    # lexer.add(Tokens.ERROR, r'.')

    lexer.ignore(r'\(.*?\)', re.DOTALL)  # comments
    lexer.ignore(r'[\s,]')  # whitespace

    return lexer
