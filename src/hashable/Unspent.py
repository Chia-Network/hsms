from atoms import uint32, streamable


@streamable
class Unspent:
    """
    These are values that correspond to a CoinName that are used
    in keeping track of the unspent database.
    """

    confirmed_block_index: uint32
    spent_block_index: uint32
