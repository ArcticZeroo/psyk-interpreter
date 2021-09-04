from .getch import getch
from random import randint
from .errors import *

class ASTNode():
    def __init__(self, children):
        self._returned = None
        self.children = children

    def compile(self, symbol_table, output=[]):
        raise NotImplementedError('ASTNode compile is not implemented')

    def interpret(self, symbol_table):
        raise NotImplementedError('ASTNode interpret is not implemented')


class CommandListNode(ASTNode):
    """
    children: a list of commands
    """
    def interpret(self, symbol_table):
        for child in self.children:
            child.interpret(symbol_table)



class ValCopyNode(ASTNode):
    """
    children[0] : number
    children[1] : svar | avar
    """
    def interpret(self, symbol_table):
        src = symbol_table.lookup(self.children[0], dequote=False)
        dst = self.children[1]
        symbol_table.val_copy(src, dst)
        symbol_table.next()



class MathBinaryOpNode(ASTNode):
    """
    children[0]: op
    children[1]: number
    children[2]: number
    children[3]: svar
    """
    def interpret(self, symbol_table):
        lhs = symbol_table.lookup(self.children[1])
        rhs = symbol_table.lookup(self.children[2])
        op = self.children[0]
        dst = self.children[3]
        if op == 'ADD':
            result = lhs + rhs
        elif op == 'SUB':
            result = lhs - rhs
        elif op == 'MUL':
            result = lhs * rhs
        elif op == 'DIV':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs / rhs
        elif op == 'IDIV':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs // rhs
        elif op == 'MOD':
            if rhs == 0:
                raise DivisionByZeroError()
            result = lhs % rhs
        symbol_table.val_copy(result, dst)
        symbol_table.next()


class CompareBinaryOpNode(ASTNode):
    """
    children[0]: op
    children[1]: number
    children[2]: number
    children[3]: svar
    """
    def interpret(self, symbol_table):
        lhs = symbol_table.lookup(self.children[1])
        rhs = symbol_table.lookup(self.children[2])
        op = self.children[0]
        dst = self.children[3]
        if op == 'TEST_EQU':
            result = int(lhs == rhs)
        elif op == 'TEST_NEQU':
            result = int(lhs != rhs)
        elif op == 'TEST_GTR':
            result = int(lhs > rhs)
        elif op == 'TEST_LESS':
            result = int(lhs < rhs)
        symbol_table.val_copy(result, dst)
        symbol_table.next()


class JumpUncondNode(ASTNode):
    """
    children[0] = label
    """
    def interpret(self, symbol_table):
        symbol_table.jump_label(self.children[0])



class JumpCondNode(ASTNode):
    """
    children[0] = cond_type
    children[1] = value
    children[2] = label
    """
    def interpret(self, symbol_table):
        cond_type = self.children[0]
        value = symbol_table.lookup(self.children[1])
        label = self.children[2]
        if cond_type == 'JUMP_IF_0':
            if value == 0:
                symbol_table.jump_label(label)
                return
        elif cond_type == 'JUMP_IF_NE0':
            if value != 0:
                symbol_table.jump_label(label)
                return
        symbol_table.next()


class PrintNumNode(ASTNode):
    """
    children[0] : number
    """
    def interpret(self, symbol_table):
        lhs = symbol_table.lookup(self.children[0])
        print(symbol_table.lookup(lhs), end='')
        symbol_table.next()


class PrintCharNode(ASTNode):
    """
    children[0] : char
    """
    def interpret(self, symbol_table):
        lhs = symbol_table.lookup(self.children[0], dequote=True)
        if lhs == r'%n':
            lhs = '\n'
        elif lhs == r'%%':
            lhs = '%'
        elif lhs == r'%t':
            lhs = '\t'
        elif lhs == r'%\'':
            lhs = '\''
        print(lhs, end='')
        symbol_table.next()



class InputCharNode(ASTNode):
    """
    children[0]: svar to store the data
    """
    def interpret(self, symbol_table):
        ch = getch()
        if ch == '\t':
            ch = '%t'
        elif ch == '\n':
            ch = '%n'
        elif ch == "'":
            ch = "%'"
        dst = self.children[0]
        to_store = f"'{ch}'"
        symbol_table.val_copy(to_store, dst)
        symbol_table.next()



class InputMysteryNode(ASTNode):
    """
    children[0]: svar to store the data
    """
    def interpret(self, symbol_table):
        val = randint(-100,100)
        dst = self.children[0]
        symbol_table.val_copy(val, dst)
        symbol_table.next()



class ArrayGetSize(ASTNode):
    """
    children[0] : avar
    children[1] : svar
    """
    def interpret(self, symbol_table):
        avar, svar = self.children
        loc = symbol_table.lookup(avar)
        sz = symbol_table[loc]
        symbol_table.val_copy(sz, svar)
        symbol_table.next()



class ArraySetSize(ASTNode):
    """
    children[0] : avar
    children[1] : number
    """
    def interpret(self, symbol_table):
        avar, num = self.children
        loc = symbol_table.lookup(avar)
        sz = symbol_table.lookup(num)
        symbol_table[loc] = sz
        symbol_table.next()





class ArrayGetNdx(ASTNode):
    """
    children[0] : avar
    children[1] : number ndx
    children[1] : svar dst
    """
    def interpret(self, symbol_table):
        avar, ndx, dst = self.children
        loc = symbol_table.lookup(avar)
        loc += symbol_table.lookup(ndx)
        loc += 1
        symbol_table.val_copy(symbol_table[loc], dst)
        symbol_table.next()



class ArraySetNdx(ASTNode):
    """
    children[0] : avar
    children[1] : number
    children[2] : number
    """
    def interpret(self, symbol_table):
        avar, svar, val = self.children
        loc = symbol_table.lookup(avar)
        loc += symbol_table.lookup(svar)
        loc += 1
        symbol_table[loc] =  symbol_table.lookup(val, dequote=False)
        symbol_table.next()



class ArrayCopy(ASTNode):
    """
    children[0] : avar src
    children[1] : avar dst
    """
    def interpret(self, symbol_table):
        src, dst = self.children
        loc_src = symbol_table.lookup(src)
        loc_dst = symbol_table.lookup(dst)
        sz = symbol_table[loc_src]
        symbol_table[loc_dst] = sz
        for k in range(0,sz):
            symbol_table[loc_dst+k+1] = symbol_table[loc_src+k+1]
        symbol_table.next()
        