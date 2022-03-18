from typing import Dict, List, Tuple

from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent


SumHint = Tuple[List[BLSPublicKey], BLSSecretExponent]
PathHint = Tuple[BLSPublicKey, List[int]]

SumHints = Dict[BLSPublicKey, SumHint]
PathHints = Dict[BLSPublicKey, PathHint]
