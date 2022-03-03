import blspy

from chiasim.atoms import uint64
from chiasim.hashable import BLSPublicKey, BLSSignature, Coin, ProgramHash


HIERARCHICAL_PRIVATE_KEY = blspy.ExtendedPrivateKey.from_seed(b"foo")
POOL_PRIVATE_KEYS = [HIERARCHICAL_PRIVATE_KEY.private_child(_).get_private_key() for _ in range(100)]
POOL_PUBLIC_KEYS = [BLSPublicKey.from_bytes(_.get_public_key().serialize()) for _ in POOL_PRIVATE_KEYS]
POOL_LOOKUP = dict(zip(POOL_PUBLIC_KEYS, POOL_PRIVATE_KEYS))


def get_pool_public_key(index=0) -> BLSPublicKey:
    # TODO: make this configurable
    return POOL_PUBLIC_KEYS[index]


def signature_for_coinbase(coin: Coin, pool_private_key: blspy.PrivateKey):
    message_hash = coin.name()
    return BLSSignature(pool_private_key.sign_prepend_prehashed(message_hash).serialize())


def sign_coinbase_coin(coin: Coin, public_key: BLSPublicKey):
    private_key = POOL_LOOKUP.get(public_key)
    if private_key is None:
        raise ValueError("unknown public key")
    return signature_for_coinbase(coin, private_key)


def create_coinbase_coin(block_index: int, puzzle_hash: ProgramHash, reward: uint64):
    block_index_as_hash = block_index.to_bytes(32, "big")
    return Coin(block_index_as_hash, puzzle_hash, reward)


def create_coinbase_coin_and_signature(
        block_index: int, puzzle_hash: ProgramHash,
        reward: uint64, public_key: BLSPublicKey):
    coin = create_coinbase_coin(block_index, puzzle_hash, reward)
    signature = sign_coinbase_coin(coin, public_key)
    return coin, signature
