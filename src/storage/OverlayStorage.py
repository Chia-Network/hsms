from chiasim.hashable import Hash

from .Storage import Storage


class OverlayStorage(Storage):
    def __init__(self, *db_list):
        self._db_list = db_list

    async def hash_preimage(self, hash: Hash) -> bytes:
        for db in self._db_list:
            v = await db.hash_preimage(hash)
            if v is not None:
                return v
        return None
