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

    def fingerprint(self) -> int:
        return self.pk.get_g1().get_fingerprint()

    def sign(self, message_hash: bytes32) -> BLSSignature:
        return BLSSignature(blspy.AugSchemeMPL.sign(self.pk, message_hash))

    def public_key(self) -> BLSPublicKey:
        return BLSPublicKey(bytes(self.pk.get_g1()))

    def secret_exponent(self):
        return int.from_bytes(bytes(self), "big")

    def hardened_child(self, index: int) -> "BLSPrivateKey":
        return BLSPrivateKey(blspy.AugSchemeMPL.derive_child_sk(self.pk, index))

    def child(self, index: int) -> "BLSPrivateKey":
        return BLSPrivateKey(
            blspy.AugSchemeMPL.derive_child_sk_unhardened(self.pk, index)
        )

    def __int__(self):
        return self.secret_exponent()

    def __bytes__(self):
        return bytes(self.pk)

    def __str__(self):
        return "<prv for:%s>" % self.public_key()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)
