import io

from clvm.casts import int_from_bytes, int_to_bytes

from ..atoms import streamable, uint64

from .Hash import std_hash
from .Program import ProgramHash

from .sized_bytes import bytes32


@streamable
class Coin:
    """
    This structure is used in the body for the reward and fees genesis coins.
    """
    parent_coin_info: "CoinName"
    puzzle_hash: ProgramHash
    amount: uint64

    @classmethod
    def from_bytes(cls, blob):
        parent_coin_info = blob[:32]
        puzzle_hash = blob[32:64]
        amount = int_from_bytes(blob[64:])
        return Coin(parent_coin_info, puzzle_hash, uint64(amount))

    def __bytes__(self):
        f = io.BytesIO()
        f.write(self.parent_coin_info)
        f.write(self.puzzle_hash)
        f.write(int_to_bytes(self.amount))
        return f.getvalue()

    def name(self) -> "CoinName":
        return CoinName(self)


class CoinPointer(bytes32):
    def __new__(cls, v):
        if isinstance(v, Coin):
            v = std_hash(bytes(v))
        return bytes32.__new__(cls, v)

    async def obj(self, storage):
        blob = await storage.hash_preimage(self)
        return Coin.from_bytes(blob)


CoinName = CoinPointer

Coin.__annotations__["parent_coin_info"] = CoinName
