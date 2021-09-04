from typing import Optional, Dict


class UniqueSymbol:
    _registry: Dict[str, 'UniqueSymbol'] = dict()

    _obj: object
    _name: Optional[str]

    def __init__(self, name: Optional[str] = ''):
        self._obj = object()
        self._name = name

    def __eq__(self, other):
        return isinstance(other, UniqueSymbol) and other._obj is self._obj

    def __hash__(self):
        return hash(self._obj)

    def __str__(self):
        return f'Symbol({self._name})'

    @staticmethod
    def for_key(key: str) -> 'UniqueSymbol':
        if key not in UniqueSymbol._registry:
            UniqueSymbol._registry[key] = UniqueSymbol(key)
        return UniqueSymbol._registry[key]

    @staticmethod
    def key_for(symbol: 'UniqueSymbol') -> Optional[str]:
        for key, registered_symbol in UniqueSymbol._registry.items():
            if registered_symbol == symbol:
                return key
        return None
