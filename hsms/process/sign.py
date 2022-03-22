from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from hsms.atoms.hexbytes import hexbytes
from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent
from hsms.streamables import bytes32, CoinSpend, Program
from hsms.puzzles.conlang import AGG_SIG_ME, AGG_SIG_UNSAFE
from hsms.util.conditions import conditions_by_opcode

from .signing_hints import SumHint, SumHints, PathHint, PathHints
from .unsigned_spend import SignatureInfo, UnsignedSpend


def conditions_for_coin_spend(coin_spend: CoinSpend) -> Program:
    return coin_spend.puzzle_reveal.run(coin_spend.solution)


def build_sum_hints_lookup(sum_hints: List[SumHint]) -> SumHints:
    return {_.final_public_key(): _ for _ in sum_hints}


def build_path_hints_lookup(path_hints: List[PathHint]) -> PathHints:
    return {_.public_key(): _ for _ in path_hints}


def sign(us: UnsignedSpend, secrets: List[BLSSecretExponent]) -> List[SignatureInfo]:
    sigs = []
    sum_hints = build_sum_hints_lookup(us.sum_hints)
    path_hints = build_path_hints_lookup(us.path_hints)
    for coin_spend in us.coin_spends:
        more_sigs = sign_for_coin_spend(
            coin_spend, secrets, sum_hints, path_hints, us.agg_sig_me_network_suffix
        )
        sigs.extend(more_sigs)
    return sigs


def sign_for_coin_spend(
    coin_spend: CoinSpend,
    secrets: List[BLSSecretExponent],
    sum_hints: SumHints,
    path_hints: PathHints,
    agg_sig_me_network_suffix: bytes,
) -> List[SignatureInfo]:
    conditions = conditions_for_coin_spend(coin_spend)
    agg_sig_me_message_suffix = coin_spend.coin.name() + agg_sig_me_network_suffix
    sigs = []
    for signature_metadata in partial_signature_metadata_for_hsm(
        conditions, sum_hints, path_hints, agg_sig_me_message_suffix
    ):
        partial_public_key = signature_metadata.partial_public_key
        final_public_key = signature_metadata.final_public_key
        message = signature_metadata.message
        path_hint = path_hints.get(partial_public_key, (partial_public_key, []))
        secret_key = secret_key_for_public_key(
            secrets, path_hint.path, path_hint.root_public_key, partial_public_key
        )
        if secret_key is None:
            continue
        sig_info = SignatureInfo(
            secret_key.sign(message, final_public_key),
            partial_public_key,
            final_public_key,
            message,
        )

        sigs.append(sig_info)
    return sigs


def generate_synthetic_offset_signatures(us: UnsignedSpend) -> List[SignatureInfo]:
    sig_infos = []
    sum_hints = build_sum_hints_lookup(us.sum_hints)
    for coin_spend in us.coin_spends:
        for final_public_key, message in generate_verify_pairs(
            coin_spend, us.agg_sig_me_network_suffix
        ):
            sum_hints = sum_hints.get(final_public_key, [final_public_key])

            secret_key = sum_hints.synthetic_offset
            partial_public_key = secret_key.public_key()
            signature = secret_key.sign(message, final_public_key)
            if final_public_key == partial_public_key:
                assert signature.verify([(partial_public_key, message)])
            sig_info = SignatureInfo(
                signature, partial_public_key, final_public_key, message
            )
            sig_infos.append(sig_info)
    return sig_infos


def generate_verify_pairs(
    coin_spend: CoinSpend, agg_sig_me_network_suffix
) -> Iterable[Tuple[BLSPublicKey, bytes]]:
    agg_sig_me_message_suffix = coin_spend.coin.name() + agg_sig_me_network_suffix
    conditions = conditions_for_coin_spend(coin_spend)
    yield from verify_pairs_for_conditions(conditions, agg_sig_me_message_suffix)


def verify_pairs_for_conditions(
    conditions: Program, agg_sig_me_message_suffix: bytes
) -> Iterable[Tuple[BLSPublicKey, bytes]]:
    d = conditions_by_opcode(conditions)

    agg_sig_me_conditions = d.get(AGG_SIG_ME, [])
    for condition in agg_sig_me_conditions:
        condition = list(condition.as_atom_list())
        yield BLSPublicKey.from_bytes(condition[1]), hexbytes(
            condition[2] + agg_sig_me_message_suffix
        )

    agg_sig_unsafe_conditions = d.get(AGG_SIG_UNSAFE, [])
    for condition in agg_sig_unsafe_conditions:
        condition = list(condition.as_atom_list())
        yield BLSPublicKey.from_bytes(condition[1]), condition[2]


@dataclass
class SignatureMetadata:
    partial_public_key: BLSPublicKey
    final_public_key: BLSPublicKey
    message: bytes


def secret_key_for_public_key(
    secrets: List[BLSSecretExponent], path, root_public_key, public_key
) -> Optional[BLSSecretExponent]:
    for secret in secrets:
        if secret.public_key() == root_public_key:
            s = secret.child_for_path(path)
            if s.public_key() == public_key:
                return s
    return None


def partial_signature_metadata_for_hsm(
    conditions: Program,
    sum_hints: SumHints,
    path_hints: PathHints,
    agg_sig_me_network_suffix: bytes32,
) -> Iterable[SignatureMetadata]:
    for final_public_key, message in verify_pairs_for_conditions(
        conditions, agg_sig_me_network_suffix
    ):
        sum_hints = sum_hints.get(final_public_key, [final_public_key])

        for partial_public_key in sum_hints.public_keys:
            metadata = SignatureMetadata(partial_public_key, final_public_key, message)
            yield metadata


def partial_signatures_offsets(
    conditions: Program,
    sum_hints: SumHints,
    path_hints: PathHints,
    agg_sig_me_network_suffix: bytes32,
) -> Iterable[Tuple[SignatureMetadata, BLSSecretExponent]]:
    for final_public_key, message in verify_pairs_for_conditions(
        conditions, agg_sig_me_network_suffix
    ):
        sum_hints = sum_hints.get(final_public_key, [final_public_key])

        partial_public_key = sum_hints.synthetic_offset.public_key()
        metadata = SignatureMetadata(partial_public_key, final_public_key, message)
        yield metadata, sum_hints.synthetic_offset
