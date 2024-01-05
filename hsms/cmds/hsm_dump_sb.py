import argparse

from chia_base.cbincode import from_bytes
from chia_base.core import SpendBundle

from hsms.debug.debug_spend_bundle import debug_spend_bundle


def file_or_string(p) -> str:
    try:
        with open(p) as f:
            text = f.read().strip()
    except Exception:
        text = p
    return text


def hsms_dump_sb(args, parser):
    blob = bytes.fromhex(file_or_string(args.spend_bundle))
    spend_bundle = from_bytes(SpendBundle, blob)
    validates = debug_spend_bundle(spend_bundle)
    assert validates is True


def create_parser():
    parser = argparse.ArgumentParser(description="Dump information about `SpendBundle`")
    parser.add_argument(
        "spend_bundle",
        metavar="hex-encoded-spend-bundle-or-file",
        help="hex-encoded `SpendBundle`",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return hsms_dump_sb(args, parser)


if __name__ == "__main__":
    main()
