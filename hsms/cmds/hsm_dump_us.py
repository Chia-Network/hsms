import argparse
import sys
import zlib

from hsms.clvm.disasm import disassemble
from hsms.cmds.hsms import summarize_unsigned_spend
from hsms.core.unsigned_spend import UnsignedSpend
from hsms.util.qrint_encoding import a2b_qrint


def file_or_string(p) -> str:
    try:
        with open(p) as f:
            text = f.read().strip()
    except Exception:
        text = p
    return text


def dump_coin_spend(coin_spend):
    coin = coin_spend.coin
    print(f"parent coin: {coin.parent_coin_info.hex()}")
    print(f"     amount: {coin.amount}")
    print("     puzzle:", end="")
    if coin_spend.puzzle_reveal.tree_hash() == coin.puzzle_hash:
        print(f" {disassemble(coin_spend.puzzle_reveal)}")
    else:
        print(" ** bad puzzle reveal")
    print(f"   solution: {disassemble(coin_spend.solution)}")


def dump_unsigned_spend(unsigned_spend):
    count = len(unsigned_spend.coin_spends)
    print()
    print(f"coin count: {count}")
    print()
    for coin_spend in unsigned_spend.coin_spends:
        dump_coin_spend(coin_spend)


def fromhex_or_qrint(s: str) -> bytes:
    try:
        return a2b_qrint(s)
    except ValueError:
        pass
    return bytes.fromhex(s)


def hsms_dump_us(args, parser):
    """
    Try to handle input in qrint or hex, with or without zlib compression
    """
    blob = fromhex_or_qrint(file_or_string(args.unsigned_spend))
    try:
        blob = zlib.decompress(blob)
    except zlib.error:
        pass
    unsigned_spend = UnsignedSpend.from_bytes(blob)
    summarize_unsigned_spend(unsigned_spend)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Dump information about `UnsignedSpend`"
    )
    parser.add_argument(
        "unsigned_spend",
        metavar="hex-encoded-unsigned-spend-or-file",
        help="hex-encoded `UnsignedSpend`",
    )
    return parser


def main(argv=sys.argv[1:]):
    parser = create_parser()
    args = parser.parse_args(argv)
    return hsms_dump_us(args, parser)


if __name__ == "__main__":
    main()
