"""
Pay to conditions

In this puzzle program, the solution is ignored. The reveal of the puzzle
returns a fixed list of conditions. This roughly corresponds to OP_SECURETHEBAG
in bitcoin.

This is a pretty useless most of the time. But some (most?) solutions
require a delegated puzzle program, so in those cases, this is just what
the doctor ordered.
"""

from clvm_rs import Program  # type: ignore

from chialisp_puzzles import load_puzzle  # type: ignore

MOD = load_puzzle("p2_conditions")


def puzzle_for_conditions(conditions) -> Program:
    return MOD.run_with_cost([conditions], max_cost=1<<32)[1]


def solution_for_conditions(conditions) -> Program:
    return Program.to([puzzle_for_conditions(conditions), 0])
