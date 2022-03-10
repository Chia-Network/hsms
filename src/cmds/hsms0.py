#!/usr/bin/env python

# simplest HSM simulator possible
# it accepts these parameters:
# - message
# - partial pubkey corresponding to the private key
# - the hint fingerprint and path of the private key
# - full pubkey to be used in the final signature (optional)

"""
m: message `bytes32`
p: partial pubkey `G1Element`
f: final pubkey `G1Element` (optional, defaults to partial)
t: fingerprint lists
h: path hints
"""

from typing import Dict, List, Optional

from blspy import G1Element, G2Element

import segno

from hashable import bytes32, Program, BLSPublicKey
from wallet.BLSPrivateKey import BLSPrivateKey


class PathHint:
    fingerprint: bytes  # length == 4
    path: List[int]

    def __bytes__(self):
        pass

    @classmethod
    def from_bytes(cls, blob) -> "SimpleSigningInfo":
        pass


class SimpleSigningInfo:
    message: bytes32
    partial_pubkey: G1Element
    final_pubkey: Optional[G1Element]
    path_hints: List[PathHint]

    def __bytes__(self):
        pass

    @classmethod
    def from_bytes(cls, blob) -> "SimpleSigningInfo":
        pass


def build_wallet_for_secret_exponents(
    secret_exponents: List[int],
) -> Dict[int, BLSPrivateKey]:
    d = {}
    for s in secret_exponents:
        private_key = BLSPrivateKey.from_secret_exponent(s)
        # breakpoint()
        d[private_key.fingerprint()] = private_key
    return d


def trivial_wallet() -> Dict[int, int]:
    return build_wallet_for_secret_exponents(
        [0x39443EF9A03473E4A58F11870B65C927788142E03134DB0C230728F413CFF81D]
    )


def generate_signature(
    message: bytes32,
    partial_pubkey: G1Element,
    path: List[int],
    wallet: Dict[int, BLSPrivateKey],
) -> Optional[G2Element]:
    fp = partial_pubkey.get_fingerprint()
    secret_key = wallet.get(fp)
    if secret_key:
        return secret_key.sign(message)


def main():
    wallet = trivial_wallet()
    while True:
        if 0:
            message = bytes32.fromhex(input("message (hex)> "))
            partial_pubkey = G1Element.from_bytes(
                bytes.fromhex(input("partial pubkey (hex)> "))
            )
            path_text = input("path (slash-separated int list) >")
            print(path_text)
        else:
            message = bytes32.fromhex(
                "4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a"
            )
            partial_pubkey = G1Element.from_bytes(
                bytes.fromhex(
                    "a53d42661673da60350e3630f16f5efd19267c83d0d69d85c18444ddcabdd7492388cd86f394b68e6c7ea20ede0d91c5"
                )
            )

            path_text = "2/3"
        path = [int(_) for _ in path_text.split("/")]
        print(message, partial_pubkey, path)
        signature = generate_signature(message, partial_pubkey, path, wallet)
        break
    hex_sig = bytes(signature).hex()
    print(hex_sig)
    qr = segno.make_qr(hex_sig)
    qr.terminal()


if __name__ == "__main__":
    main()
