from dataclasses import dataclass
from typing import List

from chia_base.atoms import bytes32
from chia_base.bls12_381 import BLSPublicKey, BLSSignature
from chia_base.core import Coin, CoinSpend

from clvm_rs import Program

from hsms.process.signing_hints import SumHint, PathHint
from hsms.util.clvm_serialization import (
    as_atom,
    as_int,
    clvm_to_list,
    no_op,
    transform_dict,
    transform_dict_by_key,
    transform_as_struct,
)


@dataclass
class SignatureInfo:
    signature: BLSSignature
    partial_public_key: BLSPublicKey
    final_public_key: BLSPublicKey
    message: bytes


@dataclass
class UnsignedSpend:
    coin_spends: List[CoinSpend]
    sum_hints: List[SumHint]
    path_hints: List[PathHint]
    agg_sig_me_network_suffix: bytes32

    def as_program(self):
        as_clvm = [("a", self.agg_sig_me_network_suffix)]
        cs_as_clvm = [
            [_.coin.parent_coin_info, _.puzzle_reveal, _.coin.amount, _.solution]
            for _ in self.coin_spends
        ]
        as_clvm.append(("c", cs_as_clvm))
        sh_as_clvm = [_.as_program() for _ in self.sum_hints]
        as_clvm.append(("s", sh_as_clvm))
        ph_as_clvm = [_.as_program() for _ in self.path_hints]
        as_clvm.append(("p", ph_as_clvm))
        self_as_program = Program.to(as_clvm)
        return self_as_program

    @classmethod
    def from_program(cls, program) -> "UnsignedSpend":
        d = transform_dict(program, transform_dict_by_key(UNSIGNED_SPEND_TRANSFORMER))
        return cls(d["c"], d.get("s", []), d.get("p", []), d["a"])

    def __bytes__(self):
        return bytes(self.as_program())

    @classmethod
    def from_bytes(cls, blob) -> "UnsignedSpend":
        return cls.from_program(Program.from_bytes(blob))


def coin_spend_from_program(program: Program) -> CoinSpend:
    struct = transform_as_struct(program, as_atom, no_op, as_int, no_op)
    parent_coin_info, puzzle_reveal, amount, solution = struct
    return CoinSpend(
        Coin(
            parent_coin_info,
            puzzle_reveal.tree_hash(),
            amount,
        ),
        puzzle_reveal,
        solution,
    )


UNSIGNED_SPEND_TRANSFORMER = {
    "c": lambda x: clvm_to_list(x, coin_spend_from_program),
    "s": lambda x: clvm_to_list(x, SumHint.from_program),
    "p": lambda x: clvm_to_list(x, PathHint.from_program),
    "a": lambda x: x.atom,
}
