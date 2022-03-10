import blspy

from streamables import bytes32

from util.std_hash import std_hash

from .BLSSignature import BLSSignature
from .BLSPublicKey import BLSPublicKey

GROUP_ORDER = (
    52435875175126190479447740508185965837690552500527637822603658699938581184513
)


class BLSPrivateKey:
    def __init__(self, sk: blspy.PrivateKey):
        self._sk = sk

    @classmethod
    def from_seed(cls, blob: bytes) -> "BLSPrivateKey":
        secret_exponent = int.from_bytes(std_hash(blob), "big")
        return cls.from_secret_exponent(secret_exponent)

    @classmethod
    def from_secret_exponent(cls, secret_exponent) -> "BLSPrivateKey":
        secret_exponent %= GROUP_ORDER
        blob = secret_exponent.to_bytes(32, "big")
        return cls.from_bytes(blob)

    @classmethod
    def from_bytes(cls, blob) -> "BLSPrivateKey":
        return cls(blspy.PrivateKey.from_bytes(blob))

    def fingerprint(self) -> int:
        return self._sk.get_g1().get_fingerprint()

    def sign(self, message_hash: bytes32) -> BLSSignature:
        return BLSSignature(blspy.AugSchemeMPL.sign(self._sk, message_hash))

    def public_key(self) -> BLSPublicKey:
        return BLSPublicKey(self._sk.get_g1())

    def secret_exponent(self):
        return int.from_bytes(bytes(self), "big")

    def hardened_child(self, index: int) -> "BLSPrivateKey":
        return BLSPrivateKey(blspy.AugSchemeMPL.derive_child_sk(self._sk, index))

    def child(self, index: int) -> "BLSPrivateKey":
        return BLSPrivateKey(
            blspy.AugSchemeMPL.derive_child_sk_unhardened(self._sk, index)
        )

    def __int__(self):
        return self.secret_exponent()

    def __bytes__(self):
        return bytes(self._sk)

    def __str__(self):
        return "<prv for:%s>" % self.public_key()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)
