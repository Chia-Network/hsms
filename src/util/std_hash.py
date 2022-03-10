import hashlib

from streamables.sized_bytes import bytes32


def std_hash(b) -> bytes32:
    """
    The standard hash used in many places.
    """
    return bytes32(hashlib.sha256(bytes(b)).digest())
