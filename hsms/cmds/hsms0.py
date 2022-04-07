#!/usr/bin/env python

from typing import BinaryIO, Dict, Iterable, List, Optional, TextIO

import argparse
import io
import subprocess
import sys

import segno

from hsms.bls12_381.BLSSecretExponent import BLSSecretExponent, BLSSignature
from hsms.process.unsigned_spend import UnsignedSpend
from hsms.process.sign import sign
from hsms.streamables import Program
from hsms.util.qrint_encoding import a2b_qrint, b2a_qrint


def create_unsigned_spend_pipeline(f: BinaryIO) -> Iterable[UnsignedSpend]:
    print("waiting for base64-encoded signing requests")
    while True:
        try:
            line = f.readline().strip()
            if len(line) == 0:
                break
            blob = a2b_qrint(line)
            program = Program.from_bytes(blob)
            yield UnsignedSpend.from_program(program)
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


def hsms(args, parser):
    wallet = parse_private_key_file(args)
    unsigned_spend_pipeline = create_unsigned_spend_pipeline(sys.stdin)
    for unsigned_spend in unsigned_spend_pipeline:
        signature_info = sign(unsigned_spend, wallet)
        if signature_info:
            signature = sum(
                [_.signature for _ in signature_info], start=BLSSignature.zero()
            )
            encoded_sig = b2a_qrint(bytes(signature))
            print(encoded_sig)
            qr = segno.make_qr(encoded_sig)
            qr.terminal()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage private keys and process signing requests"
    )
    parser.add_argument(
        "-c",
        "--create-private-key",
        nargs=1,
        help="create keys for non-existent files",
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
