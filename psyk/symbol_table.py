import abc
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Iterator, Set, Union

from psyk.exception import VariableNotDefinedException
from psyk.memory import Memory, ScalarAddress
from psyk.type_system import TypeData, TypeNull, TypeArray, TypeAny
from psyk.scalar import LiteralOrScalar, ScalarType, ArrayIndexScalarAddress


# region Scalar Pools
class ScalarPool:
    _symbol_table: 'CompilerSymbolTable'
    _all_scalars: Set[ScalarAddress]
    _free_scalars: Set[ScalarAddress]

    def __init__(self, symbol_table: 'CompilerSymbolTable'):
        self._symbol_table = symbol_table
        self._all_scalars = set()
        self._free_scalars = set()

    def acquire(self):
        scalar = None
        if len(self._free_scalars) == 0:
            scalar = self._symbol_table.register_new_scalar()
            self._all_scalars.add(scalar)
        else:
            scalar = next(iter(self._free_scalars))
            self._free_scalars.remove(scalar)
        self._symbol_table.current_scope.hold_scalar(scalar)
        return scalar

    def dispose(self, address: ScalarAddress):
        self._symbol_table.set_type_of(address, TypeNull())
        self._free_scalars.add(address)


class TemporaryScalarAddressResource:
    _scalar_pool: ScalarPool
    _address: Optional[ScalarAddress]

    def __init__(self, scalar_pool: ScalarPool, address: Optional[ScalarAddress] = None):
        self._scalar_pool = scalar_pool
        self._address = address

    def __enter__(self) -> ScalarAddress:
        self._address = self._scalar_pool.acquire()
        return self._address

    def __exit__(self, *_):
        self._scalar_pool.dispose(self._address)

    @property
    def address(self):
        return self._address


@dataclass(frozen=True)
class FixedScalarAddressResource:
    address: ScalarAddress

    def __enter__(self) -> ScalarAddress:
        return self.address

    def __exit__(self, *_):
        pass


class TemporaryScalarManager:
    _scalar_pool: ScalarPool

    def __init__(self, scalar_pool: ScalarPool):
        self._scalar_pool = scalar_pool

    def acquire(self):
        return TemporaryScalarAddressResource(self._scalar_pool)

    def acquire_or_use_existing(self, existing: Optional[ScalarAddress]):
        """
        If [existing] is not None, format it so that it can be used as in a with-resources statement
        If it is None, acquire a new temporary address instead.
        :param existing: An optionally existing scalar address
        :return: A resource containing a temporary or fixed scalar address
        """
        if existing is not None:
            return FixedScalarAddressResource(address=existing)
        return self.acquire()


# endregion


class SymbolType(Enum):
    ADDRESS = 'address'
    IDENTIFIER = 'identifier'
    FUNCTION = 'function'


class ScopeType(Enum):
    ROOT = 'root'
    IF_ELSE_STATEMENT = 'if_else'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'


class SymbolTable(abc.ABC):
    @abc.abstractmethod
    def does_symbol_exist(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def retrieve_symbol_address(self, name: str) -> Optional[ScalarAddress]:
        pass

    @abc.abstractmethod
    def store_symbol(self, name: str, data: ScalarAddress):
        pass


# possibly redundant?
class ScopeData(SymbolTable):
    _held_scalars: Set[ScalarAddress]
    _symbols: Dict[str, ScalarAddress]
    _scalar_to_symbol_name: Dict[ScalarAddress, str]
    _current_label_id: int
    _scope_type: ScopeType

    def __init__(self, scope_type: ScopeType, next_label_id: int = -1):
        self._held_scalars = set()
        self._symbols = dict()
        self._scalar_to_symbol_name = dict()
        self._current_label_id = next_label_id
        self._scope_type = scope_type

    @property
    def current_label_id(self):
        return self._current_label_id

    @property
    def scope_type(self):
        return self._scope_type

    @property
    def symbols(self):
        return self._symbols.keys()

    @property
    def scalars(self):
        return self._held_scalars

    def get_symbol_name(self, address: ScalarAddress):
        return self._scalar_to_symbol_name.get(address)

    def does_symbol_exist(self, name: str) -> bool:
        return name in self._symbols

    def retrieve_symbol_address(self, name: str) -> Optional[ScalarAddress]:
        return self._symbols.get(name)

    def store_symbol(self, name: str, data: ScalarAddress):
        self._symbols[name] = data
        self._scalar_to_symbol_name[data] = name

    def hold_scalar(self, address: ScalarAddress):
        self._held_scalars.add(address)


class ScopeManager(SymbolTable):
    _scopes: List[ScopeData]

    def __init__(self):
        self._scopes = []

    def push_scope(self, data: ScopeData):
        self._scopes.append(data)

    def pop_scope(self) -> ScopeData:
        return self._scopes.pop()

    @property
    def current_scope(self) -> ScopeData:
        return self._scopes[-1]

    @property
    def scopes(self) -> Iterator[ScopeData]:
        return reversed(self._scopes)

    def does_symbol_exist(self, name: str) -> bool:
        for scope in self.scopes:
            if scope.does_symbol_exist(name):
                return True
        return False

    def retrieve_symbol_address(self, name: str) -> Optional[ScalarAddress]:
        for scope in self.scopes:
            if scope.does_symbol_exist(name):
                return scope.retrieve_symbol_address(name)
        return None

    def retrieve_symbol_name(self, address: ScalarAddress):
        for scope in self.scopes:
            symbol_name = scope.get_symbol_name(address)
            if symbol_name:
                return symbol_name
        return None

    def store_symbol(self, name: str, data: ScalarAddress):
        self.current_scope.store_symbol(name, data)


class InterpreterSymbolTable:
    """
    A symbol table for the interpretation step.
    When undefined variables are accessed,
    an exception is raised.
    """

    # TODO when I implement interpreter... this may need to be replaced
    _scope_manager: ScopeManager

    def __init__(self):
        self._scope_manager = ScopeManager()

    def does_symbol_exist(self, name: str) -> bool:
        return self._scope_manager.does_symbol_exist(name)

    def retrieve_symbol_value(self, name: str) -> ScalarAddress:
        if not self._scope_manager.does_symbol_exist(name):
            # TODO
            raise ValueError('Variable not defined')
        return self._scope_manager.retrieve_symbol_address(name)

    def store_symbol_value(self, name: str, data: ScalarAddress) -> None:
        self._scope_manager.store_symbol(name, data)


class CompilerSymbolTable:
    """
    A symbol table for the compilation step.
    When undefined variables are accessed,
    they are created and no errors are raised.
    """
    _scope_manager: ScopeManager
    _memory: Memory
    _scalar_pool: ScalarPool
    _temp_scalars: TemporaryScalarManager

    def __init__(self):
        self._scope_manager = ScopeManager()
        self._memory = Memory()
        self._scalar_pool = ScalarPool(self)
        self._temp_scalars = TemporaryScalarManager(self._scalar_pool)

    @property
    def current_scope(self) -> ScopeData:
        return self._scope_manager.current_scope

    def does_symbol_exist(self, name: str) -> bool:
        return self._scope_manager.does_symbol_exist(name)

    def register_new_scalar(self):
        """
        Register a scalar value and return its memory location
        :return: The new memory location of this scalar
        """
        return self._memory.get_next_address()

    def acquire_scalar(self):
        return self._scalar_pool.acquire()

    def acquire_or_use_existing_scalar(self, scalar: Optional[ScalarAddress]):
        return scalar or self.acquire_scalar()

    def acquire_temporary_scalar(self):
        return self._temp_scalars.acquire()

    def acquire_or_use_existing_temporary_scalar(self, address: Optional[ScalarAddress]):
        return self._temp_scalars.acquire_or_use_existing(address)

    def dispose_scalar(self, address: ScalarAddress):
        return self._scalar_pool.dispose(address)

    def create_symbol(self, name: str, symbol_type: SymbolType, value_type: TypeData) -> ScalarAddress:
        address = self.register_new_scalar()

        symbol_data = self._memory.get(address)
        symbol_data.value = symbol_type
        symbol_data.value_type = value_type

        self._scope_manager.store_symbol(name, address)

        if TypeArray(TypeAny()).is_other_assignable_to_self(value_type):
            return ScalarAddress(address.raw_address, ScalarType.ARRAY)

        return address

    def retrieve_symbol_address(self, name: str) -> ScalarAddress:
        """
        Finds a given symbol value if it exists, or raise an exception if the symbol does not exist.
        Only use this when you know what you're doing! (i.e. you've just compiled an expression that must
        have an associated symbol with it).
        :param name: The name of the symbol
        :return: The symbol
        """
        address = self._scope_manager.retrieve_symbol_address(name)
        if address is None:
            raise VariableNotDefinedException(f'Variable {name} not defined')
        if self.has_type(address) and TypeArray(TypeAny()).is_other_assignable_to_self(self.get_type_of(address)):
            return ScalarAddress(address.raw_address, ScalarType.ARRAY)
        return address

    def get_or_create_symbol_value(self, name: str, symbol_type: SymbolType,
                                   value_type: TypeData) -> ScalarAddress:
        """
        Get symbol data for a given value, creating it if it doesn't already exist.
        :param name: The name of the symbol
        :param symbol_type: The type of the symbol to create if it doesn't already exist
        :param value_type: The value of the symbol to create if it doesn't already exist
        :return:
        """
        if not self.does_symbol_exist(name):
            return self.create_symbol(name, symbol_type, value_type)
        return self._scope_manager.retrieve_symbol_address(name)

    def push_scope(self, data: ScopeData):
        self._scope_manager.push_scope(data)

    def pop_scope(self) -> ScopeData:
        popped_scope = self._scope_manager.pop_scope()
        for popped_scalar in popped_scope.scalars:
            self._scalar_pool.dispose(popped_scalar)
        return popped_scope

    def _address_display(self, address: ScalarAddress):
        raw_address_display = f'*{address}'
        symbol_name = self._scope_manager.retrieve_symbol_name(address)
        if symbol_name:
            raw_address_display += f' (THE {symbol_name})'
        return raw_address_display

    def assert_access(self, value: LiteralOrScalar):
        if not isinstance(value, ScalarAddress):
            return
        if not self.has_type(value):
            raise VariableNotDefinedException(f'{self._address_display(value)} has no value')

    def has_type(self, address: ScalarAddress) -> bool:
        return self._memory.is_non_null(address)

    def get_type_of(self, address: ScalarAddress) -> TypeData:
        self.assert_access(address)
        type_data = self._memory.get(address).value_type
        if isinstance(address, ArrayIndexScalarAddress):
            if not isinstance(type_data, TypeArray):
                raise TypeError('Address referred to by an array index is not of type array')
            return type_data.member_type
        return type_data

    def set_type_of(self, address: ScalarAddress, type_data: TypeData):
        memory_value = self._memory.get(address)
        memory_value.value_type = type_data

    def set_type_if_none(self, address: LiteralOrScalar, type_data: TypeData):
        if isinstance(address, ScalarAddress) and not self.has_type(address):
            self.set_type_of(address, type_data)

    def find_scope_of_type(self, scope_type: ScopeType):
        for scope in self._scope_manager.scopes:
            if scope.scope_type == scope_type:
                return scope
        return None
