import hashlib

import blspy
from hashable import BLSPublicKey
from wallet.BLSPrivateKey import BLSPrivateKey


def fingerprint_for_pk(pk):
    """
    Take a public key and get the fingerprint for it.
    It's just the last four bytes of the sha256 hash.
    """
    return hashlib.sha256(bytes(pk)).digest()[-4:]


class BLSPublicHDKey:
    """
    A class for public hierarchical deterministic bls keys.
    """

    @classmethod
    def from_bytes(cls, blob):
        bls_public_hd_key = blspy.G1Element.from_bytes(blob)
        return cls(bls_public_hd_key)

    def __init__(self, bls_public_hd_key):
        self._bls_public_hd_key = bls_public_hd_key

    def public_hd_child(self, idx) -> "BLSPublicHDKey":
        return self.from_bytes(bytes(self._bls_public_hd_key.public_child(idx)))

    def public_child(self, idx) -> BLSPublicKey:
        return self.public_hd_child(idx).public_key()

    def public_key(self):
        return BLSPublicKey(self._bls_public_hd_key)

    def fingerprint(self):
        return fingerprint_for_pk(self.public_key())

    def __bytes__(self):
        return bytes(self._bls_public_hd_key)

    def __str__(self):
        return bytes(self).hex()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)


class BLSPrivateHDKey:
    """
    A class for private hierarchical deterministic bls keys.
    """

    @classmethod
    def from_seed(cls, seed_bytes: bytes):
        bls_private_hd_key = blspy.AugSchemeMPL.key_gen(seed_bytes)
        return cls(bls_private_hd_key)

    @classmethod
    def from_bytes(cls, blob):
        bls_private_hd_key = blspy.PrivateKey.from_bytes(blob)
        return cls(bls_private_hd_key)

    def __init__(self, bls_private_hd_key):
        self._bls_private_hd_key = bls_private_hd_key

    def public_hd_key(self):
        blob = bytes(self._bls_private_hd_key.get_g1())
        return BLSPublicHDKey.from_bytes(blob)

    def private_hd_child(self, idx):
        return self.__class__(
            blspy.AugSchemeMPL.derive_child_sk(self._bls_private_hd_key, idx)
        )

    def public_hd_child(self, idx):
        return self.public_hd_key().public_hd_child(idx)

    def secret_exponent_for_child(self, idx):
        return self.private_hd_child(idx).secret_exponent()

    def private_child(self, idx):
        return self.private_hd_child(idx).private_key()

    def secret_exponent(self):
        return int.from_bytes(bytes(self._bls_private_hd_key.get_private_key()), "big")

    def private_key(self):
        return BLSPrivateKey(self._bls_private_hd_key)

    def public_child(self, idx):
        return self.public_hd_child(idx).public_key()

    def public_key(self):
        return self.public_hd_key().public_key()

    def fingerprint(self):
        return fingerprint_for_pk(self.public_key())

    def __bytes__(self):
        return bytes(self._bls_private_hd_key)

    def __str__(self):
        return "<prv for:%s>" % self.public_key()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)
