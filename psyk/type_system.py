import abc
import math
import typing

from psyk.tokens import Tokens


class TypeData(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self):
        pass

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        """
        Returns whether the OTHER is assignable to the current type.
        By default, this checks that other is an instance of the same type as self, i.e. they are the same type
        :param other: The other type we wish to assign to this type
        :param can_coerce: Whether other can be coerced to self to become assignable
        :return: Whether the other type is compatible with this type
        """
        return isinstance(other, type(self))

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other: typing.Any):
        return isinstance(other, TypeData) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def assert_is_assignable(to_type: TypeData, from_type: TypeData, can_coerce: bool = False):
    if not to_type.is_other_assignable_to_self(from_type, can_coerce):
        raise TypeError(f'{from_type} is not assignable to {to_type}')


def assert_either_is_assignable(a: TypeData, b: TypeData, can_coerce: bool = False):
    if not a.is_other_assignable_to_self(b, can_coerce) and not b.is_other_assignable_to_self(a, can_coerce):
        raise TypeError(f'Neither {a} nor {b} are assignable to each other')


class TypeAny(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Any'

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        return True


class TypeInteger(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Int'

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        return isinstance(other, TypeInteger) or (can_coerce and isinstance(other, TypeBool))


class TypeFloat(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Float'

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        # previously this was allowing ints to promote without coercion, that is no longer allowed
        return isinstance(other, TypeFloat) or (can_coerce and isinstance(other, TypeInteger))


class TypeBool(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Bool'

    # def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
    #     return super().is_other_assignable_to_self(other) or (can_coerce and isinstance(other, TypeInteger))


class TypeChar(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Char'


class TypeArray(TypeData):
    _member_type: TypeData

    def __init__(self, member_type: TypeData):
        self._member_type = member_type

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        return isinstance(other, TypeArray) and self.member_type.is_other_assignable_to_self(other.member_type,
                                                                                             can_coerce)

    @TypeData.name.getter
    def name(self):
        return f'Array[{str(self._member_type)}]'

    @property
    def member_type(self) -> TypeData:
        return self._member_type


class TypeUnion(TypeData):
    _types: typing.Set[TypeData]

    def __init__(self, types: typing.Set[TypeData]):
        self._types = types

    def __eq__(self, other):
        return isinstance(other, TypeUnion) and other._types == self._types

    def __hash__(self):
        return hash(type_data for type_data in self._types)

    @TypeData.name.getter
    def name(self):
        return f'Union[{",".join(str(type_data) for type_data in self._types)}]'

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        return any(type_data.is_other_assignable_to_self(other, can_coerce)
                   for type_data in self._types)


class TypeNumeric(TypeUnion):
    def __init__(self):
        super().__init__({TypeInteger(), TypeFloat()})

    def is_other_assignable_to_self(self, other: 'TypeData', can_coerce: bool = True) -> bool:
        return super().is_other_assignable_to_self(other, can_coerce) or (can_coerce and isinstance(other, TypeBool))

    def promote_binary_result(self, a: TypeData, b: TypeData):
        assert_is_assignable(self, a)
        assert_is_assignable(self, b)

        # if both are the same, no promotion is necessary -- return the same type since that is the result type
        if a == b:
            return a

        # TODO remove maybe once coercion not needed
        # if either is a bool but the other is not, the result is the other since bool will coerce to numeric
        if isinstance(a, TypeBool):
            return b
        if isinstance(b, TypeBool):
            return a

        # if we have 1 float and 1 int, the result is always a float.
        return TypeFloat()


class TypeNull(TypeData):
    @TypeData.name.getter
    def name(self):
        return 'Null'


_TYPE_PSYK_NAME_TO_TYPE_CLASS = {
    'NUMBER':             TypeInteger,
    'REAL':               TypeFloat,
    'GLYPH':              TypeChar,
    'TRUTH':              TypeBool,
    Tokens.INT_LITERAL:   TypeInteger,
    Tokens.FLOAT_LITERAL: TypeFloat,
    Tokens.BOOL_LITERAL:  TypeBool,
    Tokens.CHAR_LITERAL:  TypeChar
}


def from_scalar_type_name(name: str) -> TypeData:
    if name not in _TYPE_PSYK_NAME_TO_TYPE_CLASS:
        # assume it is an array
        if name.endswith(Tokens.PLURAL):
            stripped_name = name[:len(name) - 1]
            member_type = from_scalar_type_name(stripped_name)
            return TypeArray(member_type)

        raise ValueError(f'{name} is not a recognized psyk scalar type')
    type_data_class = _TYPE_PSYK_NAME_TO_TYPE_CLASS[name]
    return type_data_class()


def is_truthy(value: typing.Any):
    if isinstance(value, bool):
        return value
    if isinstance(value, int) or isinstance(value, float):
        return value != 0
    if isinstance(value, str) or isinstance(value, list):
        return len(value) > 0
    raise TypeError(f'Unsupported type {type(value).__name__}')


def coerce(value: typing.Any, result_type: TypeData):
    if isinstance(result_type, TypeInteger):
        try:
            return int(value)
        except ValueError:
            return math.nan
    if isinstance(result_type, TypeFloat):
        try:
            return float(value)
        except ValueError:
            return math.nan
    if isinstance(result_type, TypeBool):
        return is_truthy(result_type)
    if isinstance(result_type, TypeChar):
        return (str(result_type) or '\0')[0]
    raise TypeError(f'Unsupported type {type(value).__name__}')
