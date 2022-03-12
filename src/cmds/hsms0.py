#!/usr/bin/env python

# simplest HSM simulator possible
# it accepts these parameters:
# - message
# - partial pubkey corresponding to the private key
# - the hint fingerprint and path of the private key
# - full pubkey to be used in the final signature (optional)

"""
m: message `bytes32`
p: partial pubkey `BLSPublicKey`
f: final pubkey `BLSPublicKey` (optional, defaults to partial)
t: fingerprint lists
h: path hints
"""

from typing import Dict, List, Optional

import binascii
import sys

import segno

from streamables import Program, SigningRequest
from bls12_381.BLSSecretExponent import BLSSecretExponent, BLSSignature


def build_wallet_for_secret_exponents(
    secret_exponents: List[int],
) -> Dict[int, BLSSecretExponent]:
    d = {}
    for s in secret_exponents:
        private_key = BLSSecretExponent.from_int(s)
        d.setdefault(private_key.fingerprint(), []).append(private_key)
    return d


def trivial_wallet() -> Dict[int, int]:
    return build_wallet_for_secret_exponents(
        [0x39443EF9A03473E4A58F11870B65C927788142E03134DB0C230728F413CFF81D]
    )


def find_secret_key_for_signing_request(
    wallet, signing_request: SigningRequest
) -> Optional[BLSSecretExponent]:
    for secret_key in wallet.get(signing_request.path_hints.fingerprint, []):
        for index in signing_request.path_hints.path:
            secret_key = secret_key.child(index)
        if secret_key.public_key() == signing_request.partial_pubkey:
            return secret_key
    return None


def generate_signature(
    signing_request: SigningRequest,
    wallet: Dict[int, BLSSecretExponent],
) -> Optional[BLSSignature]:
    breakpoint()
    secret_key = find_secret_key_for_signing_request(wallet, signing_request)
    if secret_key:
        return secret_key.sign(signing_request.message, signing_request.final_pubkey)
    return None


def create_signing_request_pipeline(f):
    while True:
        try:
            line = f.readline()
            if len(line) == 0:
                break
            blob = binascii.a2b_base64(line)
            program = Program.from_bytes(blob)
            yield SigningRequest.from_clvm(program)
        except Exception as ex:
            print(ex)


def main():
    wallet = trivial_wallet()
    signing_request_pipeline = create_signing_request_pipeline(sys.stdin)
    for signing_request in signing_request_pipeline:
        print(signing_request)
        signature = generate_signature(signing_request, wallet)
        if signature:
            encoded_sig = binascii.b2a_base64(bytes(signature)).decode()
            print(encoded_sig)
            qr = segno.make_qr(encoded_sig)
            qr.terminal()


if __name__ == "__main__":
    main()
