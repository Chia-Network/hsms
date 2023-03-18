from typing import Dict, List

from clvm_rs.program import Program


def conditions_by_opcode(conditions: Program) -> Dict[int, List[Program]]:
    d: Dict[int, List[Program]] = {}
    for _ in conditions.as_iter():
        if _.pair:
            d.setdefault(Program.to(_.pair[0]).as_int(), []).append(_)
    return d
