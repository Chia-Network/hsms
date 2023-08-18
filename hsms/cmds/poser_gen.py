from hashlib import sha256

import argparse


from chia_base.bls12_381 import BLSPublicKey
from chia_base.core.coin import Coin

from hsms.streamables.coin_spend import CoinSpend
from hsms.process.unsigned_spend import UnsignedSpend
from hsms.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    puzzle_for_synthetic_public_key,
    solution_for_conditions,
)
from hsms.util.byte_chunks import chunks_for_zlib_blob
from hsms.util.qrint_encoding import b2a_qrint


DEFAULT_PARENT_COIN_ID = sha256(b"fake_id").digest()


def bytes32_fromhex(s: str) -> bytes:
    try:
        b = bytes.fromhex(s)
        if len(b) == 32:
            return b
    except Exception:
        pass
    raise ValueError("not 64 bytes of hex")


DESCRIPTION = (
    "Proof of secret exponent request generator.\n\n"
    'Generate a fake "challenge coin" for the hsms to sign to prove ownership '
    "of the private key corresponding to a given public key."
)
EPILOG = "Output is in qrint form."


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument(
        "--parent-coin-id",
        type=bytes32_fromhex,
        default=DEFAULT_PARENT_COIN_ID,
        help="64 character hex representing parent coin id",
    )
    parser.add_argument(
        "--network-id",
        type=bytes.fromhex,
        default=b"",
        help="hex representing network id",
    )
    parser.add_argument(
        "-c",
        "--chunk-size",
        type=int,
        default=255,
        help="maximum byte count for each QR code",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    parser.add_argument("bech32m_public_key", help="bech32m-encoded public key")
    parser.add_argument("message", help="message to embed in challenge")
    args = parser.parse_args()

    verbose = not args.quiet

    public_key = BLSPublicKey.from_bech32m(args.bech32m_public_key)
    puzzle = puzzle_for_synthetic_public_key(public_key)
    puzzle_hash = puzzle.tree_hash()

    coin = Coin(args.parent_coin_id, puzzle_hash, 1)
    coin_spend = CoinSpend(coin, puzzle, solution_for_conditions(args.message))
    sum_hints = []
    path_hints = []
    agg_sig_me_network_suffix = b""  # hack to keep unsigned spend shorter
    unsigned_spend = UnsignedSpend(
        [coin_spend], sum_hints, path_hints, agg_sig_me_network_suffix
    )

    with open("us.qr", "w") as f:
        f.write(b2a_qrint(bytes(unsigned_spend)))

    print(f"challenge coin id: {coin.name().hex()}\n")

    blob = bytes(unsigned_spend)
    chunks = [b2a_qrint(_) for _ in chunks_for_zlib_blob(blob, args.chunk_size)]
    if verbose:
        print(f"chunk count: {len(chunks)}\n")

    for chunk in chunks:
        print(chunk)
        if verbose:
            print()

    if verbose:
        print(
            "Output is in qrint form. Use \n\n`segno --compact CHUNK`"
            "\n\nto create a QR code, where `CHUNK` is a qrint value above"
        )
        print(
            "Note: `segno` can also generate PNG files. Use "
            "`segno -h` for more info."
        )


if __name__ == "__main__":
    main()
