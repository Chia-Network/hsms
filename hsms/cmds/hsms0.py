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

import argparse
import binascii
import io
import subprocess
import sys

import segno

from hsms.process.unsigned_spend import UnsignedSpend
from hsms.process.sign import sign
from hsms.streamables import Program
from hsms.bls12_381.BLSSecretExponent import BLSSecretExponent, BLSSignature


def build_wallet_for_secret_exponents(
    secret_exponents: List[BLSSecretExponent],
) -> Dict[int, BLSSecretExponent]:
    d = {}
    for private_key in secret_exponents:
        d.setdefault(private_key.fingerprint(), []).append(private_key)
    return d


def find_secret_key_for_unsigned_spend(
    wallet, unsigned_spend: UnsignedSpend
) -> Optional[BLSSecretExponent]:
    for secret_key in wallet.get(unsigned_spend.path_hints.fingerprint, []):
        for index in unsigned_spend.path_hints.path:
            secret_key = secret_key.child(index)
        if secret_key.public_key() == unsigned_spend.partial_pubkey:
            return secret_key
    return None


def generate_signature(
    wallet: Dict[int, BLSSecretExponent],
    unsigned_spend: UnsignedSpend,
) -> Optional[BLSSignature]:
    secret_key = find_secret_key_for_unsigned_spend(wallet, unsigned_spend)
    if secret_key:
        return secret_key.sign(unsigned_spend.message, unsigned_spend.final_pubkey)
    return None


def create_unsigned_spend_pipeline(f):
    print("waiting for base64-encoded signing requests")
    while True:
        try:
            line = f.readline()
            if len(line) == 0:
                break
            blob = binascii.a2b_base64(line)
            program = Program.from_bytes(blob)
            yield UnsignedSpend.from_program(program)
        except Exception as ex:
            print(ex)


def replace_with_gpg_pipe(args, f):
    gpg_args = ["gpg", "-d"]
    if args.gpg_argument:
        gpg_args.extend(args.gpg_argument.split())
    gpg_args.append(f.name)
    popen = subprocess.Popen(gpg_args, stdout=subprocess.PIPE)
    return io.TextIOWrapper(popen.stdout)


def parse_private_key_file(args):
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
            encoded_sig = binascii.b2a_base64(bytes(signature)).decode()
            print(encoded_sig)
            qr = segno.make_qr(encoded_sig)
            qr.terminal()


def create_parser():
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
    hsms(args, parser)


if __name__ == "__main__":
    main()
