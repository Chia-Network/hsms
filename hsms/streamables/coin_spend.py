from clvm_rs import Program

from .coin import Coin

from hsms.meta import streamable
from hsms.util.clvm_serialization import transform_as_struct


@streamable
class CoinSpend:
    """
    This is a rather disparate data structure that validates coin transfers. It's
    generally populated with data from different sources, since burned coins are
    identified by name, so it is built up more often that it is streamed.
    """

    coin: Coin
    puzzle_reveal: Program
    solution: Program

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
