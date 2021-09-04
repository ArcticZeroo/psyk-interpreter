from dataclasses import dataclass
from typing import List, TypeVar, Union, Any

from psyk.type_system import TypeData, TypeNull
from psyk.scalar import ScalarAddress, ScalarType

META_ADDRESS = 0
T = TypeVar('T')


@dataclass
class MemoryValue:
    value: Any
    value_type: TypeData

    @staticmethod
    def null():
        return MemoryValue(None, TypeNull())


class Memory:
    _default_address_prefix: str
    _raw_memory: List[MemoryValue]

    def __init__(self, default_address_prefix: str = 's'):
        self._default_address_prefix = default_address_prefix
        self._raw_memory = [
            # TODO replace with meta
            MemoryValue.null()
        ]

    @property
    def _next_address(self):
        return len(self._raw_memory)

    @property
    def address_prefix(self):
        return self._default_address_prefix

    def get_next_address(self, scalar_type: ScalarType = ScalarType.REGULAR):
        address = self._next_address
        self._raw_memory.append(MemoryValue.null())
        return ScalarAddress(address, scalar_type)

    def is_allocated(self, scalar: ScalarAddress):
        return scalar.raw_address < len(self._raw_memory)

    def is_non_null(self, scalar: ScalarAddress):
        return self.is_allocated(scalar) and (
            not TypeNull().is_other_assignable_to_self(self._raw_memory[scalar.raw_address].value_type)
        )

    def get(self, scalar: ScalarAddress) -> MemoryValue:
        return self._raw_memory[scalar.raw_address]

    def set(self, scalar: ScalarAddress, value: MemoryValue):
        self._raw_memory[scalar.raw_address] = value
