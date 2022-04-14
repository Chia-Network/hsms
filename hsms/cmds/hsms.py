#!/usr/bin/env python

from decimal import Decimal
from typing import BinaryIO, Iterable, List, TextIO

import argparse
import io
import readline  # noqa: this allows long lines on stdin
import subprocess

import segno

from hsms.bls12_381.BLSSecretExponent import BLSSecretExponent, BLSSignature
from hsms.consensus.conditions import conditions_by_opcode
from hsms.process.sign import conditions_for_coin_spend, sign
from hsms.process.unsigned_spend import UnsignedSpend
from hsms.puzzles import conlang
from hsms.streamables import bytes32, Program
from hsms.util.bech32 import bech32_encode
from hsms.util.qrint_encoding import a2b_qrint, b2a_qrint


XCH_PER_MOJO = Decimal(1e12)


def create_unsigned_spend_pipeline() -> Iterable[UnsignedSpend]:
    print("waiting for qrint-encoded signing requests")
    while True:
        try:
            line = input("> ").strip()
            if len(line) == 0:
                break
            blob = a2b_qrint(line)
            program = Program.from_bytes(blob)
            yield UnsignedSpend.from_program(program)
        except EOFError:
            break
        except Exception as ex:
            print(ex)


def replace_with_gpg_pipe(args, f: BinaryIO) -> TextIO:
    gpg_args = ["gpg", "-d"]
    if args.gpg_argument:
        gpg_args.extend(args.gpg_argument.split())
    gpg_args.append(f.name)
    popen = subprocess.Popen(gpg_args, stdout=subprocess.PIPE)
    if popen is None or popen.stdout is None:
        raise ValueError("couldn't launch gpg")
    return io.TextIOWrapper(popen.stdout)


def parse_private_key_file(args) -> List[BLSSecretExponent]:
    secret_exponents = []
    for f in args.private_key_file:
        if f.name.endswith(".gpg"):
            f = replace_with_gpg_pipe(args, f)
        for line in f.readlines():
            try:
                secret_exponent = BLSSecretExponent.from_bech32m(line.strip())
                secret_exponents.append(secret_exponent)
            except ValueError:
                pass
    return secret_exponents


def summarize_unsigned_spend(unsigned_spend: UnsignedSpend):
    print()
    for coin_spend in unsigned_spend.coin_spends:
        xch_amount = Decimal(coin_spend.coin.amount) / XCH_PER_MOJO
        address = address_for_puzzle_hash(coin_spend.coin.puzzle_hash)
        print(f"COIN SPENT: {xch_amount:0.12f} xch at address {address}")
        conditions = conditions_for_coin_spend(coin_spend)

    print()
    for coin_spend in unsigned_spend.coin_spends:
        conditions = conditions_for_coin_spend(coin_spend)
        conditions_lookup = conditions_by_opcode(conditions)
        for create_coin in conditions_lookup.get(conlang.CREATE_COIN, []):
            puzzle_hash = create_coin.at("rf").atom
            address = address_for_puzzle_hash(puzzle_hash)
            amount = int(create_coin.at("rrf"))
            xch_amount = Decimal(amount) / XCH_PER_MOJO
            print(f"COIN CREATED: {xch_amount:0.12f} xch to {address}")
    print()


def address_for_puzzle_hash(puzzle_hash: bytes32) -> str:
    return bech32_encode("xch", puzzle_hash)


def check_ok():
    text = input('if this looks reasonable, enter "ok" to generate signature> ')
    return text.lower() == "ok"


def hsms(args, parser):
    wallet = parse_private_key_file(args)
    unsigned_spend_pipeline = create_unsigned_spend_pipeline()
    for unsigned_spend in unsigned_spend_pipeline:
        summarize_unsigned_spend(unsigned_spend)
        if not check_ok():
            continue
        signature_info = sign(unsigned_spend, wallet)
        if signature_info:
            signature = sum(
                [_.signature for _ in signature_info], start=BLSSignature.zero()
            )
            encoded_sig = b2a_qrint(bytes(signature))
            qr = segno.make_qr(encoded_sig)
            print()
            qr.terminal()
            print()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage private keys and process signing requests"
    )
    parser.add_argument(
        "-g", "--gpg-argument", help="argument to pass to gpg (besides -d).", default=""
    )
    parser.add_argument(
        # "-f",
        "private_key_file",
        metavar="path-to-private-keys",
        action="append",
        default=[],
        help="file containing bech32m-encoded secret exponents. If file name ends with .gpg, "
        '"gpg -d" will be invoked automatically. File is read one line at a time."',
        type=argparse.FileType("r"),
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    return hsms(args, parser)


if __name__ == "__main__":
    main()
