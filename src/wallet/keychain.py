from chiasim.hashable import BLSSignature
from chiasim.validation.Conditions import conditions_by_opcode
from chiasim.validation.consensus import (
    conditions_for_solution,
    hash_key_pairs_for_conditions_dict,
)
from chiasim.wallet.BLSPrivateKey import BLSPrivateKey


class Keychain(dict):
    @classmethod
    def __new__(cls, *args):
        return dict.__new__(*args)

    def add_secret_exponents(self, secret_exponents):
        for _ in secret_exponents:
            bls_private_key = BLSPrivateKey.from_secret_exponent(_)
            self[bls_private_key.public_key()] = bls_private_key

    def sign(self, aggsig_pair):
        bls_private_key = self.get(aggsig_pair.public_key)
        if not bls_private_key:
            raise ValueError("unknown pubkey %s" % aggsig_pair.public_key)
        return bls_private_key.sign(aggsig_pair.message_hash)

    def signature_for_solution(self, solution):
        signatures = []
        conditions_dict = conditions_by_opcode(conditions_for_solution(solution))
        for _ in hash_key_pairs_for_conditions_dict(conditions_dict):
            signature = self.sign(_)
            signatures.append(signature)
        return BLSSignature.aggregate(signatures)
