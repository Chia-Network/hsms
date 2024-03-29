from typing import List

import argparse

from chia_base.bls12_381 import BLSSignature
from chia_base.core import SpendBundle
from chia_base.cbincode import to_bytes

from hsms.core.unsigned_spend import UnsignedSpend
from hsms.process.sign import generate_synthetic_offset_signatures
from hsms.util.qrint_encoding import a2b_qrint


def create_spend_bundle(unsigned_spend: UnsignedSpend, signatures: List[BLSSignature]):
    extra_signatures = generate_synthetic_offset_signatures(unsigned_spend)

    # now let's try adding them all together and creating a `SpendBundle`

    all_signatures = signatures + [sig_info.signature for sig_info in extra_signatures]
    total_signature = sum(all_signatures, start=all_signatures[0].zero())

    return SpendBundle(unsigned_spend.coin_spends, total_signature)


def file_or_string(p) -> str:
    try:
        with open(p) as f:
            text = f.read().strip()
    except Exception:
        text = p
    return text


def hsmsmerge(args, parser):
    blob = a2b_qrint(file_or_string(args.unsigned_spend))
    unsigned_spend = UnsignedSpend.from_bytes(blob)
    signatures = [
        BLSSignature.from_bytes(a2b_qrint(file_or_string(_))) for _ in args.signature
    ]
    spend_bundle = create_spend_bundle(unsigned_spend, signatures)
    print(to_bytes(spend_bundle).hex())


def create_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Create a signed `SpendBundle` from `UnsignedSpends` " "and signatures."
        )
    )
    parser.add_argument(
        "unsigned_spend",
        metavar="path-to-unsigned-spend-as-hex",
        help="file containing hex-encoded `UnsignedSpends`",
    )
    parser.add_argument(
        "signature",
        metavar="qrint-encoded-signature",
        nargs="+",
        help="qrint-encoded signature",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return hsmsmerge(args, parser)


if __name__ == "__main__":
    main()
