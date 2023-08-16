import sys

from chia_base.bls12_381 import BLSSecretExponent


def main(argv=sys.argv[1:]):
    for arg in argv:
        secret_exponent = BLSSecretExponent.from_bech32m(arg)
        print(secret_exponent.public_key().as_bech32m())


if __name__ == "__main__":
    main()
