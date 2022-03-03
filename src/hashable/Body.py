
from atoms import streamable, uint64, streamable_list

from .BLSSignature import BLSSignature
from .Coin import Coin
from .Program import Program


@streamable
class Body:
    """
    This structure is pointed to by the Header, and contains everything necessary to determine
    the additions and removals from a block.
    """
    coinbase_signature: BLSSignature
    coinbase_coin: Coin
    fees_coin: Coin
    solution_program: Program
    program_cost: uint64
    aggregated_signature: BLSSignature


BodyList = streamable_list(Body)
