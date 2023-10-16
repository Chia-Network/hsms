from dataclasses import dataclass, field

from chia_base.core import Coin, CoinSpend

from clvm_rs import Program

from .signing_hints import PathHint, SumHint


CSTuple = tuple[bytes, Program, int, Program]
SerdeCoinSpends = list[CSTuple]


def to_storage(
    coin_spend_tuples: SerdeCoinSpends,
) -> list[CoinSpend]:
    return [
        CoinSpend(Coin(_[0], _[1].tree_hash(), _[2]), _[1], _[3])
        for _ in coin_spend_tuples
    ]


def from_storage(
    coin_spends: list[CoinSpend],
) -> SerdeCoinSpends:
    return [
        (
            _.coin.parent_coin_info,
            _.puzzle_reveal,
            _.coin.amount,
            _.solution,
        )
        for _ in coin_spends
    ]


@dataclass
class UnsignedSpend:
    coin_spends: list[CoinSpend] = field(
        default_factory=list,
        metadata=dict(
            key="c",
            alt_serde_type=(
                SerdeCoinSpends,
                from_storage,
                to_storage,
            ),
        ),
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
