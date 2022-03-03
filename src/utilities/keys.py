from chiasim.hashable import BLSSignature, CoinSolution, ProgramHash, SpendBundle
from chiasim.puzzles import p2_delegated_puzzle
from chiasim.validation.consensus import conditions_for_solution, hash_key_pairs_for_conditions_dict
from chiasim.validation.Conditions import conditions_by_opcode, make_create_coin_condition
from chiasim.wallet.keychain import Keychain

from .BLSHDKey import BLSPrivateHDKey

from puzzles import p2_delegated_puzzle


HIERARCHICAL_PRIVATE_KEY = BLSPrivateHDKey.from_seed(b"foo")


def private_key_for_index(index):
    return HIERARCHICAL_PRIVATE_KEY.private_child(index).get_private_key()


def secret_exponent_for_index(index):
    return HIERARCHICAL_PRIVATE_KEY.secret_exponent_for_child(index)


def public_key_bytes_for_index(index):
    return HIERARCHICAL_PRIVATE_KEY.public_child(index)


def puzzle_program_for_index(index):
    return p2_delegated_puzzle.puzzle_for_pk(public_key_bytes_for_index(index))


def puzzle_hash_for_index(index):
    return ProgramHash(puzzle_program_for_index(index))


def conditions_for_payment(puzzle_hash_amount_pairs):
    conditions = [make_create_coin_condition(ph, amount) for ph, amount in puzzle_hash_amount_pairs]
    return conditions


def sign_f_for_keychain(keychain):
    def sign_f(aggsig_pair):
        bls_private_key = keychain.get(aggsig_pair.public_key)
        if bls_private_key:
            return bls_private_key.sign(aggsig_pair.message_hash)
        raise ValueError("unknown pubkey %s" % aggsig_pair.public_key)
    return sign_f


def signature_for_solution(solution, sign_f):
    signatures = []
    conditions_dict = conditions_by_opcode(conditions_for_solution(solution))
    for _ in hash_key_pairs_for_conditions_dict(conditions_dict):
        signature = sign_f(_)
        signatures.append(signature)
    return BLSSignature.aggregate(signatures)


def make_default_keychain():
    keychain = Keychain()
    secret_exponents = [secret_exponent_for_index(_) for _ in range(10)]
    keychain.add_secret_exponents(secret_exponents)
    return keychain


DEFAULT_KEYCHAIN = make_default_keychain()


def build_spend_bundle(coin, solution, keychain=DEFAULT_KEYCHAIN):
    coin_solution = CoinSolution(coin, solution)
    signature = keychain.signature_for_solution(solution)
    return SpendBundle([coin_solution], signature)


def spend_coin(coin, conditions, index, keychain=DEFAULT_KEYCHAIN):
    solution = p2_delegated_puzzle.solution_for_conditions(
        puzzle_program_for_index(index), conditions
    )
    return build_spend_bundle(coin, solution, keychain)


"""
Copyright 2018 Chia Network Inc
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
