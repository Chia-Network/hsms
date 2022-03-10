import blspy


class BLSPublicKey:
    def __init__(self, g1: blspy.G1Element):
        self._g1 = g1

    @classmethod
    def from_bytes(cls, blob):
        bls_public_hd_key = blspy.G1Element.from_bytes(blob)
        return BLSPublicKey(bls_public_hd_key)

    def __bytes__(self) -> bytes:
        return bytes(self._g1)

    def child(self, index: int) -> "BLSPublicKey":
        return BLSPublicKey(
            blspy.AugSchemeMPL.derive_child_pk_unhardened(self._g1, index)
        )

    def fingerprint(self):
        return self._g1.get_fingerprint()

    def __str__(self):
        return bytes(self._g1).hex()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)
