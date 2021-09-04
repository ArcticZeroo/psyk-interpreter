import unittest
from psyk.interpreter.errors import *


def capture_output(inter_code, to_input=""):
    from psyk.interpreter.interpreter import interpret_intermediate
    import io
    import contextlib
    import sys
    
    old_stdin = sys.stdin

    sys.stdin = io.StringIO(to_input)

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        stable = interpret_intermediate(inter_code, debug=True)
    
    sys.stdin = old_stdin

    return f.getvalue(), stable




class TestIntermediateInterp(unittest.TestCase):

    def test_empty(self):
        code = """
        """
        expected = """"""
        output, symbol_table = capture_output(code)
        self.assertEquals(expected.split(), output.split())


    def test_val_copy_00(self):
        code = """
        VAL_COPY 3 s1
        """
        output, stable = capture_output(code)
        self.assertEqual(3, stable.lookup('s1'))


    def test_val_copy_01(self):
        code = """
        VAL_COPY 3 s1
        VAL_COPY s1 s2
        """
        output, stable = capture_output(code)
        self.assertEqual(3, stable.lookup('s2'))


    def test_val_copy_02(self):
        code = """
        VAL_COPY 3 s1
        VAL_COPY s1 a1
        """
        with self.assertRaises(ParsingError):
            output, stable = capture_output(code)



    def test_output_00(self):
        code = """
        OUT_NUM 3
        """
        expected = "3"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_output_01(self):
        code = """
        OUT_NUM 3
        OUT_CHAR '%n'
        """
        expected = "3\n"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_output_02(self):
        code = """
        OUT_CHAR 'z'
        """
        expected = "z"
        output, stable = capture_output(code)
        self.assertEquals(expected, output)


    def test_inchar_00(self):
        code = """
        IN_CHAR s1
        """
        to_input = 'x'
        output, stable = capture_output(code, to_input)
        self.assertEquals("'x'", stable.lookup('s1'))


    def test_inchar_01(self):
        code = """
        IN_CHAR s1
        """
        to_input = '\n'
        output, stable = capture_output(code, to_input)
        self.assertEquals("'%n'", stable.lookup('s1'))


    def test_mystery_00(self):
        code = """
        RANDOM s3
        """
        output, stable = capture_output(code)
        val = stable.lookup('s3')
        assert -100 <= val <= 100


    def test_math_add_00(self):
        code = """
        VAL_COPY 3 s1
        VAL_COPY 2 s2
        ADD s1 s2 s3
        """
        output, stable = capture_output(code)
        val = stable.lookup('s3')
        self.assertEqual(5, val)


    def test_math_add_01(self):
        code = """
        VAL_COPY 3 s1
        ADD s1 2 s2
        """
        output, stable = capture_output(code)
        val = stable.lookup('s2')
        self.assertEqual(5, val)


    def test_math_add_02(self):
        code = """
        ADD 2 -3 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(-1, val)

    
    def test_math_sub_00(self):
        code = """
        VAL_COPY 3 s1
        VAL_COPY 2 s2
        SUB s1 s2 s3
        """
        output, stable = capture_output(code)
        val = stable.lookup('s3')
        self.assertEqual(1, val)


    def test_math_sub_01(self):
        code = """
        VAL_COPY 3 s1
        SUB s1 2 s2
        """
        output, stable = capture_output(code)
        val = stable.lookup('s2')
        self.assertEqual(1, val)


    def test_math_sub_02(self):
        code = """
        SUB 3 -2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(5, val)


    def test_math_mul_00(self):
        code = """
        VAL_COPY 3 s1
        VAL_COPY 2 s2
        MUL s1 s2 s3
        """
        output, stable = capture_output(code)
        val = stable.lookup('s3')
        self.assertEqual(6, val)


    def test_math_mul_01(self):
        code = """
        VAL_COPY -3 s1
        MUL s1 2 s2
        """
        output, stable = capture_output(code)
        val = stable.lookup('s2')
        self.assertEqual(-6, val)


    def test_math_mul_02(self):
        code = """
        MUL 3 -2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(-6, val)


    def test_math_div_00(self):
        code = """
        VAL_COPY 6 s1
        VAL_COPY 3 s2
        DIV s1 s2 s3
        """
        output, stable = capture_output(code)
        val = stable.lookup('s3')
        self.assertEqual(2, val)


    def test_math_div_01(self):
        code = """
        VAL_COPY -6 s1
        DIV s1 -3 s2
        """
        output, stable = capture_output(code)
        val = stable.lookup('s2')
        self.assertEqual(2, val)


    def test_math_div_02(self):
        code = """
        MUL 3 -2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(-6, val)


    def test_comp_less_00(self):
        code = """
        TEST_LESS 3 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_less_01(self):
        code = """
        TEST_LESS 2 3 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(1, val)


    def test_comp_less_02(self):
        code = """
        TEST_LESS 2 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_gtr_00(self):
        code = """
        TEST_GTR 3 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(1, val)


    def test_comp_gtr_01(self):
        code = """
        TEST_GTR 2 3 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_gtr_02(self):
        code = """
        TEST_GTR 2 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_equ_00(self):
        code = """
        TEST_EQU 3 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_equ_01(self):
        code = """
        TEST_EQU 2 3 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_comp_equ_02(self):
        code = """
        TEST_EQU 2 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(1, val)


    def test_comp_nequ_00(self):
        code = """
        TEST_NEQU 3 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(1, val)


    def test_comp_nequ_01(self):
        code = """
        TEST_NEQU 2 3 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(1, val)


    def test_comp_nequ_02(self):
        code = """
        TEST_NEQU 2 2 s1
        """
        output, stable = capture_output(code)
        val = stable.lookup('s1')
        self.assertEqual(0, val)


    def test_jump_00(self):
        code = """
        VAL_COPY 10 s1
        while-start-0:
        TEST_GTR s1 0 s2
        JUMP_IF_0 s2 while-end-0
        OUT_CHAR 'a'
        SUB s1 1 s1
        JUMP while-start-0
        while-end-0:
        """
        output, stable = capture_output(code)
        self.assertEqual('a'*10, output)


    def test_jump_01(self):
        code = """
        VAL_COPY 5 s1
        VAL_COPY 3 s2
        TEST_GTR s1 s2 s3
        JUMP_IF_0 s3 if-else-0
        OUT_CHAR 'a'
        JUMP if-end-0
        if-else-0:
        OUT_CHAR 'b'
        if-end-0:
        OUT_CHAR 'c'
        """
        output, stable = capture_output(code)
        self.assertEqual('ac', output)


    def test_jump_02(self):
        code = """
        VAL_COPY 0 s1
        VAL_COPY 3 s2
        TEST_GTR s1 s2 s3
        JUMP_IF_0 s3 if-else-0
        OUT_CHAR 'a'
        JUMP if-end-0
        if-else-0:
        OUT_CHAR 'b'
        if-end-0:
        OUT_CHAR 'c'
        """
        output, stable = capture_output(code)
        self.assertEqual('bc', output)


    def test_jump_03(self):
        code = """
        VAL_COPY 10 s1
        start-loop:
        SUB s1 1 s1
        OUT_NUM s1
        TEST_GTR s1 4 s99
        JUMP_IF_NE0 s99 start-loop
        """
        output, stable = capture_output(code)
        self.assertEqual('987654', output)