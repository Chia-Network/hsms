from dataclasses import dataclass, field

from chia_base.core import Coin, CoinSpend

from clvm_rs import Program

from .signing_hints import PathHint, SumHint


CoinSpendTuple = tuple[bytes, Program, int, Program]


@dataclass
class UnsignedSpend:
    coin_spend_tuples: list[CoinSpendTuple] = field(
        default_factory=list, metadata=dict(key="c")
    )
    sum_hints: list[SumHint] = field(
        default_factory=list,
        metadata=dict(key="s"),
    )
    path_hints: list[PathHint] = field(
        default_factory=list,
        metadata=dict(key="p"),
    )
    agg_sig_me_network_suffix: bytes = field(
        default=b"",
        metadata=dict(key="a"),
    )

    def coin_spends(self):
        return [coin_spend_from_tuple(_) for _ in self.coin_spend_tuples]


def coin_spend_from_tuple(cst: CoinSpendTuple) -> CoinSpend:
    coin = Coin(cst[0], cst[1].tree_hash(), cst[2])
    return CoinSpend(coin, cst[1], cst[3])


def coin_spend_to_tuple(coin_spend: CoinSpend) -> CoinSpendTuple:
    coin = coin_spend.coin
    return (
        coin.parent_coin_info,
        coin_spend.puzzle_reveal,
        coin.amount,
        coin_spend.solution,
    )
