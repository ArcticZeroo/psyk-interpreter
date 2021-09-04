import unittest



def capture_output(src_code, to_input=""):
    from psyk.project import psyk_to_intermediate
    from psyk.interpreter.interpreter import interpret_intermediate
    import io
    import contextlib
    import sys
    
    inter_code = psyk_to_intermediate(src_code)

    old_stdin = sys.stdin

    sys.stdin = io.StringIO(to_input)

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        stable = interpret_intermediate(inter_code, debug=True)
    
    sys.stdin = old_stdin

    return f.getvalue(), stable


class TestIntermediateCode(unittest.TestCase):
    

     # ==================================================================== NOP
    def test_00_empty(self):        
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



    def test_01_comments(self):
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

    def test_02_no_empty_expr_list(self):
        code = """
        NAME A NUMBER THE JOINING OF ALL OF TOGETHER AS THE FOO.        
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)


    def test_03_undeclared_ident(self):
        code = """
        SHOW THE FOO!
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)





    # ==================================================================== EXPR Only
    def test_04_int(self):
        code = """
        3.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        ,3.
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

        code = """
        3!
        """
        expected = ""
        output, stable = capture_output(code)
        self.assertEquals(expected, output)



    # ==================================================================== OUTPUT OPS
    def test_05_outnum_00(self):
        code = """
        REVEAL 5.
        """
        expected = "5\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_06_outnum_01(self):
        code = """
        REVEAL 5, 10.
        """
        expected = "510\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

    
    def test_07_outnum_0(self):
        code = """
        SHOW THE JOINING OF 4 AND 20.
        """
        expected = "24"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    # ==================================================================== Basic Assignment
    def test_08_init_int_00(self):
        code = """
        NAME A NUMBER 3 AS THE foo.  
        REVEAL THE foo!
        """
        expected = "3\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)

    
    def test_09_init_no_as(self):
        code = """
        NAME A NUMBER 3 THE foo.  
        """
        with self.assertRaises(Exception):
            output, stable = capture_output(code)
 
    
    def test_10_declaration_assign(self):
        code = """
        NAME A NUMBER AS THE number.  
        MAKE THE number BE -2.  
        REVEAL THE number!
        """
        expected = "-2\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_11_assign_chain(self):
        code = """
        NAME A NUMBER AS THE foo.  NAME A NUMBER AS THE bar.
        MAKE THE foo BE MAKE THE bar BE 42.
        REVEAL THE foo!
        REVEAL THE bar!
        """
        expected = "42\n42\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    # ==================================================================== MATH OPERATORS

    # Negation
    def test_12_math_negation_00(self):
        code = """
        SHOW THE NEGATION OF 12.
        """
        expected = "-12"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))


    def test_13_math_negation_01(self):
        code = """
        SHOW THE NEGATION OF -42.
        """
        expected = "42"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))

    # ADD
    def test_14_math_add_00(self):
        code = """
        SHOW THE JOINING OF 10 AND 3!
        """
        expected = "13"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))   


    def test_15_math_add_01(self):
        code = """
        SHOW THE JOINING OF -10 AND 3!
        """
        expected = "-7"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))   


    # SUB
    def test_16_math_sub_00(self):
        code = """
        SHOW THE REDUCTION OF 10 BY 3!
        """
        expected = "7"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))   


    def test_17_math_sub_01(self):
        code = """
        SHOW THE REDUCTION OF -10 BY -3!
        """
        expected = "-7"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))  


    #MUL
    def test_18_math_mul_00(self):
        code = """
        SHOW THE CROSS OF 10 WITH 5!
        """
        expected = "50"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))   


    def test_19_math_mul_01(self):
        code = """
        SHOW THE CROSS OF -10 WITH -3!
        """
        expected = "30"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))  
    

    # DIV
    def test_20_math_div_00(self):
        code = """
        SHOW THE SPLIT OF 10 INTO 5!
        """
        expected = "2"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))   


    def test_21_math_div_01(self):
        code = """
        SHOW THE SPLIT OF -10 INTO -5!
        """
        expected = "2"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))  
    

    # N-ARY ADD
    def test_22_math_nary_add_00(self):
        code = """
        SHOW THE JOINING OF ALL OF 1 AND 2 AND 3 AND 10 TOGETHER.
        """
        expected = "16"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))  


    def test_23_math_nary_add_01(self):
        code = """
        SHOW THE JOINING OF ALL OF 1, -3, 3, -1 TOGETHER.
        """
        expected = "0"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))  


    # N-ARY MUL
    def test_24_math_nary_mul_00(self):
        code = """
        SHOW THE CROSS OF ALL OF 1 AND 2 AND 3 AND 10 TOGETHER.
        """
        expected = "60"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))  


    def test_25_math_nary_mul_01(self):
        code = """
        SHOW THE CROSS OF ALL OF -1, 1, 2, -2, -1 TOGETHER.
        """
        expected = "-4"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))  



    # ==================================================================== LOGIC OPERATORS

    # NOT
    def test_26_logic_not_00(self):
        code = """
        SHOW THE OPPOSITE OF 1.
        """
        output, stable = capture_output(code)
        self.assertEquals(0, int(float(output))) 


    def test_27_logic_not_01(self):
        code = """
        SHOW THE OPPOSITE OF 0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    # AND
    def test_28_logic_and_00(self):
        code = """
        SHOW BOTH OF 1 AND 2.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_29_logic_and_01(self):
        code = """
        SHOW BOTH OF 1 AND 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_30_logic_and_02(self):
        code = """
        SHOW BOTH OF 0 AND 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # OR
    def test_31_logic_or_00(self):
        code = """
        SHOW EITHER OF 1 OR 2.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_32_logic_or_01(self):
        code = """
        SHOW EITHER OF 1 OR 0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_33_logic_or_02(self):
        code = """
        SHOW EITHER OF 0 OR 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # XOR
    def test_34_logic_xor_00(self):
        code = """
        SHOW ONE OF 1 OR 2.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_35_logic_xor_01(self):
        code = """
        SHOW ONE OF 1 OR 0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_36_logic_xor_02(self):
        code = """
        SHOW ONE OF 0 OR 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # N-ary AND
    def test_37_logic_nary_and_00(self):
        code = """
        SHOW THE ENTIRETY OF 1, 2, 3, 4 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_38_logic_nary_and_01(self):
        code = """
        SHOW THE ENTIRETY OF 1, 0, 3, 4 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_39_logic_nary_and_02(self):
        code = """
        SHOW THE ENTIRETY OF 0, 0, 0, AND 0 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # N-ary OR
    def test_40_logic_nary_or_00(self):
        code = """
        SHOW SOME OF 1, 2, 3, 4 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_41_logic_nary_or_01(self):
        code = """
        SHOW SOME OF 1, 0, 3, 4 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_42_logic_nary_or_02(self):
        code = """
        SHOW SOME OF 0, 0, 0, 0 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # ==================================================================== COMPARE OPERATORS

    # EQU
    def test_43_compare_equ_00(self):
        code = """
        SHOW SELFSAME 1 AND 1.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_44_compare_equ_01(self):
        code = """
        SHOW SELFSAME 1 AND 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # LESS
    def test_45_compare_less_00(self):
        code = """
        SHOW LESSER 1 THAN 1.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_46_compare_less_01(self):
        code = """
        SHOW LESSER 1 THAN 0.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_47_compare_less_02(self):
        code = """
        SHOW LESSER 0 THAN 2.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    # GREATER
    def test_48_compare_greater_00(self):
        code = """
        SHOW GREATER 1 THAN 1.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    def test_49_compare_greater_01(self):
        code = """
        SHOW GREATER 1 THAN 0.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output))) 


    def test_50_compare_greater_02(self):
        code = """
        SHOW GREATER 0 THAN 2.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output))) 


    # ==================================================================== Input OPERATORS

    # Random
    def test_51_random_00(self):
        code = """
        SHOW MYSTERY!
        """
        for k in range(0,10):            
            output, stable = capture_output(code)
            value = int(float(output))
            assert -100 <= value <= 100


    # Input Char
    def test_52_inchar_00(self):
        code = """
        SHOW SUMMONED!
        """
        output, stable = capture_output(code, "a")
        self.assertEqual("a", output)


    def test_53_inchar_01(self):
        code = """
        SHOW SUMMONED, SUMMONED, SUMMONED!
        """
        output, stable = capture_output(code, "axy")
        self.assertEqual("axy", output)






    # ==================================================================== Assignment

    def test_54_assign_add(self):
        code = """
        NAME A NUMBER AS THE foo.  
        MAKE THE foo BE THE JOINING OF 2 AND 20.
        SHOW THE foo.
        """
        expected = "22"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))


    def test_55_assign_sub(self):
        code = """
        NAME A NUMBER AS THE foo.  
        MAKE THE foo BE THE REDUCTION OF 18 BY 4.
        SHOW THE foo.
        """
        expected = "14"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(output))


    def test_56_assign_mul(self):
        code = """
        NAME A NUMBER AS THE foo.  
        MAKE THE foo BE THE CROSS OF 11 WITH -4.
        SHOW THE foo.
        """
        expected = "-44"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))


    def test_57_assign_div(self):
        code = """
        NAME A NUMBER AS THE foo.  
        MAKE THE foo BE THE SPLIT OF 20 INTO 5.
        SHOW THE foo.
        """
        expected = "4"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))


    def test_58_assign_nary_00(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE THE JOINING OF ALL OF 1 AND 2 AND 3 AND 10 TOGETHER.
        SHOW THE FOO.
        """
        expected = "16"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))


    def test_59_assign_nary_01(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE THE JOINING OF ALL OF 1, 2, 3, 20 TOGETHER.
        SHOW THE FOO.
        """
        expected = "26"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))



    def test_60_assign_nary_02(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE THE CROSS OF ALL OF 1, 5, AND -4 TOGETHER.
        SHOW THE FOO.
        """
        expected = "-20"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))


    
    # ==================================================================== Complex
    
    def test_61_complex_00(self):
        code = """
        NAME A NUMBER THE CROSS OF 2 WITH 20 AS THE FOO.
        MAKE THE FOO BE THE REDUCTION OF THE FOO BY 10.
        MAKE THE FOO BE THE SPLIT OF THE FOO INTO 2.
        REVEAL THE FOO!
        """        
        expected = "15"
        output, stable = capture_output(code)
        self.assertEquals(int(expected), int(float(output)))


    def test_62_complex_01(self):
        code = """
        NAME A NUMBER THE CROSS OF 2 WITH 20 AS THE FOO.
        NAME A NUMBER THE JOINING OF 2 AND 20 AS THE BAR.
        SHOW GREATER THE FOO THAN THE BAR.
        """        
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output)))


    def test_63_complex_02(self):
        code = """
        NAME A NUMBER THE JOINING OF ALL OF 10, 20, 30 AND 40 TOGETHER AS THE SUM.
        MAKE THE SUM BE THE CROSS OF THE SUM WITH 10.
        MAKE THE SUM BE THE SPLIT OF THE SUM INTO 5.
        SHOW THE SUM!
        """        
        output, stable = capture_output(code)
        self.assertEqual(200, int(float(output)))


    def test_64_complex_03(self):
        code = """
        NAME A NUMBER THE CROSS OF 10 WITH THE JOINING OF 5 AND 5 AS THE COMBINED.
        SHOW THE SPLIT OF THE COMBINED INTO THE NEGATION OF 2.
        """        
        output, stable = capture_output(code)
        self.assertEqual(-50, int(float(output)))


    def test_65_complex_04(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE GREATER 20 THAN 10.
        SHOW THE CROSS OF THE FOO WITH 10.
        """        
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output)))


    def test_66_complex_05(self):
        code = """
        NAME A NUMBER THE JOINING OF MYSTERY AND 10 AS THE MYSTERIOUS.
        REVEAL THE MYSTERIOUS!
        """        
        output, stable = capture_output(code)
        assert 200 > int(float(output))


    def test_67_complex_06(self):
        code = """
        NAME A NUMBER 3 AS THE FOO.
        NAME A NUMBER 5 AS THE BAR.
        SHOW SELFSAME 8 AND THE JOINING OF THE FOO AND THE BAR.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output)))


    def test_68_complex_07(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE THE OPPOSITE OF SELFSAME 3 AND 3.
        SHOW THE FOO!
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output)))


    def test_69_complex_08(self):
        code = """
        SHOW THE JOINING OF 3 AND THE SPLIT OF 10 INTO THE NEGATION OF THE CROSS OF -1 WITH 2.
        """
        output, stable = capture_output(code)
        self.assertEqual(8, int(float(output)))

    
    def test_70_complex_09_H(self):
        code = """
        SHOW THE OPPOSITE OF THE ENTIRETY OF GREATER 2 THAN 1 AND GREATER 5 THAN 1 AND LESSER 1 THAN 7 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output)))


    def test_71_complex_10_H(self):
        code = """
        SHOW THE JOINING OF ALL OF 1 AND THE CROSS OF 3 WITH THE SPLIT OF 20 INTO -10 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(-5, int(float(output)))


    def test_72_complex_10_H(self):
        code = """
        NAME A NUMBER 3 AS THE THREE.
        NAME A NUMBER 5 AS THE FIVE.
        NAME A NUMBER -10 AS THE NEG_TEN.
        SHOW THE NEGATION OF THE CROSS OF ALL OF THE THREE AND THE NEGATION OF THE FIVE AND THE NEG_TEN TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(-150, int(float(output)))


    def test_73_complex_10_H(self):
        code = """
        SHOW THE JOINING OF ALL OF 1 AND 2 AND THE JOINING OF ALL OF 30 AND 40 TOGETHER TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(73, int(float(output)))


    def test_74_complex_11_H(self):
        code = """
        REVEAL SOME OF GREATER 1 THAN 2 AND LESSER 1 THAN 2 AND SELFSAME 1 AND 2 TOGETHER.
        REVEAL THE ENTIRETY OF GREATER 1 THAN 2 AND LESSER 1 THAN 2 AND SELFSAME 1 AND 2 TOGETHER.
        """
        output, stable = capture_output(code)
        test_or, test_and = output.split()
        self.assertNotEqual(0, int(test_or))
        self.assertEqual(0, int(test_and))


    def test_75_complex_12_H(self):
        code = """
        SHOW THE NEGATION OF THE JOINING OF ALL OF GREATER 3 THAN 5 AND GREATER 3 THAN 10 AND GREATER 3 THAN 300 TOGETHER.
        """
        output, stable = capture_output(code)
        self.assertEqual(0, int(float(output)))

    
    def test_76_complex_13_H(self):
        code = """
        NAME A NUMBER 42 AS THE FOO.
        NAME A NUMBER THE JOINING OF THE FOO AND THE NEGATION OF 42 AS THE ZERO.
        MAKE THE FOO BE THE JOINING OF THE ZERO AND -10.
        SHOW THE NEGATION OF THE FOO.
        """
        output, stable = capture_output(code)
        self.assertEqual(10, int(float(output)))
    

    def test_77_complex_14_H(self):
        code = """
        REVEAL THE SPLIT OF 100 INTO THE SPLIT OF 10 INTO 2.
        REVEAL GREATER 2 THAN THE SPLIT OF 20 INTO 10.
        """
        output, stable = capture_output(code)
        first, second = output.split()
        self.assertEqual(20, int(float(first)))
        self.assertEqual(0, int(float(second)))


    def test_78_complex_15_H(self):
        code = """
        SHOW SELFSAME THE JOINING OF 5 AND 5 AND THE SPLIT OF 100 INTO 10.
        """
        output, stable = capture_output(code)
        self.assertNotEqual(0, int(float(output)))


    def test_79_complex_16_H(self):
        code = """
        NAME A NUMBER AS THE FOO.
        MAKE THE FOO BE 3.
        REVEAL THE FOO.
        MAKE THE FOO BE 6.
        REVEAL THE FOO.
        MAKE THE FOO BE THE CROSS OF THE FOO WITH -2.
        REVEAL THE FOO.
        """
        output, stable = capture_output(code)
        outs = list(map(lambda x: int(float(x)), output.split()))
        self.assertEquals([3, 6, -12], outs)