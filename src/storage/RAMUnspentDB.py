from streamables import Hash, Unspent

from .UnspentDB import UnspentDB


class RAMUnspentDB(UnspentDB):
    def __init__(self, additions, confirmed_block_index):
        self._db = {}
        for _ in additions:
            unspent = Unspent(confirmed_block_index, 0)
            self._db[_.name()] = unspent

    async def unspent_for_coin_name(self, coin_name: Hash) -> Unspent:
        return self._db.get(coin_name)
