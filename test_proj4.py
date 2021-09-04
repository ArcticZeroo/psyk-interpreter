import unittest


def run(src_code):
    from psyk.project import psyk_to_intermediate
    from psyk.interpreter.interpreter import interpret_intermediate
    
    inter_code = psyk_to_intermediate(src_code)
    stable = interpret_intermediate(inter_code, debug=True)

    return stable



def capture_output(src_code, to_input=""):
    from psyk.project import psyk_to_intermediate
    from psyk.interpreter.interpreter import interpret_intermediate
    import io
    import contextlib
    import sys
    
    inter_code = psyk_to_intermediate(src_code)
    print(inter_code)

    old_stdin = sys.stdin

    sys.stdin = io.StringIO(to_input)

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        stable = interpret_intermediate(inter_code, debug=True)
    
    sys.stdin = old_stdin

    return f.getvalue(), stable


class TestLanguageEnhancements(unittest.TestCase):

     # ==================================================================== NOP
    def test_empty(self):        
        code = ""
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """

        """
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        ,!!!....!!!,!
        """
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    def test_comments(self):
        from psyk.project import parse_psyk
        code = """
        (This is a single line comment)
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        (This is a
        multiline comment with a SELFSAME keyword)
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    # ==================================================================== Errors

    def test_no_empty_expr_list(self):
        code = """
        NAME A NUMBER THE JOINING OF ALL OF TOGETHER AS THE FOO.        
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_undeclared_ident(self):
        code = """
        SHOW THE FOO!
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)





    # ==================================================================== EXPR Only
    def test_expr_int(self):
        code = r"""
        3.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        ,3.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        -3!
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_expr_bool(self):
        code = r"""
        TRUE.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        FALSE.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_expr_float(self):
        code = r"""
        3.0.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        ,3.0.
        """
        expected = r""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        -3.01!
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    def test_expr_char(self):
        code = r"""
        'a'.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)
        
        
        code = r"""
        '%%'.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        '%t'.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        '%''.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        '%n'.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        '%a'.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



     # ==================================================================== OUTPUT OPS
    def test_outnum_int(self):
        code = """
        REVEAL 5.
        """
        expected = "5\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        REVEAL 5, 10.
        """
        expected = "510\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        SHOW THE JOINING OF 4 AND 20.
        """
        expected = "24"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_outnum_float(self):
        code = """
        REVEAL 5.55.
        """
        expected = "5.55\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        REVEAL 5, -10.0!
        """
        expected = "5-10.0\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_outnum_bool(self):
        code = """
        REVEAL TRUE.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))

        code = """
        SHOW FALSE!
        """
        output, stable = capture_output(code)
        self.assertEquals(0, int(output))


    def test_outchar(self):
        code = """
        REVEAL 'a'.
        """
        expected = "a\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = """
        SHOW 'a', 'b', 'c', 'd'.
        """
        expected = "abcd"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        SHOW 'a', '%t', '%%', '%n'!
        """
        expected = "a\t%\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    # ==================================================================== Basic Assignment
    def test_assignment_int_good(self):
        code = r"""
        NAME A NUMBER 77 AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)
   
        code = r"""
        NAME A NUMBER -88 AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)
   
   
    def test_assignment_int_bad(self):
        code = r"""
        NAME A NUMBER 77.7 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME A NUMBER TRUE AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME A NUMBER 'a' AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    def test_assignment_float_good(self):
        code = r"""
        NAME A REAL 1.23 AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        NAME A REAL -1.2345 AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    def test_assignment_float_bad(self):
        code = r"""
        NAME A REAL 42 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A REAL 7 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A REAL '%n' AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A REAL FALSE AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    def test_assignment_bool_good(self): 
        code = r"""
        NAME A TRUTH TRUE AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = r"""
        NAME A TRUTH FALSE AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    def test_assignment_bool_bad(self):
        code = r"""
        NAME A TRUTH 1 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME A TRUTH 1.11 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A TRUTH 'z' AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    def test_assignment_char_good(self):
        code = r"""
        NAME A GLYPH 'k' AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


        code = r"""
        NAME A GLYPH '%%' AS THE FOO.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    def test_assignment_char_bad(self):
        code = r"""
        NAME A GLYPH 1 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME A GLYPH 1.99 AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME A GLYPH TRUE AS THE FOO.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Storage and Output

    def test_store_and_output(self):
        code = r"""
        NAME A NUMBER 1 AS THE BAR.
        SHOW THE BAR.
        """
        expected = "1"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        NAME A REAL 1.11 AS THE BAR.
        SHOW THE BAR.
        """
        expected = "1.11"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        NAME A TRUTH TRUE AS THE BAR.
        SHOW THE BAR.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        NAME A TRUTH FALSE AS THE BAR.
        SHOW THE BAR.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        NAME A GLYPH 'p' AS THE BAR.
        SHOW THE BAR.
        """
        expected = "p"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)



    # ==================================================================== Negate
    def test_math_negation_good(self):
        code = r"""
        SHOW THE NEGATION OF 2.
        """
        expected = "-2"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        SHOW THE NEGATION OF -4.
        """
        expected = "4"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)

        code = r"""
        SHOW THE NEGATION OF -42.01.
        """
        expected = "42.01"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        SHOW THE NEGATION OF 100.7.
        """
        expected = "-100.7"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)

        
    def test_math_negation_bad(self):
        code = r"""
        SHOW THE NEGATION OF TRUE.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE NEGATION OF 'a'.
        """
        expected = ""
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Add  
    def test_math_add_good(self):
        code = r"""
        SHOW THE JOINING OF 1 AND 2.
        """
        expected = "3"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        SHOW THE JOINING OF 1.0 AND 4.4.
        """
        expected = "5.4"
        output, stable = capture_output(code)
        self.assertEqual(float(expected), float(output))


        code = r"""
        SHOW THE JOINING OF 1 AND 2.21.
        """
        expected = "3.21"
        output, stable = capture_output(code)
        self.assertEqual(float(expected), float(output))


        code = r"""
        SHOW THE JOINING OF 1 AND 2.
        """
        expected = "3"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        SHOW THE JOINING OF 1.0 AND 4.4.
        """
        expected = "5.4"
        output, stable = capture_output(code)
        self.assertEqual(float(expected), float(output))



    def test_math_add_bad(self):
        code = r"""
        SHOW THE JOINING OF 1 AND 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF 'x' AND 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF 'x' AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF 1 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
     


    # ==================================================================== Subtract  
    def test_math_sub_good(self):
        code = r"""
        SHOW THE REDUCTION OF 1 BY 2.
        """
        expected = "-1"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


        code = r"""
        SHOW THE REDUCTION OF 1.0 BY -4.4.
        """
        expected = "5.4"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE REDUCTION OF 1 BY 2.21.
        """
        expected = "-1.21"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE REDUCTION OF 1 BY 2.
        """
        expected = "-1"
        output, stable = capture_output(code)
        self.assertAlmostEqual(expected, output)


        code = r"""
        SHOW THE REDUCTION OF 1.0 BY 4.4.
        """
        expected = "-3.4"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))



    def test_math_sub_bad(self):
        code = r"""
        SHOW THE REDUCTION OF 1 BY 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE REDUCTION OF 'x' BY 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE REDUCTION OF 'x' BY TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE REDUCTION OF 1 BY TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Multiply  
    def test_math_mult_good(self):
        code = r"""
        SHOW THE CROSS OF 2 WITH 4.
        """
        expected = "8"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))   


        code = r"""
        SHOW THE CROSS OF 2.2 WITH 6.4.
        """
        expected = "14.08"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))   


        code = r"""
        SHOW THE CROSS OF 3.3 WITH 2.
        """
        expected = "6.6"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))   


        code = r"""
        SHOW THE CROSS OF 4 WITH -1.11.
        """
        expected = "-4.44"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))   



    def test_math_mult_bad(self):
        code = r"""
        SHOW THE CROSS OF 2 WITH 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
          

        code = r"""
        SHOW THE CROSS OF TRUE WITH 6.4.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE CROSS OF 'a' WITH 'p'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE CROSS OF 4 WITH FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)




    # ==================================================================== Divide  
    def test_math_div_good(self):
        code = r"""
        SHOW THE SPLIT OF 4 INTO 2.
        """
        expected = "2"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE SPLIT OF 4.4 INTO -2.
        """
        expected = "-2.2"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE SPLIT OF 4.4 INTO 2.2.
        """
        expected = "2.0"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE SPLIT OF -4 INTO 2.2.
        """
        expected = "-1.818181818"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))



    def test_math_div_bad(self):
        code = r"""
        SHOW THE SPLIT OF 4 INTO 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE SPLIT OF 'a' INTO 2.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW THE SPLIT OF TRUTH INTO 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW THE SPLIT OF 'a' INTO 1.1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    # ==================================================================== Integer Divide 
    def test_math_idiv_good(self):
        code = r"""
        SHOW THE WHOLE SPLIT OF 10 INTO 2.
        """
        output, stable = capture_output(code)
        self.assertEqual(5, int(output))

        code = r"""
        SHOW THE WHOLE SPLIT OF 100 INTO -2.
        """
        output, stable = capture_output(code)
        self.assertEqual(-50, int(output))

        code = r"""
        SHOW THE WHOLE SPLIT OF -200 INTO -2.
        """
        output, stable = capture_output(code)
        self.assertEqual(100, int(output))


    def test_math_idiv_bad(self):
        code = r"""
        SHOW THE WHOLE SPLIT OF 10 INTO 2.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE WHOLE SPLIT OF TRUE INTO -2.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE WHOLE SPLIT OF 2.0 INTO -2.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE WHOLE SPLIT OF 2 INTO 'X'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE WHOLE SPLIT OF 2 INTO 0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Modulo 
    def test_math_mod_good(self):
        code = r"""
        SHOW THE WHOLE SPLIT REMAINDER OF 10 INTO 3.
        """
        output, stable = capture_output(code)
        self.assertEqual(1, int(output))


        code = r"""
        SHOW THE WHOLE SPLIT REMAINDER OF 21 INTO 3.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_math_mod_bad(self):
        code = r"""
        SHOW THE WHOLE SPLIT OF 2 INTO 1.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE WHOLE SPLIT OF 2.0 INTO 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE WHOLE SPLIT OF 2.0 INTO 1.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW THE WHOLE SPLIT OF 2 INTO 0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Math Greater  
    def test_math_greater_good(self):
        code = r"""
        SHOW THE GREATER OF 1 AND 10.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(10, float(output))

        code = r"""
        SHOW THE GREATER OF 33.3 AND 6.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(33.3, float(output))

        code = r"""
        SHOW THE GREATER OF 33 AND 42.0.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(42.0, float(output))

        code = r"""
        SHOW THE GREATER OF -33.3 AND 98.6.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(98.6, float(output))



    def test_math_greater_bad(self):
        code = r"""
        SHOW THE GREATER OF 6 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE GREATER OF 'x' AND 10.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE GREATER OF 'x' AND FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
            


    # ==================================================================== Math Lesser  
    def test_math_lesser_good(self):
        code = r"""
        SHOW THE LESSER OF 1 AND 10.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(1, float(output))

        code = r"""
        SHOW THE LESSER OF 33.3 AND 6.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(6, float(output))

        code = r"""
        SHOW THE LESSER OF 33 AND 42.0.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(33, float(output))

        code = r"""
        SHOW THE LESSER OF -33.3 AND 98.6.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(-33.3, float(output))


    def test_math_lesser_bad(self):
        code = r"""
        SHOW THE LESSER OF 6 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE LESSER OF 'x' AND 10.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE LESSER OF 'x' AND FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== N-ary Add  
    def test_math_nary_add_good(self):
        code = r"""
        SHOW THE JOINING OF ALL OF 1, 2, 3, 4 TOGETHER.
        """
        expected = "10"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE JOINING OF ALL OF 10.1, 20.1, 30.1, 40.1 TOGETHER.
        """
        expected = "100.4"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE JOINING OF ALL OF 10.1, 2, 3 TOGETHER.
        """
        expected = "15.1"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE JOINING OF ALL OF 11, 11.0, 22, 22.1, -0.1 TOGETHER.
        """
        expected = "66.0"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))



    def test_math_nary_add_bad(self):
        code = r"""
        SHOW THE JOINING OF ALL OF 1, 2, 3, AND 'a' TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF ALL OF TRUE AND 1 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF ALL OF 1.0, 2.0 AND 'z' TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE JOINING OF ALL OF TRUE AND FALSE AND 3.0 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    # ==================================================================== N-ary Mult  

    def test_math_nary_mult_good(self):
        code = r"""
        SHOW THE CROSS OF ALL OF 0, 1, 2 TOGETHER.
        """
        expected = "0"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE CROSS OF ALL OF 1.0, 3.0, 5.0 TOGETHER.
        """
        expected = "15.0"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))


        code = r"""
        SHOW THE CROSS OF ALL OF 2 AND 3.0 AND -0.1 TOGETHER.
        """
        expected = "-0.6"
        output, stable = capture_output(code)
        self.assertAlmostEqual(float(expected), float(output))



    def test_math_nary_mult_bad(self):
        code = r"""
        SHOW THE CROSS OF ALL OF 1, 2, AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE CROSS OF ALL OF 1, 'x', 2, 3 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE CROSS OF ALL OF 'x' AND 'y' AND 'z' TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW THE CROSS OF ALL OF TRUE AND 1.0 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)





    # ==================================================================== Compare Equ
    def test_compare_equ_good(self):
        code = r"""
        SHOW SELFSAME 1 AND 1.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SELFSAME 1 AND 2.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW SELFSAME 1 AND 1.1.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW SELFSAME 1.0 AND 1.0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SELFSAME 'a' AND 'a'.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SELFSAME 'a' AND 'z'.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW SELFSAME TRUE AND TRUE.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SELFSAME FALSE AND TRUE.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_compare_equ_bad(self):
        code = r"""
        SHOW SELFSAME 1 AND 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SELFSAME 1 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SELFSAME TRUE AND 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SELFSAME FALSE AND 1.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SELFSAME 1.0 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        
        code = r"""
        SHOW SELFSAME 2.22 AND 'q'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    # ==================================================================== Compare Less

    def test_compare_less_good(self):
        code = r"""
        SHOW LESSER 1 THAN 2.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW LESSER 1.0 THAN 2.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW LESSER 2 THAN 1.0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW LESSER 2.0 THAN 1.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW LESSER 2.0 THAN 1.0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW LESSER 1.0 THAN 2.0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))




    def test_compare_less_bad(self):
        code = r"""
        SHOW LESSER 'a' THAN 'z'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW LESSER FALSE THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW LESSER 1 THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW LESSER 1 THAN 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW LESSER 22.2 THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW LESSER 22.2 THAN 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Compare Greater
    def test_compare_greater_good(self):
        code = r"""
        SHOW GREATER 20 THAN 10.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW GREATER 10 THAN 20.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW GREATER 22.2 THAN 11.1.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW GREATER 11.1 THAN 22.2.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW GREATER 20 THAN 11.1.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW GREATER 10 THAN 22.2.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW GREATER 22.2 THAN 11.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW GREATER 11.1 THAN 22.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_compare_greater_bad(self):
        code = r"""
        SHOW GREATER 'a' THAN 'z'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW GREATER FALSE THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW GREATER 1 THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW GREATER 1 THAN 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW GREATER 22.2 THAN TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        SHOW GREATER 22.2 THAN 'a'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Logical NOT
    def test_logic_not_good(self):
        code = r"""
        SHOW THE OPPOSITE OF TRUE.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))

        code = r"""
        SHOW THE OPPOSITE OF FALSE.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))



    def test_logic_not_bad(self):
        code = r"""
        SHOW THE OPPOSITE OF 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE OPPOSITE OF -11.1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE OPPOSITE OF 'x'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)



    # ==================================================================== Logical AND
    def test_logic_and_good(self):
        code = r"""
        SHOW BOTH OF TRUE AND TRUE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))

        code = r"""
        SHOW BOTH OF FALSE AND TRUE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))

        code = r"""
        SHOW BOTH OF TRUE AND FALSE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW BOTH OF FALSE AND FALSE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_logic_and_bad(self):
        code = r"""
        SHOW BOTH OF TRUE AND 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW BOTH OF TRUE AND 33.33.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW BOTH OF FALSE AND 'h'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW BOTH OF 1 AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW BOTH OF 33.33 AND FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW BOTH OF 'h' AND TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

    

    # ==================================================================== Logical OR
    def test_logic_or_good(self):
        code = r"""
        SHOW EITHER OF TRUE OR TRUE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))

        code = r"""
        SHOW EITHER OF FALSE OR TRUE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))

        code = r"""
        SHOW EITHER OF TRUE OR FALSE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW EITHER OF FALSE OR FALSE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_logic_or_bad(self):
        code = r"""
        SHOW EITHER OF TRUE OR 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW EITHER OF TRUE OR 33.33.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW EITHER OF FALSE OR 'h'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW EITHER OF 1 OR TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW EITHER OF 33.33 OR FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW EITHER OF 'h' OR TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    
    # ==================================================================== Logical XOR
    def test_logic_xor_good(self):
        code = r"""
        SHOW ONE OF TRUE OR TRUE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))

        code = r"""
        SHOW ONE OF FALSE OR TRUE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))

        code = r"""
        SHOW ONE OF TRUE OR FALSE. 
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW ONE OF FALSE OR FALSE. 
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_logic_xor_bad(self):
        code = r"""
        SHOW ONE OF TRUE OR 1.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW ONE OF TRUE OR 33.33.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW ONE OF FALSE OR 'h'.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW ONE OF 1 OR TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW ONE OF 33.33 OR FALSE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        

        code = r"""
        SHOW ONE OF 'h' OR TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    
    # ==================================================================== Logical N-ary AND
    def test_logic_nary_and_good(self):
        code = r"""
        SHOW THE ENTIRETY OF TRUE AND TRUE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW THE ENTIRETY OF FALSE AND TRUE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW THE ENTIRETY OF TRUE AND FALSE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW THE ENTIRETY OF TRUE AND TRUE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW THE ENTIRETY OF TRUE AND FALSE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))


        code = r"""
        SHOW THE ENTIRETY OF FALSE AND FALSE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_logic_nary_and_bad(self):
        code = r"""
        SHOW THE ENTIRETY OF TRUE AND TRUE AND 1 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE ENTIRETY OF TRUE AND 'x' AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE ENTIRETY OF 3.0 AND TRUE AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW THE ENTIRETY OF 'x' AND TRUE AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    
    
    # ==================================================================== Logical N-ary OR
    def test_logic_nary_or_good(self):
        code = r"""
        SHOW SOME OF TRUE AND TRUE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SOME OF FALSE AND TRUE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SOME OF TRUE AND FALSE AND TRUE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SOME OF TRUE AND TRUE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SOME OF TRUE AND FALSE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(output))


        code = r"""
        SHOW SOME OF FALSE AND FALSE AND FALSE TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(output))



    def test_logic_nary_or_bad(self):
        code = r"""
        SHOW SOME OF TRUE AND TRUE AND 1 TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SOME OF TRUE AND 'x' AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SOME OF 3.0 AND TRUE AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        SHOW SOME OF 'x' AND TRUE AND FALSE TOGETHER.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    
    # ==================================================================== Input
    def test_input_good(self):
        code = r"""
        NAME A GLYPH SUMMONED AS THE character.
        SHOW THE character.
        """
        str_in = r"a"
        expected = r"a"
        output, stable = capture_output(code, str_in)
        self.assertEqual(expected, output)


        code = r"""
        NAME A GLYPH SUMMONED AS THE character.
        SHOW THE character.
        """
        str_in = "\t"
        expected = "\t"
        output, stable = capture_output(code, str_in)
        self.assertEqual(expected, output)


    def test_input_bad(self):
        code = r"""
        NAME A NUMBER SUMMONED AS THE character.
        SHOW THE character.
        """
        str_in = "a"
        with self.assertRaises(Exception):
            output, stable = capture_output(code, str_in)


        code = r"""
        NAME A REAL SUMMONED AS THE character.
        SHOW THE character.
        """
        str_in = "a"
        with self.assertRaises(Exception):
            output, stable = capture_output(code, str_in)

        code = r"""
        NAME A TRUTH SUMMONED AS THE character.
        SHOW THE character.
        """
        str_in = "a"
        with self.assertRaises(Exception):
            output, stable = capture_output(code, str_in)



    # ==================================================================== Random
    def test_random_good(self):
        code = r"""
        NAME A NUMBER MYSTERY AS THE number.
        SHOW THE number!
        """
        output, stable = capture_output(code)
        assert(-100 <= int(output) <= 100)


    def test_random_bad(self):
        code = r"""
        NAME A REAL MYSTERY AS THE number.
        SHOW THE number!
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A TRUTH MYSTERY AS THE number.
        SHOW THE number!
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME A GLYPH MYSTERY AS THE number.
        SHOW THE number!
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    # ==================================================================== If (basic)
    def test_if_basic_00(self):
        code = r"""
        SHOULD TRUE?
            SHOW 'a'.
        SO IT IS.
        SHOW 'b'.
        """
        expected = "ab"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)

    def test_if_basic_01(self):
        code = r"""
        SHOULD FALSE?
            SHOW 'a'.
        SO IT IS.
        SHOW 'b'.
        """
        expected = "b"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)
        


    def test_S_if_basic_02(self):
        code = r"""
        NAME A NUMBER 42 AS THE FOO.
        SHOULD TRUE?
            SHOW 'a'.
            NAME A GLYPH 'X' AS THE FOO.
            SHOW THE FOO.
        SO IT IS.
        REVEAL 'b'.
        SHOW THE FOO.
        """
        expected = "aXb\n42"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)



    # ==================================================================== If-Else (basic)
    def test_ifelse_basic_00(self):
        code = r"""
        SHOULD TRUE?
            SHOW 'a'.
        LEST,
            SHOW 'b'.
        SO IT IS.
        SHOW 'c'.
        """
        expected = "ac"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


    def test_ifelse_basic_01(self):
        code = r"""
        SHOULD FALSE?
            SHOW 'a'.
        LEST,
            SHOW 'b'.
        SO IT IS.
        SHOW 'c'.
        """
        expected = "bc"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)

    
    def test_S_ifelse_basic_02(self):
        code = r"""
        NAME A NUMBER 23 AS THE scoped.
        SHOW THE scoped.
        SHOULD FALSE?
            SHOW THE scoped.
            SHOW 'a'.
            NAME A GLYPH 's' AS THE scoped.
            SHOW THE scoped.
        LEST,
            SHOW THE scoped.
            SHOW 'b'.
            NAME A GLYPH 't' AS THE scoped.
            SHOW THE scoped.
        SO IT IS.
        SHOW THE scoped.
        SHOW 'c'.
        """
        expected = "2323bt23c"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)



    # ==================================================================== While (basic)
    def test_while_basic_00(self):
        code = r"""
        SHOW 'a'.
        WHILST FALSE?
            SHOW 'b'.
        SO IT IS.
        SHOW 'c'.
        """
        expected = "ac"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


    def test_while_basic_01(self):
        # Warning: this could loop infinitely if imporperly implemented
        code = r"""
        SHOW 'a'.
        NAME A NUMBER 3 AS THE counter.
        WHILST GREATER THE counter THAN 0?
            SHOW 'b'.
            MAKE THE counter BE THE REDUCTION OF THE counter BY 1.
        SO IT IS.
        SHOW 'c'.
        """
        expected = "abbbc"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


    def test_while_basic_02(self):
        code = r"""
        SHOW 'a'.
        NAME A NUMBER 3 AS THE counter.
        WHILST GREATER THE counter THAN 0?
            SHOW 'b'.
            FLEE!
            MAKE THE counter BE THE REDUCTION OF THE counter BY 1.
        SO IT IS.
        SHOW 'c'.
        """
        expected = "abc"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)


    def test_while_basic_03(self):
        code = r"""
        NAME A NUMBER 3 AS THE COUNTER.
        WHILST GREATER THE COUNTER THAN 0?
            NAME A NUMBER 4 AS THE OTHER_COUNTER.
            WHILST GREATER THE OTHER_COUNTER THAN 0?
                SHOULD SELFSAME 2 AND THE OTHER_COUNTER?
                    FLEE.
                SO IT IS.
                SHOW 'X'.
                MAKE THE OTHER_COUNTER BE THE REDUCTION OF THE OTHER_COUNTER BY 1.
            SO IT IS.
            SHOW 'O'.
            MAKE THE COUNTER BE THE REDUCTION OF THE COUNTER BY 1.
        SO IT IS.
        """
        expected = 'XXOXXOXXO'
        output, stable = capture_output(code)
        self.assertEqual(expected, output)

    
    def test_S_while_scope(self):
        code = r"""
        NAME A NUMBER 10 AS THE scoped.
        NAME A NUMBER 5 AS THE counter.
        WHILST GREATER THE counter THAN 0?
            MAKE THE counter BE THE REDUCTION OF THE counter BY 1.
            NAME A GLYPH 'a' AS THE scoped.
            SHOW THE scoped.
        SO IT IS.
        SHOW '%n'.
        REVEAL THE counter.
        REVEAL THE scoped.
        """
        expected = "aaaaa\n0\n10\n"
        output, stable = capture_output(code)
        self.assertEqual(expected, output)



    # ==================================================================== Array Declaration
    def test_A_decl_arr_good_00(self):
        code = r"""
        NAME 3 NUMBERS AS THE foos.
        """
        output, stable = capture_output(code)

        code = r"""
        NAME 4 REALS AS THE foos.
        """
        output, stable = capture_output(code)

        code = r"""
        NAME 4 GLYPHS AS THE foos.
        """
        output, stable = capture_output(code)

        code = r"""
        NAME 2 TRUTHS AS THE foos.
        """
        output, stable = capture_output(code)

    
    def test_A_decl_arr_good_01(self):
        code = r"""
        NAME 3 NUMBERS 1, 2, AND 3 AS THE foos.
        """
        output, stable = capture_output(code)

    
    def test_A_decl_arr_good_02(self):
        code = r"""
        NAME 4 REALS 11.1, 22.2, 33.3, 44.4 AS THE foos.
        """
        output, stable = capture_output(code)


    def test_A_decl_arr_good_03(self):
        code = r"""
        NAME 5 GLYPHS 'a', 'b', 'c', 'd' AS THE foos.
        """
        output, stable = capture_output(code)


    def test_A_decl_arr_good_04(self):
        code = r"""
        NAME 3 TRUTHS TRUE, TRUE, AND FALSE AS THE foos.
        """
        output, stable = capture_output(code)


    def test_A_decl_arr_bad_00(self):
        code = r"""
        NAME 3 TRUTHS 1, 2, AND 3 AS THE foos.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_A_decl_arr_bad_01(self):
        code = r"""
        NAME 3 NUMBER 1, 2, AND 3 AS THE foos.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_A_decl_arr_bad_02(self):
        code = r"""
        NAME NUMBERS 1, 2, AND 3 AS THE foos.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_A_decl_arr_bad_03(self):
        code = r"""
        NAME 5 GLYPHS 'a', 'b', 'c', TRUE AS THE foos.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME 3 NUMBERS 1, 'x', AND 3 AS THE foos.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    # ==================================================================== Array Size Of
    def test_A_sizeof(self):
        code = r"""
        NAME 3 NUMBERS AS THE foos.
        SHOW THE SIZE OF THE foos.
        """
        output, stable = capture_output(code)
        self.assertEqual(3, int(output))

        code = r"""
        NAME 4 REALS AS THE foos.
        SHOW THE SIZE OF THE foos.
        """
        output, stable = capture_output(code)
        self.assertEqual(4, int(output))


        code = r"""
        NAME 4 GLYPHS AS THE foos.
        SHOW THE SIZE OF THE foos.
        """
        output, stable = capture_output(code)
        self.assertEqual(4, int(output))


        code = r"""
        NAME 2 TRUTHS AS THE foos.
        SHOW THE SIZE OF THE foos.
        """
        output, stable = capture_output(code)
        self.assertEqual(2, int(output))


    # ==================================================================== Array Get
    def test_A_expr_arr_ndx_good_00(self):
        code = r"""
        NAME 3 GLYPHS 'x', 'y', 'z' AS THE foos.
        SHOW THE foos'0.
        """
        output, stable = capture_output(code)
        self.assertEqual('x', output)

        code = r"""
        NAME 3 GLYPHS 'x', 'y', 'z' AS THE foos.
        SHOW THE foos'0, THE foos'1, THE foos'2.
        """
        output, stable = capture_output(code)
        self.assertEqual('xyz', output)


    def test_A_expr_arr_ndx_good_01(self):
        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        NAME A GLYPH THE cat'0 AS THE char_c.
        SHOW THE char_c.
        """
        output, stable = capture_output(code)
        self.assertEqual('c', output)


    def test_A_expr_arr_ndx_bad(self):
        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        SHOW THE cat'x.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)

        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        SHOW THE cat'0.0.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        SHOW THE cat'TRUE.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_A_assgn_array(self):
        code = r"""
            NAME 5 NUMBERS 1, 2, 3, 4, 5 AS THE FOO.
            NAME 5 NUMBERS AS THE BAR.
            MAKE THE BAR BE THE FOO.
            SHOW THE BAR'3.
        """
        output, stable = capture_output(code)
        self.assertEqual(4, int(output))


    # ==================================================================== Array Set
    def test_A_expr_arr_ndx_set_good_00(self):
        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        MAKE THE cat'0 BE 'b'.
        SHOW THE cat'0, THE cat'1, THE cat'2.
        """
        output, stable = capture_output(code)
        self.assertEqual('bat', output)


    def test_A_expr_arr_ndx_set_good_01(self):
        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        MAKE THE cat'0 BE 'b'.
        NAME A GLYPH THE cat'0 AS THE should_b.
        SHOW THE should_b.
        """
        output, stable = capture_output(code)
        self.assertEqual('b', output)


    def test_A_expr_arr_ndx_set_good_02(self):
        code = r"""
        NAME 3 GLYPHS 'd', 'a', 'd' AS THE fam.
        MAKE THE fam'0 BE MAKE THE fam'2 BE 'n'.
        SHOW THE fam'0, THE fam'1, THE fam'2.
        """
        output, stable = capture_output(code)
        self.assertEqual('nan', output)



    def test_A_expr_arr_ndx_set_bad_00(self):
        code = r"""
        NAME 3 GLYPHS 'c', 'a', 't' AS THE cat.
        MAKE THE cat'0 BE 1.
        SHOW THE cat'0, THE cat'1, THE cat'2.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
        


    # ==================================================================== Complex (basic)
    def test_complex_00(self):
        code = r"""
        NAME 3 GLYPHS 'D', 'A', 'D' AS THE FAM.
        NAME A GLYPH MAKE THE FAM'0 BE MAKE THE FAM'2 BE 'N' AS THE n.
        SHOW THE n.
        """
        output, stable = capture_output(code)
        self.assertEqual('N', output)


    def test_complex_01(self):
        code = r"""
        NAME A NUMBER THE JOINING OF 1 AND 3 AS THE four.
        NAME A REAL THE REDUCTION OF 10.0 BY 5 AS THE five.
        NAME A REAL THE CROSS OF THE four WITH THE five AS THE twenty.
        SHOW SELFSAME THE twenty AND 20.
        """
        output, stable = capture_output(code)
        self.assertNotAlmostEqual(0, float(output))


    def test_complex_02(self):
        code = r"""
        NAME A TRUTH LESSER 2.0 THAN 4 AS THE true.
        NAME A TRUTH GREATER 2.0 THAN 4 AS THE false.
        SHOW SELFSAME THE true AND THE false.
        """
        output, stable = capture_output(code)
        self.assertAlmostEqual(0, int(output))


    def test_complex_03(self):
        code = r"""
        NAME A GLYPH 'b' AS THE b.
        NAME A GLYPH 'c' AS THE c.
        NAME A GLYPH MAKE THE c BE MAKE THE b BE 'a' AS THE a.
        SHOW THE a, THE b, THE c.
        """
        output, stable = capture_output(code)
        self.assertEqual('aaa', output)


    def test_complex_04(self):
        code = r"""
        NAME A GLYPH 'x' AS THE X.
        NAME A GLYPH 'y' AS THE Y.
        SHOW THE LESSER OF THE x AND THE y.
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)




    # ==================================================================== Complex w/ if
    def test_complex_if_00(self):
        code = r"""
        NAME A NUMBER 3 AS THE three.
        NAME A REAL 4.0 AS THE four.
        NAME A REAL THE JOINING OF THE three AND THE four AS THE sum.
        SHOULD SELFSAME THE sum AND 7?
            SHOW 'Y', 'e', 'p'.
        LEST,
            SHOW 'N', 'o', 'p', 'e'.
        SO IT IS.
        """
        output, stable = capture_output(code)
        self.assertEqual('Yep', output)



    def test_complex_if_01(self):
        code = r"""
        SHOULD GREATER 3 THAN 4?
            SHOW 'w' 'r' 'o' 'n' 'g'.
        LEST
            SHOULD SELFSAME 3 AND 4?
                SHOW 'n', 'o', 'p', 'e'.
            LEST
                SHOULD LESSER 3 THAN 4?
                    SHOW 'y', 'e', 'p'.
                SO IT IS.
            SO IT IS.
        SO IT IS.
        """
        output, stable = capture_output(code)
        self.assertEqual('yep', output)



    def test_S_complex_if_02(self):
        code = r"""
        NAME A NUMBER 42 AS THE scoped.
        SHOULD GREATER 3 THAN 4?
            SHOW THE scoped.
            NAME A GLYPH '!' AS THE scoped.
            SHOW 'w' 'r' 'o' 'n' 'g'.
        LEST
            SHOULD SELFSAME 3 AND 4?
                SHOW 'n', 'o', 'p', 'e'.
            LEST
                SHOW THE scoped.
                NAME A GLYPH '?' AS THE scoped.
                SHOULD LESSER 3 THAN 4?
                    SHOW 'y', 'e', 'p'.
                    SHOW THE scoped.
                SO IT IS.
            SO IT IS.
        SO IT IS.
        SHOW THE scoped.
        """
        output, stable = capture_output(code)
        self.assertEqual('42yep?42', output)


    def test_complex_if_03(self):
        code = r"""
        NAME A NUMBER MYSTERY AS THE a.
        NAME A NUMBER MYSTERY AS THE b.
        SHOULD LESSER THE a THAN 0?
            MAKE THE a BE THE NEGATION OF THE a.
        SO IT IS.
        SHOULD LESSER THE b THAN 0?
            MAKE THE b BE THE NEGATION OF THE b.
        SO IT IS.
        NAME A NUMBER THE CROSS OF THE a WITH THE b AS THE c.
        SHOW THE c.
        """
        output, stable = capture_output(code)
        assert(int(output) >= 0)



    # ==================================================================== Complex w/ while
    def test_S_complex_while_00(self):
        code = r"""
        NAME A NUMBER 3 AS THE counter.
        NAME A GLYPH 'x' AS THE output.
        WHILST GREATER THE counter THAN 0?
            SHOW THE output.
            NAME A NUMBER 2 AS THE other_counter.
            WHILST GREATER THE other_counter THAN 0?
                NAME A GLYPH 'o' AS THE output.
                SHOW THE output.
                MAKE THE other_counter BE THE REDUCTION OF THE other_counter BY 1.
            SO IT IS.
            MAKE THE counter BE THE REDUCTION OF THE counter BY 1.
        SO IT IS.
        SHOW THE output.
        """
        output, stable = capture_output(code)
        self.assertEqual('xooxooxoox', output)


    def test_A_complex_while_01(self):
        code = r"""
        NAME 5 GLYPHS 'H', 'E', 'L', 'L', 'O' AS THE hello.
        NAME A NUMBER THE SIZE OF THE hello AS THE ndx.
        WHILST GREATER THE ndx THAN 0?
            MAKE THE ndx BE THE REDUCTION OF THE ndx BY 1.
            SHOW THE hello'THE ndx.
        SO IT IS.
        """
        output, stable = capture_output(code)
        self.assertEqual('OLLEH', output)


    def test_S_complex_while_02(self):
        code = r"""
        NAME A NUMBER 10 AS THE switcher.
        NAME A GLYPH 'r' AS THE output.
        NAME A NUMBER 0 AS THE count.
        SHOULD LESSER THE switcher THAN 0?
            WHILST LESSER THE count THAN 5?
                NAME A GLYPH 'x' AS THE output.
                SHOW THE output.
                MAKE THE count BE THE JOINING OF THE count AND 1.
            SO IT IS.
        LEST
            WHILST LESSER THE count THAN 4?
                NAME A GLYPH 'z' AS THE output.
                SHOW THE output.
                MAKE THE count BE THE JOINING OF THE count AND 1.
            SO IT IS.
        SO IT IS.
        SHOW THE output.
        """
        output, stable = capture_output(code)
        self.assertEqual('zzzzr', output)



    def test_complex_while_03(self):
        code = r"""
        NAME A NUMBER 1 AS THE M.
        NAME A NUMBER 1 AS THE N.
        NAME A NUMBER 8 AS THE TERM.
        SHOULD LESSER THE TERM THAN 2?
            SHOW 1.
        LEST
            NAME A NUMBER 2 AS THE COUNTER.
            NAME A NUMBER AS THE RESULT.
            WHILST LESSER THE COUNTER THAN THE TERM?
                MAKE THE RESULT BE THE JOINING OF THE M AND THE N.
                MAKE THE M BE THE N.
                MAKE THE N BE THE RESULT.
                MAKE THE COUNTER BE THE JOINING OF THE COUNTER AND 1.
            SO IT IS.
            SHOW THE RESULT.
        SO IT IS.
        """
        output, stable = capture_output(code)
        self.assertEqual(21, int(output))



    def test_complex_while_04(self):
        code = r"""
        NAME A NUMBER 0 AS THE COUNTER.
        WHILST LESSER THE COUNTER THAN 10?
            SHOULD EITHER OF GREATER THE COUNTER THAN 5 OR SELFSAME THE COUNTER AND 5?
                SHOW 'O'.
            LEST
                SHOW '-'.
            SO IT IS.
            NAME A NUMBER THE COUNTER AS THE OTHER_COUNTER.
            WHILST LESSER THE OTHER_COUNTER THAN 10?
                SHOULD GREATER THE OTHER_COUNTER THAN 1?
                    FLEE.
                LEST
                    SHOW 'X'.
                SO IT IS.
                MAKE THE OTHER_COUNTER BE THE JOINING OF THE OTHER_COUNTER AND 1.
            SO IT IS.
            MAKE THE COUNTER BE THE JOINING OF THE COUNTER AND 1.
        SO IT IS.
        """
        output, stable = capture_output(code)
        expected = '-XX-X---OOOOO'
        self.assertEqual(expected, output)



    # ==================================================================== Complex w/ all
    def test_A_complex_all_00(self):
        code = r"""
        (We're going to try to find the even numbers.)

        NAME 5 NUMBERS 1, 2, 3, 4, 5 AS THE nums.
        NAME 5 TRUTHS AS THE is_evens.
        NAME A NUMBER THE SIZE OF THE nums AS THE size.
        NAME A NUMBER 0 AS THE ndx.
        WHILST LESSER THE ndx THAN THE size?
            SHOULD SELFSAME THE WHOLE SPLIT REMAINDER OF THE nums'THE ndx INTO 2 AND 0?
                MAKE THE is_evens'THE ndx BE TRUE.
            LEST
                MAKE THE is_evens'THE ndx BE FALSE.
            SO IT IS.
            MAKE THE ndx BE THE JOINING OF THE ndx AND 1.
        SO IT IS.
        MAKE THE ndx BE 0.
        WHILST LESSER THE ndx THAN THE size?
            REVEAL THE is_evens'THE ndx.
            MAKE THE ndx BE THE JOINING OF THE ndx AND 1.
        SO IT IS.
        """
        output, stable = capture_output(code)
        expected = [False, True, False, True, False]
        output = list(map(lambda x: int(x) != 0, output.splitlines()))
        self.assertEqual(expected, output)


    def test_A_complex_all_01(self):
        code = r"""

        (Let's implement bubble sort!)

        NAME 5 REALS 1.1, 3.4, 0.2, -6.2, 2.2 AS THE UNSORTED.

        NAME A NUMBER THE REDUCTION OF THE SIZE OF THE UNSORTED BY 1 AS THE LAST.
        NAME A NUMBER 0 AS THE COUNTER.
        
        WHILST LESSER THE COUNTER THAN THE SIZE OF THE UNSORTED?
            NAME A NUMBER 0 AS THE PTR.
            WHILST LESSER THE PTR THAN THE LAST?
                NAME A NUMBER THE JOINING OF THE PTR AND 1 AS THE NEXT.
                NAME A REAL THE UNSORTED'THE PTR AS THE M.
                NAME A REAL THE UNSORTED'THE NEXT AS THE N.
                MAKE THE UNSORTED'THE PTR BE THE LESSER OF THE M AND THE N.
                MAKE THE UNSORTED'THE NEXT BE THE GREATER OF THE M AND THE N.
                MAKE THE PTR BE THE JOINING OF THE PTR AND 1.
            SO IT IS.
            MAKE THE COUNTER BE THE JOINING OF THE COUNTER AND 1.
            MAKE THE LAST BE THE REDUCTION OF THE LAST BY 1.
        SO IT IS.

        MAKE THE COUNTER BE 0.
        WHILST LESSER THE COUNTER THAN THE SIZE OF THE UNSORTED?
            REVEAL THE UNSORTED'THE COUNTER.
            MAKE THE COUNTER BE THE JOINING OF THE COUNTER AND 1.
        SO IT IS.
        """
        output, stable = capture_output(code)
        expected = [-6.2, 0.2, 1.1, 2.2, 3.4]
        output = list(map(lambda x: float(x), output.splitlines()))
        self.assertAlmostEquals(expected, output)



    def test_A_complex_all_02(self):
        code = r"""

        (We're going to find the first ten prime numbers
        and store them into an array)
        
        NAME A NUMBER 10 AS THE NUM_TO_FIND.
        NAME THE NUM_TO_FIND NUMBERS AS THE PRIMES.
        NAME A NUMBER 2 AS THE COUNTER.
        NAME A NUMBER 0 AS THE NUM_FOUND.
        
        WHILST TRUE?

            (WE'VE FOUND TEN PRIMES.  TIME TO GO LEAVE.)
            SHOULD SELFSAME THE NUM_FOUND AND THE NUM_TO_FIND?
                FLEE.
            SO IT IS.
            

            SHOULD SELFSAME THE NUM_FOUND AND 0?
                (WE START AT 2, SO LET'S ADD IT)
                MAKE THE PRIMES'THE NUM_FOUND BE THE COUNTER.
                MAKE THE NUM_FOUND BE THE JOINING OF THE NUM_FOUND AND 1.
            LEST
                (EVERY NUMBER PAST 2 WE SHOULD CHECK)

                NAME A NUMBER 0 AS THE NDX.

                (SEE IF THE NUMBER WE'RE CHECKING IS EVENLY DIVISIBLE
                BY ONE OF THE FOUND PRIMES.  IF IT IS, IT IS NOT PRIME.)
                NAME A TRUTH TRUE AS THE DID_FIND.
                NAME A NUMBER AS THE P.
                WHILST LESSER THE NDX THAN THE NUM_FOUND?
                    MAKE THE P BE THE PRIMES'THE NDX.
                    NAME A NUMBER THE WHOLE SPLIT REMAINDER OF THE COUNTER INTO THE P AS THE REMAINDER.
                    SHOULD SELFSAME THE REMAINDER AND 0?
                        MAKE THE DID_FIND BE FALSE.
                        FLEE.
                    SO IT IS.
                    MAKE THE NDX BE THE JOINING OF THE NDX AND 1.
                SO IT IS.
                SHOULD THE DID_FIND?
                    MAKE THE PRIMES'THE NUM_FOUND BE THE COUNTER.
                    MAKE THE NUM_FOUND BE THE JOINING OF THE NUM_FOUND AND 1.
                SO IT IS.
            SO IT IS.

            MAKE THE COUNTER BE THE JOINING OF THE COUNTER AND 1.
        SO IT IS.

        (OUTPUT THE PRIMES WE FOUND.)
        NAME A NUMBER 0 AS THE NDX.
        WHILST LESSER THE NDX THAN THE NUM_FOUND?   (THE SIZE OF THE PRIMES?)
            REVEAL THE PRIMES'THE NDX.
            MAKE THE NDX BE THE JOINING OF THE NDX AND 1.
        SO IT IS.
        """
        output, stable = capture_output(code)
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        output = list(map(lambda x: int(x), output.splitlines()))
        self.assertEquals(expected, output)

