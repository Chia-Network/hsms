from dataclasses import dataclass, field
from typing import List, Tuple

from chia_base.bls12_381 import BLSPublicKey, BLSSignature
from chia_base.core import Coin, CoinSpend

from clvm_rs import Program  # type: ignore

from hsms.clvm_serde import (
    to_program_for_type,
    from_program_for_type,
)
from .signing_hints import PathHint, SumHint


CSTuple = Tuple[bytes, Program, int, Program]
SerdeCoinSpends = List[CSTuple]


def to_storage(
    coin_spend_tuples: SerdeCoinSpends,
) -> List[CoinSpend]:
    return [
        CoinSpend(Coin(_[0], _[1].tree_hash(), _[2]), _[1], _[3])
        for _ in coin_spend_tuples
    ]


def from_storage(
    coin_spends: List[CoinSpend],
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
class SignatureInfo:
    signature: BLSSignature
    partial_public_key: BLSPublicKey
    final_public_key: BLSPublicKey
    message: bytes


@dataclass
class UnsignedSpend:
    coin_spends: List[CoinSpend] = field(
        metadata=dict(
            key="c",
            alt_serde_type=(
                SerdeCoinSpends,
                from_storage,
                to_storage,
            ),
        ),
    )
    sum_hints: List[SumHint] = field(
        default_factory=list,
        metadata=dict(key="s"),
    )
    path_hints: List[PathHint] = field(
        default_factory=list,
        metadata=dict(key="p"),
    )
    agg_sig_me_network_suffix: bytes = field(
        default=b"",
        metadata=dict(key="a"),
    )

    def __bytes__(self):
        return bytes(TO_PROGRAM(self))

    @classmethod
    def from_bytes(cls, blob: bytes):
        return FROM_PROGRAM(Program.from_bytes(blob))


TO_PROGRAM = to_program_for_type(UnsignedSpend)
FROM_PROGRAM = from_program_for_type(UnsignedSpend)
