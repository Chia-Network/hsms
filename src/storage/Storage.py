from ..hashable import Hash


class Storage:

    async def hash_preimage(self, hash: Hash) -> bytes:
        raise NotImplementedError

    async def add_preimage(self, blob: bytes) -> None:
        raise NotImplementedError
