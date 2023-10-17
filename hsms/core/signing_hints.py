from dataclasses import dataclass

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent

from hsms.util.clvm_serde import Frugal


@dataclass
class SumHint(Frugal):
    public_keys: list[BLSPublicKey]
    synthetic_offset: BLSSecretExponent

    def final_public_key(self) -> BLSPublicKey:
        return sum(self.public_keys, start=self.synthetic_offset.public_key())


@dataclass
class PathHint(Frugal):
    root_public_key: BLSPublicKey
    path: list[int]

    def public_key(self) -> BLSPublicKey:
        return self.root_public_key.child_for_path(self.path)


PathHints = dict[BLSPublicKey, PathHint]
SumHints = dict[BLSPublicKey, SumHint]
