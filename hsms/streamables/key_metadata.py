# def create_request(coin_spend_list: CoinSpend) -> bytes:
# public key breakdown hints
# public_keys : [pubkey1, pubkey2, ...]
# secret_keys: [se1, se2, ...]
# sums_hints:
#    { public_key_fingerprint : [fp1, fp2, fp3, fp4] }
# path_hints :
#    { public_key_fingerprint : PATH  }
#    pass

from dataclasses import dataclass
from typing import Dict, List, Union, Tuple

from clvm.casts import int_from_bytes

from hsms.util.clvm_serialization import (
    transform_as_struct,
    clvm_list_of_bytes_to_list,
    clvm_list_of_ints_to_list,
    clvm_list_to_dict,
    clvm_to_list,
)

from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent


def _key_for_index(
    index, public_keys: BLSPublicKey, secret_exponents: BLSSecretExponent
) -> Union[BLSPublicKey, BLSSecretExponent]:
    if index < 0:
        return secret_exponents[-1 - index]
    return public_keys[index]


@dataclass
class KeyMetadata:
    public_keys: List[BLSPublicKey]
    secret_exponents: List[BLSSecretExponent]
    sums_hints: Dict[BLSPublicKey, List[Union[BLSPublicKey, BLSSecretExponent]]]
    path_hints: Dict[BLSPublicKey, Tuple[BLSPublicKey, List[int]]]

    def _build_lookup(self):
        d = {}
        for idx, pk in enumerate(self.public_keys):
            d[pk] = idx
        for idx, se in enumerate(self.secret_exponents):
            d[se.public_key] = -1 - idx
        return d

    def to_clvm(self):
        lookup = self._build_lookup()

        def as_pub_key(key: Union[BLSPublicKey, BLSSecretExponent]) -> BLSPublicKey:
            if isinstance(key, BLSSecretExponent):
                return key.public_key()
            return key

        t1 = [
            (lookup.get(k), (lookup.get(v[0]), v[1]))
            for k, v in self.path_hints.items()
        ]

        return [
            [bytes(_) for _ in self.public_keys],
            [int(_) for _ in self.secret_exponents],
            [
                [lookup.get(k)] + [lookup.get(as_pub_key(_)) for _ in v]
                for k, v in self.sums_hints.items()
            ],
            [
                [lookup.get(k)] + [lookup.get(v[0])] + list(v[1])
                for k, v in self.path_hints.items()
            ],
        ]

    @classmethod
    def from_clvm(cls, program) -> "KeyMetadata":
        a1, a2, a3, a4 = transform_as_struct(
            program,
            lambda obj: clvm_list_of_bytes_to_list(obj, BLSPublicKey.from_bytes),
            lambda obj: clvm_list_of_ints_to_list(obj, BLSSecretExponent.from_int),
            lambda obj: clvm_list_to_dict(
                obj,
                lambda k, v: (int_from_bytes(k.atom), clvm_list_of_ints_to_list(v)),
            ),
            lambda obj: clvm_to_list(
                obj,
                lambda o: (
                    int_from_bytes(o.pair[0].atom),
                    clvm_list_of_ints_to_list(o.pair[1]),
                ),
            ),
        )
        sums_hints = dict(
            [
                (_key_for_index(k, a1, a2), [_key_for_index(_, a1, a2) for _ in v])
                for k, v in a3.items()
            ]
        )
        path_hints = dict(
            [
                (_key_for_index(k, a1, a2), (_key_for_index(v[0], a1, a2), v[1:]))
                for k, v in a4
            ]
        )
        return cls(a1, a2, sums_hints, path_hints)
