from ..hashable import Hash, std_hash

from .Storage import Storage
from .UnspentDB import Unspent, UnspentDB


class RAM_DB(Storage, UnspentDB):

    def __init__(self):
        self._preimage_db = dict()
        self._unspent_db = dict()

    async def hash_preimage(self, hash: Hash) -> bytes:
        return self._preimage_db.get(hash)

    async def add_preimage(self, blob: bytes) -> None:
        self._preimage_db[std_hash(blob)] = blob

    async def unspent_for_coin_name(self, coin_name: Hash) -> Unspent:
        return self._unspent_db.get(coin_name)

    async def set_unspent_for_coin_name(self, coin_name: Hash, unspent: Unspent) -> None:
        self._unspent_db[coin_name] = unspent

    async def all_unspents(self):
        for coin_name, unspent in self._unspent_db.items():
            yield coin_name, unspent

    async def rollback_to_block(self, block_index):
        for v in self._unspent_db.values():
            if v.spent_block_index > block_index:
                v.spent_block_index = 0
            if v.confirmed_block_index > block_index:
                v.confirmed_block_index = 0
