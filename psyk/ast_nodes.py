import abc
from typing import Generic, TypeVar, Tuple, Any, Optional, List

from psyk.context import CompilerContext
from psyk.intermediate_output import Operation
from psyk.symbol_table import SymbolType
from psyk.type_system import TypeData, TypeAny, TypeInteger, TypeFloat, TypeNumeric, TypeChar, TypeBool, \
    TypeNull, assert_is_assignable, TypeArray
from psyk.scalar import ScalarAddress, ArrayIndexScalarAddress, ScalarType

TChildren = TypeVar('TChildren', bound=Tuple)
TCompileResult = TypeVar('TCompileResult')


# region Base Classes
class ASTNode(Generic[TChildren], abc.ABC):
    children: TChildren

    def __init__(self, children: Optional[TChildren] = None):
        self.children = children

    @abc.abstractmethod
    def compile(self, context: CompilerContext) -> ScalarAddress:
        pass


class CommandList(ASTNode[List[ASTNode]]):
    def compile(self, context: CompilerContext) -> ScalarAddress:
        for child in self.children:
            child.compile(context)
        return ScalarAddress.null()


class Expr(ASTNode[TChildren], Generic[TChildren], abc.ABC):
    @abc.abstractmethod
    def compile(self, context: CompilerContext) -> ScalarAddress:
        pass


class Statement(ASTNode[TChildren], Generic[TChildren], abc.ABC):
    @abc.abstractmethod
    def compile(self, context: CompilerContext) -> None:
        pass


# endregion


class ExprLiteral(Expr[Tuple[str, TypeData]]):
    @property
    def raw_value(self) -> str:
        return self.children[0]

    @property
    def value(self):
        if isinstance(self.type, TypeInteger):
            return int(self.raw_value)
        if isinstance(self.type, TypeFloat):
            return float(self.raw_value)
        if isinstance(self.type, TypeChar):
            return self.raw_value
        if isinstance(self.type, TypeBool):
            return self.raw_value == 'TRUE'
        raise TypeError(f'Unknown type: {self.type}')

    @property
    def type(self) -> TypeData:
        return self.children[1]

    def compile(self, context: CompilerContext) -> ScalarAddress:
        result_address = context.symbol_table.acquire_scalar()
        formatted_value = context.output.format_literal(self.value, self.type)
        context.output.copy(formatted_value, result_address)
        context.types[result_address] = self.type
        return result_address


class ExprArray(Expr[Tuple[List[Any], Optional[TypeData]]]):
    @property
    def members(self) -> List[Any]:
        return self.children[0]

    @property
    def member_type(self):
        return self.children[1] or TypeAny()

    @property
    def type_data(self):
        return TypeArray(self.member_type)

    def compile(self, context: CompilerContext) -> ScalarAddress:
        pass


# region Identifiers (type, declaration, assignment)


class IdentifierAccessFlags:
    NONE = 0
    DECLARATION = 1 << 0
    ASSIGNMENT = 1 << 1


class ExprIdentifierBase(Generic[TChildren], Expr[TChildren]):
    @property
    def name(self) -> str:
        return self.children[0]

    def assign(self, context: CompilerContext, identifier_address: ScalarAddress, value_address: ScalarAddress):
        context.output.format_scalar(identifier_address, context.types[identifier_address])
        context.output.copy(value_address, identifier_address)

    def compile(self, context: CompilerContext, access_flags: int = IdentifierAccessFlags.NONE) -> ScalarAddress:
        # we can only use cached symbol name when we're not making a declaration.
        # this way we don't accidentally return a cached symbol inside a lower scope instead of creating a new one
        if not (access_flags & IdentifierAccessFlags.DECLARATION) and context.symbol_table.does_symbol_exist(self.name):
            return context.symbol_table.retrieve_symbol_address(self.name)
        # type is currently unknown?
        return context.symbol_table.create_symbol(self.name, SymbolType.IDENTIFIER, TypeNull())


class ExprIdentifier(ExprIdentifierBase[Tuple[str]]):
    def assign(self, context: CompilerContext, identifier_address: ScalarAddress, value_address: ScalarAddress):
        assert_is_assignable(to_type=context.types[identifier_address],
                             from_type=context.types[value_address])
        super().assign(context, identifier_address, value_address)


class ExprArrayIndexIdentifier(ExprIdentifierBase[Tuple[str, Expr]]):
    @property
    def index_expr(self):
        return self.children[1]

    def assign(self, context: CompilerContext, identifier_address: ScalarAddress, value_address: ScalarAddress):
        member_type = context.types[identifier_address]
        context.assert_is_assignable(member_type, value_address)
        super().assign(context, identifier_address, value_address)

    def compile(self, context: CompilerContext,
                access_flags: int = IdentifierAccessFlags.NONE) -> ArrayIndexScalarAddress:
        identifier_address = super().compile(context, access_flags)
        context.assert_is_assignable(TypeArray(TypeAny()), identifier_address)
        index_address = self.index_expr.compile(context)
        context.assert_is_assignable(TypeInteger(), index_address)
        return identifier_address[index_address]


class ExprDeclarationBase(Expr[Tuple[ExprIdentifierBase, TypeData]], abc.ABC):
    @property
    def identifier(self) -> ExprIdentifierBase:
        return self.children[0]

    @property
    def type(self) -> TypeData:
        return self.children[1]

    @property
    def access_flags(self):
        flags = IdentifierAccessFlags.DECLARATION
        if self.is_assignment():
            flags |= IdentifierAccessFlags.ASSIGNMENT
        return flags

    @abc.abstractmethod
    def is_assignment(self) -> bool:
        return False

    def compile(self, context: CompilerContext) -> ScalarAddress:
        access_flags = self.access_flags
        identifier_address = self.identifier.compile(context, access_flags)
        context.types[identifier_address] = self.type
        return identifier_address


class ExprDeclaration(ExprDeclarationBase):
    @property
    def initial_value_expr(self) -> Optional[Expr]:
        return self.children[2]

    def is_assignment(self) -> bool:
        return self.initial_value_expr is not None

    def compile(self, context: CompilerContext) -> ScalarAddress:
        identifier_address = super().compile(context)
        if self.is_assignment():
            initial_value_address = self.initial_value_expr.compile(context)
            assert_is_assignable(self.type, context.types[initial_value_address], can_coerce=False)
            context.output.copy(initial_value_address, identifier_address)
        return identifier_address


class ExprArrayDeclaration(ExprDeclarationBase):
    @property
    def initial_value_expr_list(self) -> Optional[List[Expr]]:
        return self.children[2]

    @property
    def size_expr(self) -> Expr:
        return self.children[3]

    def is_assignment(self) -> bool:
        return self.initial_value_expr_list is not None

    def create_array(self, context: CompilerContext, size_address: ScalarAddress, array_address: ScalarAddress,
                     items: Optional[List[ScalarAddress]]):
        array_type = self.type
        if not isinstance(array_type, TypeArray):
            raise TypeError('Invalid state: self.type should have been instance of TypeArray already')

        context.output.create_array(size_address, array_address)

        if items is not None:
            for i, item in enumerate(items):
                context.assert_is_assignable(array_type.member_type, item)
                context.output.array_set_value_at_index(array_address, i, item)

    def compile(self, context: CompilerContext) -> ScalarAddress:
        context.assert_is_assignable(TypeArray(TypeAny()), self.type)
        result_address = super().compile(context)
        array_address = ScalarAddress(result_address.raw_address, ScalarType.ARRAY)

        size_address = self.size_expr.compile(context)

        if self.is_assignment():
            array_items = list(expr.compile(context) for expr in self.initial_value_expr_list)
            self.create_array(context, size_address, array_address, array_items)
        else:
            self.create_array(context, size_address, array_address, None)

        return array_address


class ExprAssignment(Expr[Tuple[ExprIdentifierBase, Expr]]):
    @property
    def identifier(self) -> ExprIdentifierBase:
        return self.children[0]

    @property
    def assign_value_expr(self) -> Expr:
        return self.children[1]

    def compile(self, context: CompilerContext) -> ScalarAddress:
        identifier_address = self.identifier.compile(context, IdentifierAccessFlags.ASSIGNMENT)
        value_address = self.assign_value_expr.compile(context)
        self.identifier.assign(context, identifier_address, value_address)
        return identifier_address


# endregion Identifiers (type, declaration, assignment)

# region Unary Expressions
class ExprUnary(Expr[Tuple[Operation, Expr]], abc.ABC):
    required_type: TypeData

    @property
    def operation(self) -> Operation:
        return self.children[0]

    @property
    def argument(self) -> Expr:
        return self.children[1]

    def compile(self, context: CompilerContext) -> ScalarAddress:
        argument_address = self.argument.compile(context)
        argument_type = context.types[argument_address]

        assert_is_assignable(self.required_type, argument_type, can_coerce=False)
        result_address = context.symbol_table.acquire_scalar()

        context.output.format_scalar(argument_address, argument_type)
        context.output.unary_operation(self.operation, argument_address, result_address)
        context.output.format_scalar(result_address, argument_type)

        context.types[result_address] = argument_type
        return result_address


class ExprMathUnary(ExprUnary):
    required_type = TypeNumeric()


class ExprLogicUnary(ExprUnary):
    required_type = TypeBool()


# endregion

# region Binary Expressions
class ExprBinary(Expr[Tuple[Expr, Operation, Expr]], abc.ABC):
    required_type: TypeData
    format_input_scalars: bool = True

    @property
    def left(self) -> Expr:
        return self.children[0]

    @property
    def right(self) -> Expr:
        return self.children[2]

    @property
    def operation(self) -> Operation:
        return self.children[1]

    @abc.abstractmethod
    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        pass

    def check_types(self, lhs_type: TypeData, rhs_type: TypeData):
        pass

    def compile(self, context: CompilerContext) -> ScalarAddress:
        lhs_address = self.left.compile(context)
        rhs_address = self.right.compile(context)

        lhs_type = context.types[lhs_address]
        rhs_type = context.types[rhs_address]

        assert_is_assignable(self.required_type, lhs_type, can_coerce=False)
        assert_is_assignable(self.required_type, rhs_type, can_coerce=False)
        self.check_types(lhs_type, rhs_type)

        result_type = self.result_type(lhs_type, rhs_type)
        result_address = context.symbol_table.acquire_scalar()

        if self.format_input_scalars:
            context.output.format_scalar(lhs_address, result_type)
            context.output.format_scalar(rhs_address, result_type)

        context.output.binary_operation(self.operation, lhs_address, rhs_address, result_address)
        context.types[result_address] = result_type
        context.output.format_scalar(result_address, result_type)

        return result_address


class ExprMathBinary(ExprBinary):
    required_type = TypeNumeric()

    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        if self.operation == Operation.IDIV:
            assert_is_assignable(TypeInteger(), lhs_type, can_coerce=False)
            assert_is_assignable(TypeInteger(), rhs_type, can_coerce=False)

        return self.required_type.promote_binary_result(lhs_type, rhs_type)


class ExprLogicBinary(ExprBinary):
    required_type = TypeBool()

    def result_type(self, *_) -> TypeData:
        return self.required_type


class ExprCompareBinary(ExprBinary):
    required_type = TypeAny()
    required_type_for_less_or_greater = TypeNumeric()
    format_input_scalars = False

    def check_types(self, lhs_type: TypeData, rhs_type: TypeData):
        if self.operation == Operation.EQUAL:
            if (lhs_type != rhs_type
                    and not (TypeNumeric().is_other_assignable_to_self(lhs_type, can_coerce=False)
                             and TypeNumeric().is_other_assignable_to_self(rhs_type, can_coerce=False))):
                raise TypeError('Equality comparison must be across two numbers, or two values of the same type')
        else:
            assert_is_assignable(self.required_type_for_less_or_greater, lhs_type, can_coerce=False)
            assert_is_assignable(self.required_type_for_less_or_greater, rhs_type, can_coerce=False)

    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        return TypeBool()


# endregion

# region Nary Expressions
class ExprNary(Expr[Tuple[Operation, List[Expr]]], abc.ABC):
    required_type = TypeNumeric()

    @property
    def operation(self) -> Operation:
        return self.children[0]

    @property
    def arguments(self) -> List[Expr]:
        return self.children[1]

    @abc.abstractmethod
    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        pass

    def compile(self, context: CompilerContext) -> ScalarAddress:
        result_address = context.symbol_table.acquire_scalar()

        first_argument_address = self.arguments[0].compile(context)

        current_result_type = context.types[first_argument_address]
        assert_is_assignable(self.required_type, current_result_type, can_coerce=False)

        # result = arguments[0]
        context.output.format_scalar(first_argument_address, current_result_type)
        context.output.copy(first_argument_address, result_address)

        for argument in self.arguments[1:]:
            argument_address = argument.compile(context)
            argument_type = context.types[argument_address]
            assert_is_assignable(self.required_type, argument_type, can_coerce=False)

            # result *= argument
            context.output.format_scalar(argument_address, current_result_type)
            context.output.binary_operation(self.operation, result_address, argument_address, result_address)

            # promote type if necessary
            current_result_type = self.result_type(current_result_type, argument_type)

            context.types[result_address] = current_result_type
            context.output.format_scalar(result_address, current_result_type)

        context.types[result_address] = current_result_type
        return result_address


class ExprMathNary(ExprNary):
    required_type = TypeNumeric()

    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        return self.required_type.promote_binary_result(lhs_type, rhs_type)


class ExprLogicNary(ExprNary):
    required_type = TypeBool()

    def result_type(self, lhs_type: TypeData, rhs_type: TypeData) -> TypeData:
        return self.required_type


# endregion


# region I/O

class ExprMystery(Expr[None]):
    def compile(self, context: CompilerContext) -> ScalarAddress:
        result_address = context.symbol_table.acquire_scalar()
        context.output.get_random(result_address)
        context.types[result_address] = TypeInteger()
        return result_address


class ExprReadInput(Expr[None]):
    result_type = TypeChar()

    def compile(self, context: CompilerContext) -> ScalarAddress:
        result_address = context.symbol_table.acquire_scalar()
        context.output.read_stdin(self.result_type, result_address)
        context.types[result_address] = self.result_type
        return result_address


class StatementPrint(Statement[Tuple[List[Expr]]]):
    @property
    def arguments(self) -> List[Expr]:
        return self.children[0]

    def compile(self, context: CompilerContext) -> None:
        for argument in self.arguments:
            argument_address = argument.compile(context)
            context.output.print_stdout(context.types[argument_address], argument_address)


class StatementPrintWithNewline(StatementPrint):
    def compile(self, context: CompilerContext) -> None:
        super().compile(context)
        context.output.print_stdout(TypeChar(), context.output.format_literal(r'%n', TypeChar()))


# endregion I/O

# region control flow
class ExprCondition(Expr[Tuple[Expr]]):
    @property
    def argument(self):
        return self.children[0]

    def compile(self, context: CompilerContext) -> ScalarAddress:
        result_address = self.argument.compile(context)
        assert_is_assignable(TypeBool(), context.types[result_address], can_coerce=False)
        return result_address


class StatementIfElse(Statement[Tuple[Expr, CommandList, Optional[CommandList]]]):
    @property
    def condition(self):
        return self.children[0]

    @property
    def if_body(self):
        return self.children[1]

    @property
    def has_else_body(self):
        return self.children[2] is not None

    @property
    def else_body(self):
        return self.children[2]

    def compile(self, context: CompilerContext) -> None:
        condition_address = self.condition.compile(context)
        context.output.if_statement_begin(condition_address, has_else=self.has_else_body)
        self.if_body.compile(context)
        if self.has_else_body:
            context.output.else_statement_begin()
            self.else_body.compile(context)
        context.output.if_else_statement_end()


class StatementWhile(Statement[Tuple[Expr, CommandList]]):
    @property
    def condition(self):
        return self.children[0]

    @property
    def body(self):
        return self.children[1]

    def compile(self, context: CompilerContext) -> None:
        context.output.while_loop_begin(lambda *_: self.condition.compile(context))
        self.body.compile(context)
        context.output.while_loop_end()


class StatementBreak(Statement):
    def compile(self, context: CompilerContext) -> None:
        context.output.while_loop_break()


class StatementForEach(Statement[Tuple[Expr, ExprIdentifier, CommandList]]):
    @property
    def iterable(self):
        return self.children[0]

    @property
    def identifier(self):
        return self.children[1]

    @property
    def body(self):
        return self.children[2]

    def compile(self, context: CompilerContext) -> None:
        iterable_address = self.iterable.compile(context)
        context.assert_is_assignable(TypeArray(TypeAny()), iterable_address)

        identifier_access_flags = IdentifierAccessFlags.DECLARATION | IdentifierAccessFlags.ASSIGNMENT
        identifier_address = self.identifier.compile(context, identifier_access_flags)

        def write_loop_body(_: ScalarAddress):
            self.body.compile(context)

        context.output.array_iterate(
            array_address=iterable_address,
            for_each_item=write_loop_body,
            current_item_address=identifier_address
        )


# endregion

class ExprArraySize(Expr[Tuple[Expr]]):
    @property
    def argument(self):
        return self.children[0]

    def compile(self, context: CompilerContext) -> ScalarAddress:
        argument_address = self.argument.compile(context)
        assert_is_assignable(TypeArray(TypeAny()), context.types[argument_address])
        result_address = context.symbol_table.acquire_scalar()
        context.output.array_get_size(argument_address, result_address)
        return result_address
