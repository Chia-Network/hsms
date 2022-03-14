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

import binascii
import sys

import segno

from hsms.bls12_381 import BLSSignature, BLSPublicKey


def create_signature_pipeline(f):
    while True:
        try:
            line = f.readline()
            if len(line) == 0:
                break
            blob = binascii.a2b_base64(line)
            breakpoint()
            signature = BLSSignature.from_bytes(blob)
            yield signature
        except Exception as ex:
            print(ex)


def main():
    signature_pipeline = create_signature_pipeline(sys.stdin)
    signatures = [_ for _ in signature_pipeline]
    final_signature = sum(signatures, start=BLSSignature.zero())
    print(signatures)
    print()
    print(final_signature)
    qr = segno.make_qr(bytes(final_signature).hex())
    qr.terminal()

    pubkey = BLSPublicKey.from_bytes(
        bytes.fromhex(
            "901d9807932291dfbc5b78d7e405084b3535e2170306cc484b53eb0890230f18d73f475001dd9f2a3de29937be5e9478"
        )
    )
    message = bytes.fromhex(
        "4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a"
    )
    hash_key_pairs = [BLSSignature.aggsig_pair(pubkey, message)]
    r = final_signature.validate(hash_key_pairs)
    print(f"r = {r}")


if __name__ == "__main__":
    main()
