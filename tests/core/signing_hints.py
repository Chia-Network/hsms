from dataclasses import dataclass

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent

from hsms.util.clvm_serde import Frugal


@dataclass
class SumHint(Frugal):
    public_keys: list[BLSPublicKey]
    synthetic_offset: BLSSecretExponent


@dataclass
class PathHint(Frugal):
    root_public_key: BLSPublicKey
    path: list[int]
