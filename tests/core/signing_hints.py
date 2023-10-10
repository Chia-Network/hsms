from dataclasses import dataclass

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent

from hsms.util.clvm_serde import Nonexpandable


@dataclass
class SumHint(Nonexpandable):
    public_keys: list[BLSPublicKey]
    synthetic_offset: BLSSecretExponent


@dataclass
class PathHint(Nonexpandable):
    root_public_key: BLSPublicKey
    path: list[int]
