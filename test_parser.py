import unittest

class TestParser(unittest.TestCase):
    
    def test_00_empty(self):
        from psyk.project import parse_psyk
        code = """"""
        parse_psyk(code)


    def test_01_empty(self):
        from psyk.project import parse_psyk
        code = """

        """
        parse_psyk(code)

    def test_02_blank_commands(self):
        from psyk.project import parse_psyk
        code ="""
        !!!...!!!
        """
        parse_psyk(code)

    def test_03_comments(self):
        from psyk.project import parse_psyk
        code = """
        (This is a single line comment)
        """
        parse_psyk(code)

        code = """
        (This is a
        multiline comment with a SELFSAME keyword)
        """
        parse_psyk(code)


    def test_04_declaration_noinit_int(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER AS THE foo.
        """
        parse_psyk(code)


    def test_05_declaration_init_int(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 3 AS THE foo.
        """
        parse_psyk(code)


    def test_06_declaration_many(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 3 AS THE foo.
        NAME A NUMBER 4 AS THE bar.
        """
        parse_psyk(code)


    def test_09_expr_literal(self):
        from psyk.project import parse_psyk
        code = """
        4.
        """
        parse_psyk(code)

        code = """
        -10.
        """
        parse_psyk(code)


    def test_10_expr_assign_int(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER AS THE foo. MAKE THE foo BE 3.
        """
        parse_psyk(code)


    def test_11_assign_chain(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER AS THE foo.
        NAME A NUMBER AS THE bar.
        MAKE THE foo BE MAKE THE bar BE 3.
        """
        parse_psyk(code)


    def test_12_math_negation(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE NEGATION OF THE bar AS THE baz.
        """
        parse_psyk(code)


    def test_13_math_add(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE JOINING OF THE bar AND THE foo AS THE baz.
        """
        parse_psyk(code)


    def test_14_math_sub(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE REDUCTION OF THE bar BY THE foo AS THE baz.
        """
        parse_psyk(code)


    def test_15_math_mul(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE CROSS OF THE bar WITH THE foo AS THE baz.
        """
        parse_psyk(code)


    def test_16_math_mul(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE SPLIT OF THE bar INTO THE foo AS THE baz.
        """
        parse_psyk(code)


    def test_17_math_greater(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo!
        NAME A NUMBER 2 AS THE bar!
        NAME A NUMBER THE GREATER OF THE bar AND THE foo AS THE baz!
        """
        parse_psyk(code)


    def test_18_math_greater(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 1 AS THE foo.
        NAME A NUMBER 2 AS THE bar.
        NAME A NUMBER THE LESSER OF THE bar AND THE foo AS THE baz.
        """
        parse_psyk(code)



    def test_21_math_binary_complex(self):
        from psyk.project import parse_psyk
        code = """
        NAME A NUMBER 4 AS THE baz.
        NAME A NUMBER THE JOINING OF 3 AND THE baz AS THE foo.
        MAKE THE baz BE THE CROSS OF THE baz WITH 3.
        """
        parse_psyk(code)



    def test_26_math_nary_sum(self):
        from psyk.project import parse_psyk
        code = """
        THE JOINING OF ALL OF 1, 2, 3, 4 TOGETHER.
        """
        parse_psyk(code) 


    def test_31_expr_bool(self):
        from psyk.project import parse_psyk
        code = """
        TRUE.
        """
        parse_psyk(code)

        code = """
        FALSE!
        """
        parse_psyk(code)


    def test_32_assign_noinit_bool(self):
        from psyk.project import parse_psyk
        code = """
        NAME A TRUTH AS THE truthiness.
        """
        parse_psyk(code)


    def test_33_assign_init_bool(self):
        from psyk.project import parse_psyk
        code = """
        NAME A TRUTH TRUE AS THE truthiest.
        """
        parse_psyk(code)


    def test_34_expr_logic_negate(self):
        from psyk.project import parse_psyk
        code = """
        THE OPPOSITE OF FALSE!
        """
        parse_psyk(code)


    def test_35_expr_logic_binary_and(self):
        from psyk.project import parse_psyk
        code = """
        BOTH OF TRUE AND FALSE.
        """
        parse_psyk(code)


    def test_36_expr_logic_binary_or(self):
        from psyk.project import parse_psyk
        code = """
        EITHER OF TRUE OR TRUE!
        """
        parse_psyk(code)   


    def test_37_expr_logic_binary_xor(self):
        from psyk.project import parse_psyk
        code = """
        ONE OF TRUE OR FALSE.
        """
        parse_psyk(code)


    def test_38_expr_logic_binary_complex_0(self):
        from psyk.project import parse_psyk
        code = """
        ONE OF TRUE OR EITHER OF TRUE OR TRUE.
        """
        parse_psyk(code)



    def test_41_expr_logic_nary_and(self):
        from psyk.project import parse_psyk
        code ="""
        THE ENTIRETY OF TRUE AND FALSE TOGETHER.
        """
        parse_psyk(code)


    def test_42_expr_logic_nary_or(self):
        from psyk.project import parse_psyk
        code ="""
        SOME OF TRUE, FALSE, TRUE TOGETHER.
        """
        parse_psyk(code)


    def test_44_expr_compare_equal(self):
        from psyk.project import parse_psyk
        code = """
        SELFSAME 1 AND 2.
        """
        parse_psyk(code)


    def test_45_expr_compare_equal(self):
        from psyk.project import parse_psyk
        code = """
        LESSER 1 THAN 2.
        """
        parse_psyk(code)


    def test_46_expr_compare_equal(self):
        from psyk.project import parse_psyk
        code = """
        GREATER 2 THAN 3.
        """
        parse_psyk(code)


    def test_47_io_mystery(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A NUMBER MYSTERY AS THE unknown!
        """
        parse_psyk(code)


    def test_48_io_summon(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A NUMBER SUMMONED AS THE unknown!
        REVEAL SUMMONED.
        """
        parse_psyk(code)       


    def test_49_io_reveal(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A NUMBER 3 AS THE three!
        REVEAL THE three AND 4, 5, 6!
        """
        parse_psyk(code)        


    def test_50_io_show(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A NUMBER 3 AS THE three!
        SHOW THE three!
        """
        parse_psyk(code)   


    def test_51_error_lexing(self):
        from psyk.project import parse_psyk
        code ="""
        'too many characters in this glyph'
        """
        with self.assertRaises(Exception):
            parse_psyk(code)       


    def test_52_error_parsing(self):
        from psyk.project import parse_psyk
        code ="""
        Really this shouldn't work at all.
        """
        with self.assertRaises(Exception):
            parse_psyk(code)  


    def test_53_combined(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A TRUTH TRUE AS THE truest.
        NAME A TRUTH THE OPPOSITE OF TRUE AS THE falstest.
        NAME A TRUTH SELFSAME THE truest AND THE falsest AS THE both.
        """
        parse_psyk(code)  


    def test_54_combined(self):
        from psyk.project import parse_psyk
        code ="""
        NAME A NUMBER 3 AS THE greater.
        NAME A NUMBER 2 AS THE lesser.
        NAME A NUMBER THE JOINING OF THE greater AND THE lesser AS THE combined.
        NAME A TRUTH GREATER THE lesser THAN THE combined AS THE foobar.
        """
        parse_psyk(code)  
    
