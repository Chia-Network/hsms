#!/bin/env python3


from pathlib import Path

import argparse
import os
import secrets
import sys
import time

import segno

from hsms.bls12_381 import BLSSecretExponent

import hsms.cmds.hsms


def wait_for_usb_mount(path):
    print(f"insert USB stick for path {path}")
    while 1:
        if path.exists():
            return
        time.sleep(1)


def generate_secret(wallet_path):
    CLEAR_SCREEN = "\033[2J"
    secret_exponent = BLSSecretExponent.from_int(secrets.randbits(256))
    b = secret_exponent.as_bech32m()
    assert BLSSecretExponent.from_bech32m(b) == secret_exponent

    print("No secret found. We are generating you a new secret.")
    while True:
        print(f"write down your secret:\n\n{b}\n")
        input("hit return when done> ")
        print(CLEAR_SCREEN)
        t = input("enter your secret> ")
        if t == b:
            break
        diff_string = "".join(" " if a1 == a2 else "^" for a1, a2 in zip(t, b))
        print(f"{b} <= actual secret")
        print(f"{t} <= you entered")
        print(diff_string)
        print("fix it and let's try again")
        print()

    with open(wallet_path, "w") as f:
        f.write(t)

    print("you entered your secret correctly! Good job")

    public_key = secret_exponent.public_key().as_bech32m()
    print(f"your public key is {public_key}")
    print("Take a photo of it and share with your coordinator:")
    qr = segno.make_qr(public_key)
    print()
    qr.terminal(compact=True)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Wizard to look for USB mount point and key file and launch hsms"
    )
    parser.add_argument(
        "path_to_secret_exponent_file",
        metavar="bech32m-encoded-se-file",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    wallet_path = Path(args.path_to_secret_exponent_file)
    wait_for_usb_mount(wallet_path.parent)
    if wallet_path.exists():
        parser = hsms.cmds.hsms.create_parser()
        args = parser.parse_args([str(wallet_path)])
        hsms.cmds.hsms.hsms(args, parser)
    else:
        generate_secret(wallet_path)
    print()
    input("hit return to power off> ")
    os.system("poweroff")


if __name__ == "__main__":
    main()
