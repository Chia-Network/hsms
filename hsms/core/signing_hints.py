from dataclasses import dataclass

from typing import Dict, List

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent

from hsms.clvm_serde import Frugal


@dataclass
class SumHint(Frugal):
    public_keys: List[BLSPublicKey]
    synthetic_offset: BLSSecretExponent

    def final_public_key(self) -> BLSPublicKey:
        return sum(self.public_keys, start=self.synthetic_offset.public_key())


@dataclass
class PathHint(Frugal):
    root_public_key: BLSPublicKey
    path: List[int]

    def public_key(self) -> BLSPublicKey:
        return self.root_public_key.child_for_path(self.path)


PathHints = Dict[BLSPublicKey, PathHint]
SumHints = Dict[BLSPublicKey, SumHint]
