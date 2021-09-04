from enum import Enum
from typing import List, Optional, Dict, Any, Callable

from psyk.scalar import ScalarAddress, assert_scalar_type, ScalarType, LiteralOrScalar, ArrayIndexScalarAddress
from psyk.symbol_table import CompilerSymbolTable, ScopeData, ScopeType
from psyk.tokens import Tokens, math_nary
from psyk.type_system import TypeData, TypeInteger, TypeChar, TypeNumeric, TypeBool, \
    is_truthy, TypeAny, TypeArray


class Operation(Enum):
    @property
    def instruction(self):
        return self.value

    def __str__(self):
        return self.instruction

    # binary
    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'
    IDIV = 'IDIV'
    MOD = 'MOD'

    # binary, but tests
    EQUAL = 'TEST_EQU'
    NOT_EQUAL = 'TEST_NEQU'
    GREATER = 'TEST_GTR'
    LESS = 'TEST_LESS'
    MIN = 'MIN'
    MAX = 'MAX'

    # unary
    MATH_NEGATE = 'MATH_NEG'
    LOGICAL_NEGATE = 'LOGIC_NEG'

    # unary-ish
    RANDOM = 'RANDOM'

    READ = 'IN_'
    PRINT = 'OUT_'

    PUSH = 'PUSH'
    POP = 'POP'

    LOGICAL_AND = 'AND'
    LOGICAL_OR = 'OR'
    LOGICAL_XOR = 'XOR'

    # assign is its own thing
    ASSIGN = 'VAL_COPY'

    # jumps
    JUMP = 'JUMP'
    JUMP_IF_ZERO = 'JUMP_IF_0'
    JUMP_IF_NOT_ZERO = 'JUMP_IF_NE0'

    # tests
    TEST_EQUAL = 'TEST_EQU'
    TEST_NOT_EQUAL = 'TEST_NEQU'
    TEST_GREATER_THAN = 'TEST_GTR'
    TEST_LESS_THAN = 'TEST_LESS'

    # arrays
    ARRAY_GET_AT_INDEX = 'AR_GET_NDX'
    ARRAY_SET_AT_INDEX = 'AR_SET_NDX'
    ARRAY_GET_SIZE = 'AR_GET_SZ'
    ARRAY_SET_SIZE = 'AR_SET_SZ'
    ARRAY_COPY = 'AR_COPY'


# a set of operators whose signature looks like lhs, rhs, result
BINARY_OPERATIONS = {Operation.ADD, Operation.SUB, Operation.MUL, Operation.DIV, Operation.EQUAL, Operation.NOT_EQUAL,
                     Operation.GREATER, Operation.LESS, Operation.LOGICAL_OR, Operation.LOGICAL_AND,
                     Operation.LOGICAL_XOR}

# a set of operators whose signature looks like expr, result
UNARY_OPERATIONS = {Operation.MATH_NEGATE, Operation.LOGICAL_NEGATE}

JUMP_OPERATIONS = {Operation.JUMP, Operation.JUMP_IF_ZERO, Operation.JUMP_IF_NOT_ZERO}

TOKEN_TO_OPERATION = {
    Tokens.MATH_ADD: Operation.ADD,
    Tokens.MATH_SUB: Operation.SUB,
    Tokens.MATH_DIV: Operation.DIV,
    Tokens.MATH_MUL: Operation.MUL,
    Tokens.MATH_NEGATE: Operation.MATH_NEGATE,
    Tokens.MATH_INTEGER_DIV: Operation.IDIV,
    Tokens.MATH_INTEGER_MOD: Operation.MOD,

    math_nary(Tokens.MATH_ADD): Operation.ADD,
    math_nary(Tokens.MATH_SUB): Operation.SUB,
    math_nary(Tokens.MATH_DIV): Operation.DIV,
    math_nary(Tokens.MATH_MUL): Operation.MUL,
    math_nary(Tokens.MATH_NEGATE): Operation.MATH_NEGATE,

    Tokens.LOGICAL_AND: Operation.LOGICAL_AND,
    Tokens.LOGICAL_OR: Operation.LOGICAL_OR,
    Tokens.LOGICAL_XOR: Operation.LOGICAL_XOR,
    Tokens.LOGICAL_NEGATE: Operation.LOGICAL_NEGATE,
    Tokens.LOGICAL_ALL_TRUE: Operation.LOGICAL_AND,
    Tokens.LOGICAL_ANY_TRUE: Operation.LOGICAL_OR,

    Tokens.COMPARE_EQUAL: Operation.EQUAL,
    Tokens.COMPARE_LESS_THAN: Operation.LESS,
    Tokens.COMPARE_GREATER_THAN: Operation.GREATER,
    Tokens.MIN: Operation.MIN,
    Tokens.MAX: Operation.MAX,

    Tokens.MYSTERY: Operation.RANDOM,
}

OPERATION_REMAP = {
    Operation.LOGICAL_OR: Operation.ADD,
    Operation.LOGICAL_AND: Operation.MUL,
    Operation.LOGICAL_XOR: Operation.TEST_NOT_EQUAL
}

# Maps types to the suffixes for their I/O commands (e.g. OUT_CHAR, IN_CHAR, etc)
_TYPE_TO_COMMAND_SUFFIX: Dict[TypeData, str] = {
    TypeNumeric(): 'NUM',
    TypeChar(): 'CHAR',
}


def get_command_suffix_for_type(type_data: TypeData) -> Optional[str]:
    for possible_type, command_suffix in _TYPE_TO_COMMAND_SUFFIX.items():
        if possible_type.is_other_assignable_to_self(type_data):
            return command_suffix
    return None


def always_get_command_suffix_for_type(type_data: TypeData) -> str:
    suffix = get_command_suffix_for_type(type_data)
    if suffix is None:
        raise ValueError(f'{type_data} could not be assigned to any registered command type')
    return suffix


class _LabelName:
    IfElse = 'if_else'
    IfEnd = 'if_end'
    WhileStart = 'while_start'
    WhileEnd = 'while_end'


HEAP_ADDRESS = ScalarAddress(0, ScalarType.REGULAR)
INITIAL_HEAP_VALUE = 1000


class IntermediateOutput:
    # TODO optimize by having a pool of temp variable locations
    _symbol_table: CompilerSymbolTable
    _current_label_id: int
    _output: List[str]

    def __init__(self, symbol_table: CompilerSymbolTable):
        self._symbol_table = symbol_table
        self._current_label_id = -1
        self._output = []
        self._push_scope(ScopeType.ROOT)
        self.copy(INITIAL_HEAP_VALUE, HEAP_ADDRESS)
        self._symbol_table.set_type_of(HEAP_ADDRESS, TypeInteger())

    @property
    def scoped_current_label_id(self) -> int:
        return self._symbol_table.current_scope.current_label_id

    def _label(self, name: str):
        self._output.append(f'{name}:')

    def _get_label_name(self, name: str, label_id: int = None) -> str:
        return f'{name}_{label_id or self.scoped_current_label_id}'

    def _get_unique_label_name(self, name: str) -> str:
        label_name = self._get_label_name(name)
        self._current_label_id += 1
        return label_name

    def _push_scope(self, scope_type: ScopeType):
        self._current_label_id += 1
        self._symbol_table.push_scope(ScopeData(scope_type, self._current_label_id))

    def _pop_scope(self):
        self._symbol_table.pop_scope()

    def _arg(self, value: LiteralOrScalar) -> LiteralOrScalar:
        if isinstance(value, ArrayIndexScalarAddress):
            result_address = self._symbol_table.register_new_scalar()
            self.array_get_value_at_index(value, value.index, result_address)
            return result_address
        return value

    def _do_safe_output(self, result_address: ScalarAddress, create_output: Callable[[ScalarAddress], None]):
        """
        Performs "safe output", which means that your output can be to an array address or a regular scalar address.
        We don't have the ability to provide symbol-level pointers to arrays (at least not in any clean way I can
        fathom so far), so this is the next best option. The result is copied to a temporary address, then set in
        the array.
        This function can be skipped for output when the result address is known to always or never be an array.
        It can also be skipped if there is no line which appends directly to output. Any function which appends to
        output will call this function, so there's no need to nest.
        :param result_address: The initial result address. This may be a typical scalar or an array-indexed scalar.
        :param create_output: A function which receives the address it should send the result to instead, and performs
            output on that.
        :return: None
        """
        if isinstance(result_address, ArrayIndexScalarAddress):
            with self._symbol_table.acquire_temporary_scalar() as temp_scalar:
                # copy the value to a temporary location first, and then to the array index
                create_output(temp_scalar)
                self.array_set_value_at_index(result_address.array, result_address.index, temp_scalar)
        else:
            create_output(result_address)

    def jump_if(self, operation: Operation, predicate: LiteralOrScalar, label: str):
        if operation == Operation.JUMP:
            raise ValueError(f'Operation must not be JUMP')

        self._symbol_table.assert_access(predicate)
        self._output.append(f'{operation} {self._arg(predicate)} {label}')

    def jump(self, label: str):
        self._output.append(f'{Operation.JUMP} {label}')

    def copy(self, from_value: LiteralOrScalar, to_value: ScalarAddress):
        self._symbol_table.assert_access(from_value)
        self._do_safe_output(to_value,
                             lambda result: self._output.append(f'{Operation.ASSIGN} {self._arg(from_value)} {result}'))
        if isinstance(from_value, ScalarAddress) and not self._symbol_table.has_type(from_value):
            self._symbol_table.set_type_of(to_value, self._symbol_table.get_type_of(from_value))

    def clamp(self, expr: LiteralOrScalar, low: int, high: int, result_address: ScalarAddress = None) -> ScalarAddress:
        """
        Clamp expr between [low, high] inclusive
        :param expr: The expression to clamp
        :param low: The low
        :param high: The high
        :param result_address: The result address for the clampening, if you don't want a temp variable
        """
        self._symbol_table.assert_access(expr)
        with self._symbol_table.acquire_temporary_scalar() as if_predicate_address:
            with self._symbol_table.acquire_or_use_existing_temporary_scalar(result_address) as result_address:
                # if expr < low:
                self.test(Operation.TEST_LESS_THAN, expr, low, if_predicate_address)
                self.if_statement_begin(if_predicate_address, has_else=True)
                #   result = low
                self.copy(low, result_address)
                # else:
                self.else_statement_begin()
                #   if expr > high
                self.test(Operation.TEST_GREATER_THAN, expr, high, if_predicate_address)
                self.if_statement_begin(if_predicate_address, has_else=True)
                #       result = high
                self.copy(high, result_address)
                #   else:
                self.else_statement_begin()
                #       result = expr
                self.copy(expr, result_address)
                self.if_else_statement_end()
                self.if_else_statement_end()
                return result_address

    def find_comparison(self, a: LiteralOrScalar, b: LiteralOrScalar,
                        if_a_less_than_b: Callable, if_b_less_than_a: Callable, if_equal: Callable):
        self._symbol_table.assert_access(a)
        self._symbol_table.assert_access(b)

        with self._symbol_table.acquire_temporary_scalar() as temp_predicate_address:
            # if expr < low:
            self.test(Operation.TEST_LESS_THAN, a, b, temp_predicate_address)
            self.if_statement_begin(temp_predicate_address, has_else=True)
            if_a_less_than_b()
            # else:
            self.else_statement_begin()
            #   if a > b
            self.test(Operation.TEST_GREATER_THAN, a, b, temp_predicate_address)
            self.if_statement_begin(temp_predicate_address, has_else=True)
            if_b_less_than_a()
            #   else:
            self.else_statement_begin()
            if_equal()
            self.if_else_statement_end()
            self.if_else_statement_end()

    def for_loop(self, initial_value: Callable, predicate: Callable[[ScalarAddress], None], update: Callable,
                 body: Callable):
        with self._symbol_table.acquire_temporary_scalar() as predicate_address:
            initial_value()

            def while_loop_predicate():
                predicate(predicate_address)
                return predicate_address

            self.while_loop_begin(predicate=while_loop_predicate)
            body()
            update()
            self.while_loop_end()

    def array_iterate(self, array_address: ScalarAddress, for_each_item: Callable[[ScalarAddress], None],
                      current_item_address: Optional[ScalarAddress] = None):
        assert_scalar_type(array_address, ScalarType.ARRAY)
        self._symbol_table.assert_access(array_address)
        with self._symbol_table.acquire_temporary_scalar() as array_size_address:
            self.array_get_size(array_address, array_size_address)
            with self._symbol_table.acquire_temporary_scalar() as i_address:
                self._symbol_table.set_type_of(i_address, TypeInteger())
                with self._symbol_table.acquire_or_use_existing_temporary_scalar(
                        current_item_address) as current_item_address:
                    self._symbol_table.set_type_of(current_item_address,
                                                   self._symbol_table.get_type_of(array_address).member_type)

                    def body():
                        self.array_get_value_at_index(array_address, i_address, current_item_address)
                        for_each_item(current_item_address)

                    self.for_loop(
                        initial_value=lambda *_: self.copy(0, i_address),
                        predicate=lambda result_address: self.test(Operation.TEST_LESS_THAN, i_address,
                                                                   array_size_address, result_address),
                        update=lambda *_: self.binary_operation(Operation.ADD, i_address, 1, i_address),
                        body=body
                    )

    def min(self, a: LiteralOrScalar, b: LiteralOrScalar, raw_result_address: ScalarAddress):
        self.find_comparison(a, b,
                             if_a_less_than_b=lambda *_: self.copy(a, raw_result_address),
                             if_b_less_than_a=lambda *_: self.copy(b, raw_result_address),
                             if_equal=lambda *_: self.copy(a, raw_result_address))

    def max(self, a: LiteralOrScalar, b: LiteralOrScalar, raw_result_address: ScalarAddress):
        self.find_comparison(a, b,
                             if_a_less_than_b=lambda *_: self.copy(b, raw_result_address),
                             if_b_less_than_a=lambda *_: self.copy(a, raw_result_address),
                             if_equal=lambda *_: self.copy(a, raw_result_address))

    def is_truthy(self, expr: LiteralOrScalar, raw_result_address: ScalarAddress):
        self._symbol_table.assert_access(expr)
        self.test(Operation.TEST_NOT_EQUAL, 0, expr, raw_result_address)

    def binary_operation(self, operation: Operation, lhs: LiteralOrScalar, rhs: LiteralOrScalar,
                         raw_result_address: ScalarAddress):
        if not self._symbol_table.has_type(raw_result_address):
            self._symbol_table.set_type_of(raw_result_address, TypeAny())

        if operation in OPERATION_REMAP:
            return self.binary_operation(OPERATION_REMAP[operation], lhs, rhs, raw_result_address)

        if operation == Operation.MIN:
            return self.min(lhs, rhs, raw_result_address)

        if operation == Operation.MAX:
            return self.max(lhs, rhs, raw_result_address)

        self._symbol_table.assert_access(lhs)
        self._symbol_table.assert_access(rhs)
        self._do_safe_output(raw_result_address,
                             lambda result: self._output.append(
                                 f'{operation} {self._arg(lhs)} {self._arg(rhs)} {result}'))

    def test(self, operation: Operation, lhs: LiteralOrScalar, rhs: LiteralOrScalar, raw_result_address: ScalarAddress):
        self._symbol_table.assert_access(lhs)
        self._symbol_table.assert_access(rhs)
        self.binary_operation(operation, lhs, rhs, raw_result_address)

    def unary_operation(self, operation: Operation, expr: LiteralOrScalar, raw_result_address: ScalarAddress):
        self._symbol_table.assert_access(expr)

        def run(result: ScalarAddress):
            if operation == Operation.MATH_NEGATE:
                self._output.append(f'{Operation.MUL} -1 {self._arg(expr)} {result}')
                return

            # 1 - 1 = 0 * -1 = 0, 0 - 1 = -1 * -1 = 1
            if operation == Operation.LOGICAL_NEGATE:
                self._symbol_table.set_type_of(result, TypeInteger())
                # temp = expr - 1
                self.binary_operation(Operation.SUB, expr, 1, result)
                # temp  *= -1
                self.binary_operation(Operation.MUL, result, -1, result)
                return

            raise ValueError(f'Operation {operation.name} is currently unsupported')

        self._do_safe_output(raw_result_address, run)

    def if_statement_begin(self, predicate: LiteralOrScalar, has_else: bool = False):
        """
        Called when an if statement begins. Given a LiteralOrScalar representing the value of the predicate,
        everything until else_statement_begin or if_else_statement_end are called (if there is an else or no else
        respectively) will be jumped over when predicate == 0.
        This must ALWAYS be called at the beginning of an if statement
        :param predicate: The predicate to test for in the if statement
        :param has_else: Whether this if statement has an else after it
        """
        self._symbol_table.assert_access(predicate)
        # push an if-else-statement scope
        self._push_scope(ScopeType.IF_ELSE_STATEMENT)
        label_base_name = _LabelName.IfEnd if not has_else else _LabelName.IfElse
        # jump to the else statement if the condition is false
        self.jump_if(Operation.JUMP_IF_ZERO, predicate, self._get_label_name(label_base_name))
        # OK, this is kind of stupid, right? We already pushed a scope.
        # But I have decided to create two scopes for each if-else block, since if, else, and the if-else block
        # all need their own individual scopes
        # push an if scope
        self._push_scope(ScopeType.IF)

    def else_statement_begin(self):
        """
        Called when an if statement ends, and it is followed by an else statement.
        The if statement will jump over everything until if_else_statement_end is called.
        """
        # kill the if-scope
        self._pop_scope()
        # end the previous if statement by jumping past the else
        self.jump(self._get_label_name(_LabelName.IfEnd))
        # assign the same label that would have been used as a jump target inside if_statement_begin
        self._label(self._get_label_name(_LabelName.IfElse))
        # push an else scope
        self._push_scope(ScopeType.ELSE)

    def if_else_statement_end(self):
        """
        Called when an if statement ends, AND its corresponding else statement (if any) has also ended.
        """
        # pop the if OR else scope
        self._pop_scope()
        self._label(self._get_label_name(_LabelName.IfEnd))
        # pop the if-else-statement scope
        self._pop_scope()

    def while_loop_begin(self, predicate: Callable[[], ScalarAddress]):
        self._push_scope(ScopeType.WHILE)
        # mark this position as the start of the loop
        self._label(self._get_label_name(_LabelName.WhileStart))
        predicate_address = predicate()
        self._symbol_table.assert_access(predicate_address)
        # if (!predicate) jump to end
        self.jump_if(Operation.JUMP_IF_ZERO, predicate_address, self._get_label_name(_LabelName.WhileEnd))

    def while_loop_end(self):
        self.jump(self._get_label_name(_LabelName.WhileStart))
        self._label(self._get_label_name(_LabelName.WhileEnd))
        self._pop_scope()

    def while_loop_break(self):
        while_scope = self._symbol_table.find_scope_of_type(ScopeType.WHILE)
        if while_scope is None:
            raise ValueError('No while loop scope exists')
        self.jump(self._get_label_name(_LabelName.WhileEnd, while_scope.current_label_id))

    def get_random(self, raw_result_address: ScalarAddress):
        self._do_safe_output(raw_result_address, lambda result: self._output.append(f'{Operation.RANDOM} {result}'))

    def read_stdin(self, variable_type: TypeData, raw_result_address: ScalarAddress):
        command_suffix = always_get_command_suffix_for_type(variable_type)
        self._do_safe_output(raw_result_address,
                             lambda result: self._output.append(f'{Operation.READ}{command_suffix} {result}'))

    def print_stdout_array(self, variable_type: TypeData, source: LiteralOrScalar):
        if isinstance(source, int):
            raise TypeError('Array must be an address')
        if not isinstance(variable_type, TypeArray):
            raise TypeError('Type must be an array type')

        self._symbol_table.assert_access(source)
        self.array_iterate(source,
                           lambda current_item_address: self.print_stdout(variable_type.member_type,
                                                                          current_item_address))

    def print_stdout(self, variable_type: TypeData, source: LiteralOrScalar):
        self._symbol_table.assert_access(source)
        if TypeArray(TypeAny()).is_other_assignable_to_self(variable_type):
            self.print_stdout_array(variable_type, source)
            return
        command_suffix = always_get_command_suffix_for_type(variable_type)
        self._output.append(f'{Operation.PRINT}{command_suffix} {self._arg(source)}')

    def array_get_size(self, array: ScalarAddress, raw_result_address: ScalarAddress):
        assert_scalar_type(array, ScalarType.ARRAY)
        self._symbol_table.assert_access(array)

        def run(result: ScalarAddress):
            self._output.append(f'{Operation.ARRAY_GET_SIZE} {array} {result}')
            self._symbol_table.set_type_if_none(result, TypeInteger())

        self._do_safe_output(raw_result_address, run)

    def array_set_size(self, array: ScalarAddress, size: LiteralOrScalar):
        assert_scalar_type(array, ScalarType.ARRAY)
        self._symbol_table.assert_access(array)
        self._output.append(f'{Operation.ARRAY_SET_SIZE} {array} {self._arg(size)}')

    def array_set_value_at_index(self, array: ScalarAddress, index: int, value: LiteralOrScalar):
        assert_scalar_type(array, ScalarType.ARRAY)
        self._symbol_table.assert_access(array)
        self._output.append(f'{Operation.ARRAY_SET_AT_INDEX} {array} {self._arg(index)} {self._arg(value)}')

    def array_get_value_at_index(self, array: ScalarAddress, index: LiteralOrScalar,
                                 raw_result_address: LiteralOrScalar):
        assert_scalar_type(array, ScalarType.ARRAY)
        self._symbol_table.assert_access(array)
        self._do_safe_output(raw_result_address,
                             lambda result: self._output.append(
                                 f'{Operation.ARRAY_GET_AT_INDEX} {array} {self._arg(index)} {result}'))

    def create_array(self, size_address: LiteralOrScalar, array_result_address: ScalarAddress):
        assert_scalar_type(array_result_address, ScalarType.ARRAY)

        self.copy(HEAP_ADDRESS, array_result_address)
        self.binary_operation(Operation.ADD, HEAP_ADDRESS, size_address, HEAP_ADDRESS)
        # size in memory is 1 larger due to the size position
        self.binary_operation(Operation.ADD, HEAP_ADDRESS, 1, HEAP_ADDRESS)
        self.array_set_size(array_result_address, size_address)
        self._symbol_table.set_type_if_none(array_result_address, TypeArray(TypeAny()))

    def format_scalar(self, scalar: ScalarAddress, scalar_type: TypeData):
        requires_truthy_output = TypeBool()
        if requires_truthy_output.is_other_assignable_to_self(scalar_type, can_coerce=False):
            # todo make this better lol
            if not isinstance(scalar, ArrayIndexScalarAddress):
                self._symbol_table.set_type_of(scalar, scalar_type)
            # this doesn't seem like it may be needed anymore now that we have actual type checking
            # self.is_truthy(scalar, scalar)

    def format_literal(self, value: Any, value_type: TypeData):
        # replace any of these with unions if necessary ever
        can_output_raw = TypeNumeric()
        requires_truthy_output = TypeBool()
        requires_quoted_output = TypeChar()
        # bool is assignable to numeric, so check this first
        if requires_truthy_output.is_other_assignable_to_self(value_type, can_coerce=False):
            return self.format_literal(1 if is_truthy(value) else 0, TypeInteger())
        if can_output_raw.is_other_assignable_to_self(value_type, can_coerce=False):
            return str(value)
        if (requires_quoted_output.is_other_assignable_to_self(value_type, can_coerce=False)
                and not str(value).startswith("'")):
            return f"'{value}'"
        return value

    def serialize(self) -> str:
        # extra newline is needed since the parser definition is incorrect for the interpreter
        return '\n'.join(self._output + [''])
