from psyk.project import lex_psyk
from psyk.rply import Token
import unittest

"""
Remember that unittest test cases have to begin with test_
"""


class TestLexer(unittest.TestCase):
    """
    Project1 starter test case
    """

    def test_starter(self):
        code = """
        NAME A NUMBER THE foo.
        MAKE THE foo BE 3.
        REVEAL THE FOO!
        (0 should be printed with a newline to stdout.)
        (But not right now
         ...that comes later)
        """
        expected = []

        tokens, possible_tokens = lex_psyk(code)
        # print(tokens)


class Project1Tests(unittest.TestCase):
    """
    Mimir test cases
    """

    def check_enumerate(self, expected, tokens):
        for ndx, t in enumerate(expected):
            tkn = tokens[ndx]
            if (t != tkn):
                print(t, tkn)

    def test_empty(self):
        code = ''
        expected = []
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

    def test_delimiters(self):
        code = ' '
        expected = []
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

        code = ','
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

        code = '\n'
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

        code = '\t'
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

        code = ',,\n '
        tokens, possible_tokens = lex_psyk(code)
        assert expected == tokens

    def test_stmnt_empty(self):
        code = """
        .
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('EOC', '.')]
        assert expected == tokens

    def test_decl_number_noinit(self):
        code = """
        NAME A NUMBER AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'NUMBER'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.')]
        assert expected == tokens

    def test_decl_number_init(self):
        code = """
        NAME A NUMBER 3 AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'NUMBER'),
                    Token('INT_LITERAL', '3'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.')]
        assert expected == tokens

    def test_decl_float_noinit(self):
        code = """
        NAME A REAL AS THE real.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'REAL'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'real'),
                    Token('EOC', '.')]
        assert expected == tokens


    def test_decl_float_noinit_bang(self):
        code = """
        NAME A REAL AS THE real!
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'REAL'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'real'),
                    Token('EOC', '!')]
        assert expected == tokens

    def test_decl_float_init(self):
        code = """
        NAME A REAL 3.14 AS THE real.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'REAL'),
                    Token('FLOAT_LITERAL', '3.14'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'real'),
                    Token('EOC', '.')]
        assert expected == tokens

    def test_decl_glyph_noinit(self):
        code = """
        NAME A GLYPH AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'GLYPH'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.')]
        assert expected == tokens

    def test_decl_glyph_init(self):
        code = """
        NAME A GLYPH '1' AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'GLYPH'),
                    Token('CHAR_LITERAL', '\'1\''),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.')]
        assert expected == tokens

    def test_decl_glyph_invalid(self):
        code = """
        NAME A GLYPH '123' AS THE foo.
        """
        with self.assertRaises(Exception):
            tokens, possible_tokens = lex_psyk(code)


    def test_decl_many_single_line(self):
        code = "NAME A NUMBER AS THE foo.  NAME A GLYPH AS THE bar."
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'NUMBER'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.'),
                    Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'GLYPH'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'bar'),
                    Token('EOC', '.'),
                    ]
        assert expected == tokens

    def test_identifier_underscore(self):
        code = "NAME A NUMBER AS THE foo_."
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo_'),
            Token('EOC', '.')
        ]
        assert expected == tokens

    def test_identifier_bad_underscore(self):
        code = "NAME A NUMBER AS THE _foo."
        with self.assertRaises(Exception):
            tokens, possible_tokens = lex_psyk(code)


    def test_identifier_bad_numbers(self):
        code = "NAME A NUMBER AS THE foo1."
        tokens, possible_tokens = lex_psyk(code)
        assert tokens[6] != Token('EOC', '.')

    def test_math_binary_joining(self):
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER AS THE foobar.
        MAKE THE foobar BE THE JOINING OF THE foo AND THE bar.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('INT_LITERAL', '1'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('INT_LITERAL', '2'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('EOC', '.'),
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foobar'),
            Token('EOC', '.'),
            Token('ASSIGN', 'MAKE'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foobar'),
            Token('BE', 'BE'),
            Token('MATH_BINARY_OP', 'THE JOINING OF'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('AND', 'AND'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('EOC', '.')
        ]

    def test_math_binary_reduction(self):
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER AS THE foobar.
        MAKE THE foobar BE THE REDUCTION OF THE foo BY THE bar.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('INT_LITERAL', '1'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('INT_LITERAL', '2'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('EOC', '.'),
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foobar'),
            Token('EOC', '.'),
            Token('ASSIGN', 'MAKE'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foobar'),
            Token('BE', 'BE'),
            Token('MATH_BINARY_OP', 'THE REDUCTION OF'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('BY', 'BY'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('EOC', '.')
        ]
        assert expected == tokens

    def test_math_binary_cross(self):
        code = """
        NAME A NUMBER THE CROSS OF 2 AND 3 AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('MATH_BINARY_OP', 'THE CROSS OF'),
            Token('INT_LITERAL', '2'),
            Token('AND', 'AND'),
            Token('INT_LITERAL', '3'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_math_binary_split(self):
        code = """
        NAME A REAL THE SPLIT OF 30 INTO -20 AS THE foo.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'REAL'),
            Token('MATH_BINARY_OP', 'THE SPLIT OF'),
            Token('INT_LITERAL', '30'),
            Token('INTO', 'INTO'),
            Token('INT_LITERAL', '-20'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_math_nary_joining(self):
        code = """
         NAME A REAL THE JOINING OF ALL OF 30, -20, 5 TOGETHER AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'REAL'),
            Token('MATH_NARY_OP', 'THE JOINING OF ALL OF'),
            Token('INT_LITERAL', '30'),
            Token('INT_LITERAL', '-20'),
            Token('INT_LITERAL', '5'),
            Token('TOGETHER', 'TOGETHER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_math_nary_cross(self):
        code = """
         NAME A REAL THE CROSS OF ALL OF 30, -20, 5 TOGETHER AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'REAL'),
            Token('MATH_NARY_OP', 'THE CROSS OF ALL OF'),
            Token('INT_LITERAL', '30'),
            Token('INT_LITERAL', '-20'),
            Token('INT_LITERAL', '5'),
            Token('TOGETHER', 'TOGETHER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_binary_both(self):
        code = """
         NAME A TRUTH BOTH OF TRUE AND FALSE AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_BINARY_OP', 'BOTH OF'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_binary_either(self):
        code = """
         NAME A TRUTH EITHER OF TRUE AND FALSE AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_BINARY_OP', 'EITHER OF'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_binary_one(self):
        code = """
         NAME A TRUTH ONE OF TRUE AND FALSE AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_BINARY_OP', 'ONE OF'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_nary_entirety(self):
        code = """
         NAME A TRUTH THE ENTIRETY OF TRUE AND FALSE AND TRUE TOGETHER AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_NARY_OP', 'THE ENTIRETY OF'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('TOGETHER', 'TOGETHER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_nary_some(self):
        code = """
         NAME A TRUTH SOME OF TRUE AND FALSE AND TRUE TOGETHER AS THE foo.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_NARY_OP', 'SOME OF'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AND', 'AND'),
            Token('BOOL_LITERAL', 'TRUE'),
            Token('TOGETHER', 'TOGETHER'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_logic_unary(self):
        code = """
                 NAME A TRUTH THE OPPOSITE OF FALSE AS THE foo.
                 """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('LOGIC_UNARY_OP', 'THE OPPOSITE OF'),
            Token('BOOL_LITERAL', 'FALSE'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
        ]
        self.check_enumerate(expected, tokens)
        assert expected == tokens

    def test_compare_greater(self):
        code = """
        NAME A TRUTH GREATER 100 THAN 3.0 AS THE BAR.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('COMPARE_BINARY_OP', 'GREATER'),
            Token('INT_LITERAL', '100'),
            Token('THAN', 'THAN'),
            Token('FLOAT_LITERAL', '3.0'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'BAR'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_compare_selfsame(self):
        code = """
        NAME A TRUTH SELFSAME 100 AND 100 AS THE BAR.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'TRUTH'),
            Token('COMPARE_BINARY_OP', 'SELFSAME'),
            Token('INT_LITERAL', '100'),
            Token('AND', 'AND'),
            Token('INT_LITERAL', '100'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'BAR'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_io_mystery(self):
        code = """
        NAME A NUMBER MYSTERY AS THE UNKNOWN.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('MYSTERY', 'MYSTERY'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'UNKNOWN'),
            Token('EOC', '.'),
        ]
        assert expected == tokens

    def test_io_summon(self):
        code = """
        NAME A GLYPH AS THE char. MAKE THE char BE SUMMONED.
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'GLYPH'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'char'),
            Token('EOC', '.'),
            Token('ASSIGN', 'MAKE'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'char'),
            Token('BE', 'BE'),
            Token('SUMMONED', 'SUMMONED'),
            Token('EOC', '.')
        ]
        assert expected == tokens


    def test_io_reveal_noendl(self):
        code = """
         NAME A NUMBER 3 AS THE foo.
         REVEAL THE FOO.
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'NUMBER'),
                    Token('INT_LITERAL', '3'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.'),
                    Token('REVEAL', 'REVEAL'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'FOO'),
                    Token('EOC', '.')
                    ]
        assert expected == tokens

    def test_io_reveal_endl(self):
        code = """
         NAME A NUMBER 3 AS THE foo.
         REVEAL THE FOO!
         """
        tokens, possible_tokens = lex_psyk(code)
        expected = [Token('DECLARE', 'NAME'),
                    Token('A', 'A'),
                    Token('SCALAR_TYPE', 'NUMBER'),
                    Token('INT_LITERAL', '3'),
                    Token('AS', 'AS'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'foo'),
                    Token('EOC', '.'),
                    Token('REVEAL', 'REVEAL'),
                    Token('THE', 'THE'),
                    Token('IDENTIFIER', 'FOO'),
                    Token('EOC', '!')
                    ]
        assert expected == tokens


    def test_comments_single(self):
        code = """(This is a comment.  Nothing else should.)"""
        tokens, possible_tokens = lex_psyk(code)
        expected = []
        assert expected == tokens


    def test_comments_multiline(self):
        code = """(This is a comment.  
        Nothing else should.)"""
        tokens, possible_tokens = lex_psyk(code)
        expected = []
        assert expected == tokens


    def test_comments_multiline_code(self):
        code = """(This is a comment.  
        Nothing else should.)
        REVEAL THE FOO!
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('REVEAL', 'REVEAL'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('EOC', '!')
        ]
        assert expected == tokens

    def test_comments_multiline_code_middle(self):
        code = """(This is a comment.  
        Nothing else should.)
        REVEAL (as we say) THE FOO!
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('REVEAL', 'REVEAL'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('EOC', '!')
        ]
        assert expected == tokens

    def test_comma_code(self):
        code = """
        REVEAL, THE FOO!
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('REVEAL', 'REVEAL'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('EOC', '!')
        ]
        assert expected == tokens

    def test_complex(self):
        code = """
        NAME A REAL AS THE foo.  (Foo!)
        NAME A NUMBER 3 AS THE bar! (Yes!)
        MAKE THE FOO BE THE CROSS OF (multiplied) THE bar BY 2!
        REVEAL THE FOO!!
        (And, we're done!)
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'REAL'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'foo'),
            Token('EOC', '.'),
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'NUMBER'),
            Token('INT_LITERAL', '3'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('EOC', '!'),
            Token('ASSIGN', 'MAKE'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('BE', 'BE'),
            Token('MATH_BINARY_OP', 'THE CROSS OF'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'bar'),
            Token('BY', 'BY'),
            Token('INT_LITERAL', '2'),
            Token('EOC', '!'),
            Token('REVEAL', 'REVEAL'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('EOC', '!'),
            Token('EOC', '!')
        ]
        assert tokens, possible_tokens == expected

    def test_math_unary_negation(self):
        code = """
        NAME A REAL THE NEGATION OF -2 AS THE FOO!
        """
        tokens, possible_tokens = lex_psyk(code)
        expected = [
            Token('DECLARE', 'NAME'),
            Token('A', 'A'),
            Token('SCALAR_TYPE', 'REAL'),
            Token('MATH_UNARY_OP', 'THE NEGATION OF'),
            Token('INT_LITERAL', '-2'),
            Token('AS', 'AS'),
            Token('THE', 'THE'),
            Token('IDENTIFIER', 'FOO'),
            Token('EOC', '!'),
        ]
        assert tokens, possible_tokens == expected

"""
The only thing we're going to do for main is call our unittests.

See the documentation for Python 3's unittest library for details
about how to run a subset of tests.

https://docs.python.org/3/library/unittest.html
"""
if __name__ == '__main__':
    unittest.main()
