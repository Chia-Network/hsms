from .coin import Coin
from .program import Program

from hsms.atoms import streamable


@streamable
class CoinSpend:
    """
    This is a rather disparate data structure that validates coin transfers. It's generally populated
    with data from different sources, since burned coins are identified by name, so it is built up
    more often that it is streamed.
    """

    coin: Coin
    puzzle_reveal: Program
    solution: Program
