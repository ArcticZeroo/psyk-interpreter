from enum import Enum
from typing import Union


class ScalarType(Enum):
    NULL = 'NULL'
    REGULAR = 's'
    ARRAY = 'a'


class ScalarAddress:
    _raw_address: int
    _scalar_type: ScalarType

    def __init__(self, raw_address: int, scalar_type: ScalarType = ScalarType.REGULAR):
        self._raw_address = raw_address
        self._scalar_type = scalar_type

    def __str__(self):
        return f'{self._scalar_type.value}{self._raw_address}'

    def __getitem__(self, item):
        assert_scalar_type(self, ScalarType.ARRAY)

        if not isinstance(item, int) and not isinstance(item, ScalarAddress):
            raise TypeError('Item must be an integer or scalar address')

        return ArrayIndexScalarAddress(self, item)

    @property
    def address(self):
        return str(self)

    @property
    def raw_address(self):
        return self._raw_address

    @property
    def type(self):
        return self._scalar_type

    @staticmethod
    def null():
        return ScalarAddress(raw_address=-1, scalar_type=ScalarType.NULL)


LiteralValue = Union[int, str]
LiteralOrScalar = Union[ScalarAddress, LiteralValue]


class ArrayIndexScalarAddress(ScalarAddress):
    _index: LiteralOrScalar

    def __init__(self, array_address: ScalarAddress, index: LiteralOrScalar = 0):
        assert_scalar_type(array_address, ScalarType.ARRAY)
        super().__init__(array_address.raw_address, ScalarType.ARRAY)
        self._index = index

    @property
    def index(self):
        return self._index

    @property
    def array(self):
        return ScalarAddress(self.raw_address, ScalarType.ARRAY)


def assert_scalar_type(scalar: ScalarAddress, expected_type: ScalarType):
    if scalar.type != expected_type:
        raise TypeError(f'Scalar type {scalar.type} does not match expected type {expected_type}')
