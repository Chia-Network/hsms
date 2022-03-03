import dataclasses

import blspy

from chiasim.atoms.ints import uint32
from chiasim.hashable import bytes32, BLSSignature, BLSPublicKey

GROUP_ORDER = (
    52435875175126190479447740508185965837690552500527637822603658699938581184513
)


@dataclasses.dataclass
class BLSSecretExponent(uint32):
    def private_key(self):
        return blspy.PrivateKey.from_bytes(bytes(self % GROUP_ORDER))

    def sign(self, message_hash: bytes32) -> BLSSignature:
        return BLSSignature(
            self.private_key().sign_prepend_prehashed(message_hash).serialize()
        )

    def public_key(self) -> BLSPublicKey:
        return BLSPublicKey(self.private_key().get_public_key().serialize())
