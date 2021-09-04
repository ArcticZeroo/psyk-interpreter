from typing import List, Tuple, Set

from rply.parser import LRParser
from rply.utils import IdentityDict, Counter


class Conflict:
    shift: Set[str]
    reduce: Set[str]

    def __init__(self):
        self.shift = set()
        self.reduce = set()


def get_lr0_items(rply_parser: LRParser):
    # copied from LRTable source (from_grammar)
    cidhash = IdentityDict()
    goto_cache = {}
    add_count = Counter()
    return rply_parser.lr_table.lr0_items(rply_parser.lr_table.grammar, add_count, cidhash, goto_cache)


def create_conflict_map(rply_parser: LRParser):
    conflict_list: List[Tuple[int, str, str]] = rply_parser.lr_table.sr_conflicts
    conflict_map = {}
    for conflict in conflict_list:
        (conflict_id, token_name, conflict_type) = conflict
        token_name = token_name.strip("'")
        if conflict_id not in conflict_map:
            conflict_map[conflict_id] = Conflict()
        conflict_data = conflict_map[conflict_id]
        if conflict_type == 'shift':
            conflict_data.shift.add(token_name)
        else:
            conflict_data.reduce.add(token_name)
    return conflict_map


def display_conflict_map(rply_parser: LRParser):
    conflict_map = create_conflict_map(rply_parser)
    whatever_C_means = get_lr0_items(rply_parser)

    if len(conflict_map) == 0:
        return

    print(f'Shift/reduce errors exist:')
    for conflict_id, conflict_data in conflict_map.items():
        print(f'{whatever_C_means[conflict_id]}')
        if len(conflict_data.shift) > 0:
            print(f'shift: {conflict_data.shift}')
        if len(conflict_data.reduce) > 0:
            print(f'reduce: {conflict_data.reduce}')
