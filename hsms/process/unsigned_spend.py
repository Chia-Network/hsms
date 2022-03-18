from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Union, Tuple

from hsms.atoms.hexbytes import hexbytes
from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent, BLSSignature
from hsms.streamables import bytes32, CoinSpend
from hsms.validation.Conditions import conditions_by_opcode
from hsms.puzzles.conlang import AGG_SIG_ME, AGG_SIG_UNSAFE


@dataclass
class SignatureInfo:
    signature: BLSSignature
    partial_public_key: BLSPublicKey
    final_public_key: BLSPublicKey
    message: bytes


@dataclass
class UnsignedSpend:
    coin_spends: List[CoinSpend]
    sums_hints: Dict[BLSPublicKey, List[Union[BLSPublicKey, BLSSecretExponent]]]
    path_hints: Dict[BLSPublicKey, Tuple[BLSPublicKey, List[int]]]
    agg_sig_me_network_suffix: bytes32

    def sign(self, secrets: List[BLSSecretExponent]) -> List[SignatureInfo]:
        sigs = []
        for coin_spend in self.coin_spends:
            more_sigs = self.sign_for_coin_spend(coin_spend, secrets)
            sigs.extend(more_sigs)
        return sigs

    def sign_for_coin_spend(self, coin_spend, secrets) -> List[SignatureInfo]:
        sigs = []
        for public_key, message in generate_verify_pairs(
            coin_spend, self.agg_sig_me_network_suffix
        ):
            more_sigs = self.sign_for_public_key_and_message(
                public_key, message, secrets
            )
            sigs.extend(more_sigs)
        return sigs

    def sign_for_public_key_and_message(
        self, final_public_key, message, secrets
    ) -> List[SignatureInfo]:
        sum_hints = self.sums_hints.get(final_public_key, [final_public_key])

        sig_infos = []

        for pk_or_se in sum_hints:
            if isinstance(pk_or_se, BLSSecretExponent):
                continue
            partial_public_key = pk_or_se
            root_public_key, path = self.path_hints.get(
                partial_public_key, (partial_public_key, [])
            )

            secret_key = secret_key_for_public_key(
                secrets, path, root_public_key, partial_public_key
            )
            if secret_key is None:
                continue

            signature = secret_key.sign(message, final_public_key)
            if final_public_key == root_public_key:
                assert signature.verify([(partial_public_key, message)])
            sig_info = SignatureInfo(
                signature, partial_public_key, final_public_key, message
            )
            sig_infos.append(sig_info)
        return sig_infos

    def sign_extra(self) -> List[SignatureInfo]:
        sig_infos = []
        for coin_spend in self.coin_spends:
            for final_public_key, message in generate_verify_pairs(
                coin_spend, self.agg_sig_me_network_suffix
            ):
                sum_hints = self.sums_hints.get(final_public_key, [final_public_key])

                for secret_key in sum_hints:
                    if isinstance(secret_key, BLSSecretExponent):
                        partial_public_key = secret_key.public_key()
                        signature = secret_key.sign(message, final_public_key)
                        if final_public_key == partial_public_key:
                            assert signature.verify([(partial_public_key, message)])
                        sig_info = SignatureInfo(
                            signature, partial_public_key, final_public_key, message
                        )
                        sig_infos.append(sig_info)
        return sig_infos


def secret_key_for_public_key(
    secrets, path, root_public_key, public_key
) -> Optional[BLSSecretExponent]:
    for secret in secrets:
        if secret.public_key() == root_public_key:
            s = secret.child_for_path(path)
            if s.public_key() == public_key:
                return s
    return None


def as_atom_list(obj) -> Iterable[hexbytes]:
    """
    Pretend `self` is a list of atoms. Return the corresponding
    python list of atoms.

    At each step, we always assume a node to be an atom or a pair.
    If the assumption is wrong, we exit early. This way we never fail
    and always return SOMETHING.
    """
    while obj.pair:
        first, obj = obj.pair
        atom = first.atom
        if atom is None:
            break
        yield hexbytes(atom)


def generate_verify_pairs(
    coin_spend, agg_sig_me_network_suffix
) -> Iterable[Tuple[BLSPublicKey, bytes]]:
    agg_sig_me_message_suffix = coin_spend.coin.name() + agg_sig_me_network_suffix
    conditions = coin_spend.puzzle_reveal.run(coin_spend.solution)
    d = conditions_by_opcode(conditions)

    agg_sig_me_conditions = d.get(AGG_SIG_ME, [])
    for condition in agg_sig_me_conditions:
        condition = list(as_atom_list(condition))
        yield BLSPublicKey.from_bytes(condition[1]), hexbytes(
            condition[2] + agg_sig_me_message_suffix
        )

    agg_sig_unsafe_conditions = d.get(AGG_SIG_UNSAFE, [])
    for condition in agg_sig_unsafe_conditions:
        condition = list(as_atom_list(condition))
        yield BLSPublicKey.from_bytes(condition[1]), condition[2]
