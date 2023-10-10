from dataclasses import dataclass, field

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent
from chia_base.core import Coin, CoinSpend

from clvm_rs import Program

from hsms.util.clvm_serde import PairTuple


SumHint = PairTuple[list[BLSPublicKey], BLSSecretExponent]

CoinSpendTuple = tuple[bytes, Program, int, Program]

PathHint = PairTuple[BLSPublicKey, list[int]]


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


def sum_hint_as_tuple(sum_hint: SumHint) -> tuple:
    keys = "public_keys synthetic_offset".split()
    return tuple(getattr(sum_hint, _) for _ in keys)


def path_hint_as_tuple(path_hint: PathHint) -> tuple:
    return tuple(getattr(path_hint, _) for _ in "root_public_key path".split())
