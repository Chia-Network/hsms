from clvm_rs import Program

from chia_base.core import Coin, CoinSpend

from hsms.util.clvm_serialization import transform_as_struct


def as_program(self):
    return [
        [_.coin.parent_coin_info, _.puzzle_reveal, _.coin.amount, _.solution]
        for _ in self.coin_spends
    ]

@classmethod
def from_program(cls, program) -> "CoinSpend":
    parent_coin_info, puzzle_reveal, amount, solution = transform_as_struct(
        program,
        lambda x: x.atom,
        lambda x: x,
        lambda x: Program.to(x).as_int(),
        lambda x: x,
    )
    puzzle_reveal = Program.to(puzzle_reveal)
    solution = Program.to(solution)
    return cls(
        Coin(
            parent_coin_info,
            puzzle_reveal.tree_hash(),
            amount,
        ),
        puzzle_reveal,
        solution,
    )

CoinSpend.as_program = as_program
CoinSpend.from_program = from_program