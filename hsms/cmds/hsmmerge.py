#!/usr/bin/env python

import argparse
import binascii

from hsms.bls12_381.BLSSecretExponent import BLSSignature
from hsms.process.unsigned_spend import UnsignedSpend
from hsms.process.sign import generate_synthetic_offset_signatures
from hsms.streamables import SpendBundle
from hsms.util.debug_spend_bundle import debug_spend_bundle


def create_spend_bundle(unsigned_spend, signatures):

    extra_signatures = generate_synthetic_offset_signatures(unsigned_spend)

    # now let's try adding them all together and creating a `SpendBundle`

    all_signatures = signatures + [sig_info.signature for sig_info in extra_signatures]
    total_signature = sum(all_signatures, start=all_signatures[0].zero())

    return SpendBundle(unsigned_spend.coin_spends, total_signature)


def file_or_string(p) -> str:
    try:
        with open(p) as f:
            text = f.readline().strip()
    except Exception:
        text = p
    return text


def hsmsmerge(args, parser):
    blob = binascii.a2b_hex(args.unsigned_spend.read())
    unsigned_spend = UnsignedSpend.from_bytes(blob)
    signatures = [
        BLSSignature.from_bytes(binascii.a2b_hex(file_or_string(_)))
        for _ in args.signature
    ]
    spend_bundle = create_spend_bundle(unsigned_spend, signatures)
    print(bytes(spend_bundle).hex())
    validates = debug_spend_bundle(spend_bundle)
    assert validates is True


def create_parser():
    parser = argparse.ArgumentParser(
        description="Create a signed `SpendBundle` from `UnsignedSpends` and signatures."
    )
    parser.add_argument(
        "unsigned_spend",
        metavar="path-to-unsigned-spend-as-hex",
        help="file containing hex-encoded `UnsignedSpends`",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "signature",
        metavar="hex-encoded-signature",
        nargs="+",
        help="hex-encoded signature",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    hsmsmerge(args, parser)


if __name__ == "__main__":
    main()
