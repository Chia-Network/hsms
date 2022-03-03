import hashlib

from .sized_bytes import bytes32


Hash = bytes32


def std_hash(b) -> Hash:
    """
    The standard hash used in many places.
    """
    return Hash(hashlib.sha256(bytes(b)).digest())
