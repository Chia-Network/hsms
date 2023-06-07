import io

from clvm_rs import Program

from hsms.atoms import uint64
from hsms.meta import streamable
from hsms.util.std_hash import std_hash

from . import bytes32


@streamable
class Coin:
    """
    This structure is used in the body for the reward and fees genesis coins.
    """

    parent_coin_info: bytes32
    puzzle_hash: bytes32
    amount: uint64

    @classmethod
    def from_bytes(cls, blob):
        parent_coin_info = blob[:32]
        puzzle_hash = blob[32:64]
        amount = Program.int_from_bytes(blob[64:])
        return Coin(parent_coin_info, puzzle_hash, amount)

    def __bytes__(self):
        f = io.BytesIO()
        f.write(self.parent_coin_info)
        f.write(self.puzzle_hash)
        f.write(Program.int_to_bytes(self.amount))
        return f.getvalue()

    def name(self) -> bytes32:
        return std_hash(bytes(self))
