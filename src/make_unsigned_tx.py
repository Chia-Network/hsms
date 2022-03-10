from blspy import G2Element

import hashlib

from atoms.hexbytes import hexbytes
from hashable import Coin, CoinSolution, Program, SpendBundle
from multisig.pst import PartiallySignedTransaction

from clvm_tools.binutils import assemble


PAY_TO_AGGSIG_ME_PROG = """(q (50
     0x8ba79a9ccd362086d552a6f56da7fe612959b0dd372350ad798c77c2170de2163a00e499928cc40547a7a8a5e2cde6be
     0x4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a))"""

PAY_TO_AGGSIG_ME = Program.to(assemble(PAY_TO_AGGSIG_ME_PROG))


def make_coin():
    parent_id = hashlib.sha256(bytes([1] * 32)).digest()
    puzzle_hash = PAY_TO_AGGSIG_ME.tree_hash()
    coin = Coin(parent_id, puzzle_hash, 10000)
    return coin


def make_spend_bundle():
    coin = make_coin()
    solution_pair = Program.to((PAY_TO_AGGSIG_ME, 0))
    coin_spend = CoinSolution(coin, solution_pair)
    spend_bundle = SpendBundle([coin_spend], G2Element())
    return spend_bundle


def main():
    spend_bundle = make_spend_bundle()
    print(spend_bundle)

    print(bytes(spend_bundle).hex())

    d = PartiallySignedTransaction(
        coin_solutions=list(spend_bundle.coin_solutions),
        sigs=[],
        delegated_solution=Program.to(0),
        hd_hints={
            bytes.fromhex("c34eb867"): {
                "hd_fingerprint": bytes.fromhex("0b92dcdd"),
                "index": 0,
            }
        },
    )

    t = bytes(d)
    print()
    print(t.hex())


def round_trip():
    spend_bundle = make_spend_bundle()
    d = PartiallySignedTransaction(
        coin_solutions=spend_bundle.coin_solutions,
        sigs=[],
        delegated_solution=Program.to(0),
        hd_hints={
            bytes(b"c34eb867"): {
                "hd_fingerprint": bytes.fromhex("0b92dcdd"),
                "index": 0,
            }
        },
    )

    b = hexbytes(d)
    breakpoint()
    d1 = PartiallySignedTransaction.from_bytes(b)
    b1 = hexbytes(d1)
    print(b)
    print(b1)

    assert b == b1


round_trip()
