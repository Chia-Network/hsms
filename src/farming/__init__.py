import blspy

from clvm_tools import binutils

from chiasim.atoms import uint64
from chiasim.hashable import (
    BLSSignature, Body, Coin, EORPrivateKey, Header, HeaderHash,
    Program, ProgramHash, ProofOfSpace, PublicKey, Signature,
    SpendBundle, std_hash
)
from chiasim.validation import validate_spend_bundle_signature


PLOT_PRIVATE_KEY = EORPrivateKey(blspy.Util.hash256(bytes([4])))
PLOT_PUBLIC_KEY = PLOT_PRIVATE_KEY.public_key()


def get_plot_public_key() -> PublicKey:
    # TODO: make this configurable
    return PLOT_PUBLIC_KEY


def sign_header(header: Header, public_key: PublicKey):
    if public_key != PLOT_PUBLIC_KEY:
        raise ValueError("unknown public key")
    message_hash = blspy.Util.hash256(bytes(header))
    return PLOT_PRIVATE_KEY.sign(message_hash)


def best_solution_program(bundle: SpendBundle):
    """
    This could potentially do a lot of clever and complicated compression
    optimizations in conjunction with choosing the set of SpendBundles to include.

    For now, we just quote the solutions we know.
    """
    r = []
    for coin_solution in bundle.coin_solutions:
        entry = [coin_solution.coin.name(), coin_solution.solution]
        r.append(entry)
    return Program.to([binutils.assemble("#q"), r])


def collect_best_bundle(known_bundles) -> SpendBundle:
    # this is way too simple
    spend_bundle = SpendBundle.aggregate(known_bundles)
    assert spend_bundle.fees() >= 0
    return spend_bundle


def farm_new_block(
        previous_header: HeaderHash, previous_signature: Signature,
        block_index: int, proof_of_space: ProofOfSpace,
        spend_bundle: SpendBundle, coinbase_coin: Coin,
        coinbase_signature: BLSSignature, fees_puzzle_hash: ProgramHash,
        timestamp: uint64):
    """
    Steps:
        - collect up a consistent set of removals and solutions
        - run solutions to get the additions
        - select a timestamp = max(now, minimum_legal_timestamp)
        - create blank extension data
        - collect up coinbase coin with coinbase signature (if solo mining, we get these locally)
        - return Header, Body
    """

    program_cost = 0

    assert validate_spend_bundle_signature(spend_bundle)
    solution_program = best_solution_program(spend_bundle)
    extension_data = std_hash(b'')

    block_index_hash = block_index.to_bytes(32, "big")
    fees_coin = Coin(block_index_hash, fees_puzzle_hash, spend_bundle.fees())
    body = Body(
        coinbase_signature, coinbase_coin, fees_coin,
        solution_program, program_cost, spend_bundle.aggregated_signature)

    header = Header(previous_header, previous_signature, timestamp, proof_of_space, body, extension_data)
    return header, body
