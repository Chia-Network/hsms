from dataclasses import dataclass
from typing import List


from chia_base.atoms import bytes96
from chia_base.meta import Streamable

from .coin_spend import CoinSpend


@dataclass(frozen=True)
class SpendBundle(Streamable):
    """
    This is a list of coins being spent along with their solution programs, and a
    single aggregated signature. This is the object that most closely corresponds to
    a bitcoin transaction (although because of non-interactive signature aggregation,
    the boundaries between transactions are more flexible than in bitcoin).
    """

    coin_spends: List[CoinSpend]
    aggregated_signature: bytes96

    def __add__(self, other: "SpendBundle") -> "SpendBundle":
        return self.__class__(
            self.coin_spends + other.coin_spends,
            self.aggregated_signature + other.aggregated_signature,
        )
