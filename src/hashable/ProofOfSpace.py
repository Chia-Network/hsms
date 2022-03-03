from atoms import streamable

from .BLSSignature import BLSPublicKey
from .Signature import PublicKey


@streamable
class ProofOfSpace:
    """
    This represents a proof of space, an "above-the-line" construct designed to
    rate-limit block creation.
    """
    pool_public_key: BLSPublicKey
    plot_public_key: PublicKey
    # TODO: more items
    # Farmer commitment
    # Size (k)
    # Challenge hash
    # X vals
