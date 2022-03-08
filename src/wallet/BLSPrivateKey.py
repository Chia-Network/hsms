import dataclasses

import blspy

from hashable import bytes32, BLSSignature, BLSPublicKey

GROUP_ORDER = (
    52435875175126190479447740508185965837690552500527637822603658699938581184513
)


@dataclasses.dataclass
class BLSPrivateKey:

    pk: blspy.PrivateKey

    @classmethod
    def from_bytes(cls, blob):
        return cls(blspy.PrivateKey.from_bytes(blob))

    @classmethod
    def from_secret_exponent(cls, secret_exponent):
        secret_exponent %= GROUP_ORDER
        blob = secret_exponent.to_bytes(32, "big")
        return cls(blspy.PrivateKey.from_bytes(blob))

    def sign(self, message_hash: bytes32) -> BLSSignature:
        return BLSSignature(blspy.AugSchemeMPL.sign(self.pk, message_hash))

    def public_key(self) -> BLSPublicKey:
        return BLSPublicKey(self.pk.get_public_key().serialize())

    def secret_exponent(self):
        return int.from_bytes(bytes(self), "big")

    def __bytes__(self):
        return self.pk.serialize()
