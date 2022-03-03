import blspy

from ..atoms import streamable, hash_pointer

from .sized_bytes import bytes32


def bls_hash(s) -> bytes32:
    return bytes32(blspy.Util.hash256(s))


@streamable
class Message:
    data: bytes

    def stream(self, f):
        f.write(self.data)

    def __str__(self):
        return self.data.hex()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, str(self))


MessageHash = hash_pointer(Message, bls_hash)
