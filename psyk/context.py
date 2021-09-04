from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Union

from psyk.intermediate_output import IntermediateOutput
from psyk.memory import ScalarAddress
from psyk.symbol_table import CompilerSymbolTable
from psyk.type_system import TypeData, assert_is_assignable

TSymbolTable = TypeVar('TSymbolTable')
TOutput = TypeVar('TOutput')


class TypeProxy:
    _symbol_table: CompilerSymbolTable

    def __init__(self, symbol_table: CompilerSymbolTable):
        self._symbol_table = symbol_table

    def __getitem__(self, item: ScalarAddress):
        if not isinstance(item, ScalarAddress):
            raise TypeError('item must be a ScalarAddress')
        return self._symbol_table.get_type_of(item)

    def __setitem__(self, key: ScalarAddress, value: TypeData):
        if not isinstance(key, ScalarAddress):
            raise TypeError('key must be a ScalarAddress')
        if not isinstance(value, TypeData):
            raise TypeError('value must be a TypeData')
        self._symbol_table.set_type_of(address=key, type_data=value)


@dataclass
class Context(Generic[TSymbolTable, TOutput]):
    symbol_table: TSymbolTable
    output: TOutput


class CompilerContext(Context[CompilerSymbolTable, IntermediateOutput]):
    types: TypeProxy

    def __init__(self, symbol_table: CompilerSymbolTable, output: IntermediateOutput):
        super().__init__(symbol_table, output)
        self.types = TypeProxy(symbol_table)

    def _type_from_address_or_type(self, from_type: Union[ScalarAddress, TypeData]):
        if isinstance(from_type, ScalarAddress):
            return self.types[from_type]
        return from_type

    def assert_is_assignable(self, to_type: Union[ScalarAddress, TypeData], from_type: Union[ScalarAddress, TypeData]):
        assert_is_assignable(self._type_from_address_or_type(to_type), self._type_from_address_or_type(from_type))
