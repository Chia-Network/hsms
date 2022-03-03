from ..hashable import Hash, Unspent


class UnspentDB:
    async def unspent_for_coin_name(self, coin_name: Hash) -> Unspent:
        raise NotImplementedError

    async def set_unspent_for_coin_name(self, coin_name: Hash, unspent: Unspent) -> None:
        raise NotImplementedError

    async def rollback_to_block(self, uint32):
        raise NotImplementedError
