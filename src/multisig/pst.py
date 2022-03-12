from clvm.casts import int_from_bytes

from bls12_381 import BLSSignature
from streamables import CoinSpend, Program


from util.clvm_serialization import (
    xform_clvm_list,
    transform_dict,
    cbor_struct_to_bytes,
    transform_dict_by_key,
)


class PartiallySignedTransaction(dict):
    @classmethod
    def from_bytes(cls, blob):
        pst = Program.from_bytes(blob)
        return cls(transform_pst(pst))

    def __bytes__(self):
        cbor_obj = cbor_struct_to_bytes(self)
        return bytes(Program.to(cbor_obj))


def xform_aggsig_sig_pair(pair):
    """
    Transform a pair (aggsig_pair_bytes, sig_bytes)
    to (aggsig_pair, BLSSignature).
    """
    aggsig = BLSSignature.aggsig_pair.from_bytes(pair[0])
    sig = BLSSignature.from_bytes(pair[1])
    return (aggsig, sig)


def to_str(b: bytes) -> str:
    return b.decode()


HINT_TRANSFORMS = dict(
    hd_fingerprint=lambda x: int_from_bytes(x.atom),
    index=xform_clvm_list(lambda x: int_from_bytes(x.atom)),
)


def clvm_to_coin_spend(program):
    return CoinSpend.from_bytes(program.atom)


def deserialize_hints(program):
    print(program)
    breakpoint()
    table = transform_dict(program, transform_dict_by_key(HINT_TRANSFORMS))
    return table


PST_TRANSFORMS = dict(
    coin_spends=xform_clvm_list(lambda x: CoinSpend.from_bytes(x.atom)),
    sigs=xform_clvm_list(xform_aggsig_sig_pair),
    delegated_solution=lambda x: Program.from_bytes(x.atom),
    hd_hints=lambda x: transform_dict(
        x, lambda k, v: (int_from_bytes(k.atom), deserialize_hints(v))
    ),
)


def transform_pst(pst):
    """
    Turn a pst `Program` into its corresponding constituent parts.
    """
    return transform_dict(pst, transform_dict_by_key(PST_TRANSFORMS))
