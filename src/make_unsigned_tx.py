from blspy import G2Element

import hashlib

import cbor

from hashable import Coin, CoinSolution, Program, SpendBundle
from multisig.pst import PartiallySignedTransaction, transform_pst


PAY_TO_AGGSIG_ME_HEX = "ff01ffff32ffb0a272e9d1d50a4aea7d8f0583948090d0888be5777f2846800b8281139cd4aa9eee05f89b069857a3e77ccfaae1615f9cffa04bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a8080"

PAY_TO_AGGSIG_ME = Program.from_bytes(bytes.fromhex(PAY_TO_AGGSIG_ME_HEX))


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


spend_bundle = make_spend_bundle()
print(spend_bundle)

print(bytes(spend_bundle).hex())

d = PartiallySignedTransaction(
    coin_solutions=list(spend_bundle.coin_solutions),
    sigs=[],
    delegated_solution=Program.to(0),
    hd_hints=[],
)

breakpoint()
t = bytes(d)
print()
print(t.hex())
