from dataclasses import dataclass
from typing import Dict, List, Union, Tuple

from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent, BLSSignature
from hsms.streamables import bytes32, CoinSpend


@dataclass
class SignatureInfo:
    signature: BLSSignature
    partial_public_key: BLSPublicKey
    final_public_key: BLSPublicKey
    message: bytes


SumHints = Dict[BLSPublicKey, List[Union[BLSPublicKey, BLSSecretExponent]]]
PathHints = Dict[BLSPublicKey, Tuple[BLSPublicKey, List[int]]]


@dataclass
class UnsignedSpend:
    coin_spends: List[CoinSpend]
    sum_hints: SumHints
    path_hints: PathHints
    agg_sig_me_network_suffix: bytes32
