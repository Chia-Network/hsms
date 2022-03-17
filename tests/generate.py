import hashlib
import hmac

from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent
from hsms.streamables import bytes32


def bytes32_generate(nonce: int, namespace: str = "bytes32") -> bytes32:
    return bytes32(
        hmac.HMAC(
            namespace.encode(), nonce.to_bytes(32, "big"), digestmod=hashlib.sha256
        ).digest()
    )


def uint256_generate(nonce: int, namespace: str = "uint256") -> int:
    return int.from_bytes(bytes32_generate(nonce, namespace), "big")


def se_generate(nonce: int, namespace: str = "BLSSecretExponent") -> BLSSecretExponent:
    return BLSSecretExponent.from_int(uint256_generate(nonce))


def pk_generate(nonce: int, namespace: str = "BLSPublicKey") -> BLSPublicKey:
    return se_generate(nonce, namespace).public_key()
