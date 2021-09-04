import re
from .errors import *

class InterpreterST():

    def __init__(self):
        self.labels = {}
        self.memory = {}
        self.ip = 0
        self.nextHeapLoc = 10000

    def var2loc(self, var):
        if not self.is_var(var):
            raise Expection('Expected var')
        return int(var[1:])


    def val_copy(self, src, dst):
        loc_dst = self.var2loc(dst)
        self.memory[loc_dst] = self.lookup(src, dequote=False)



    def is_var(self, symb):
        if not isinstance(symb, str):
            return False
        return re.match(r'^[AaSs]\d+', symb) != None


    def is_svar(self, symb):
        if not isinstance(symb, str):
            return False
        return re.match(r'^[Ss]\d+', symb) != None


    def is_avar(self, symb):
        if not isinstance(symb, str):
            return False
        return re.match(r'^[Aa]\d+', symb) != None


    def lookup(self, symb, dequote=True):
        if self.is_var(symb): #It's a variable
            loc = self.var2loc(symb)
            if loc not in self.memory:
                raise UninitializedMemoryRequestError(symb)
            to_return = self.memory[loc]
            if isinstance(to_return, str) and dequote:
                to_return = to_return[1:-1]
            return to_return
        else:
            # It's a value; if it's not a string, return it
            # If it is a string, see if it is a char literal and
            # try to convert it if it is not
            if not isinstance(symb, str):
                return symb
            elif symb[0] == '\'':
                return symb[1:-1] if dequote else symb # It's a char literal
            else:  #Try to convert the string to a number
                try: 
                    return int(symb) 
                except:
                    return float(symb)
    

    def __getitem__(self, ndx):
        if not isinstance(ndx, int):
            raise TypeError('Symbol table indexing requires an integer.')
        if not ndx in self.memory:
            raise UninitializedMemoryRequestError(f'Index {ndx}')
        return self.memory[ndx]


    def __setitem__(self, ndx, val):
        if not isinstance(ndx, int):
            raise TypeError('Symbol table indexing requires an integer.')
        self.memory[ndx] = val


    def __delitem__(self, ndx):
        if not isinstance(ndx, int):
            raise TypeError('Symbol table indexing requires an integer.')
        del self.memory[ndx]



    def next(self):
        self.ip += 1


    def jump_label(self, label):
        if label in self.labels:
            self.ip = self.labels[label] + 1
        else:
            raise LabelNotFoundError(f'Unable to find label {label}')

    
    def add_label(self, label, line):
        self.labels[label] = line

