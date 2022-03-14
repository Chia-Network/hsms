from hsms.streamables import Hash, Unspent

from .UnspentDB import UnspentDB


class OverlayUnspentDB(UnspentDB):
    def __init__(self, *db_list):
        self._db_list = db_list

    async def unspent_for_coin_name(self, coin_name: Hash) -> Unspent:
        for db in self._db_list:
            v = await db.unspent_for_coin_name(coin_name)
            if v is not None:
                return v
        return None
