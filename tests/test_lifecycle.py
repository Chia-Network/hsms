from tests.generate import se_generate, bytes32_generate, uint256_generate

from hsms.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    DEFAULT_HIDDEN_PUZZLE,
    puzzle_for_public_key_and_hidden_puzzle,
    solution_for_conditions,
    calculate_synthetic_offset,
)
from hsms.streamables import Coin, CoinSpend, SpendBundle
from hsms.streamables.key_metadata import KeyMetadata

from hsms.puzzles.conlang import CREATE_COIN

AGG_SIG_ME_ADDITIONAL_DATA = bytes.fromhex(
    "ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"
)


DEFAULT_HIDDEN_PUZZLE_HASH = DEFAULT_HIDDEN_PUZZLE.tree_hash()


def test_lifecycle():
    """
    let's create three `CoinSpend` objects and generate a signing request
    then pass it to the hsms0 tool for signatures
    then reassemble the signatures
    """

    # create two private keys A and B

    se_A = se_generate(100)
    se_B = se_generate(200)

    # create some compound public keys
    # each using a different path from A and B

    A_PATHS = [[1, 5, 10], [2, 3, 1], [1000, 0, 92]]
    B_PATHS = [[1, 5, 10], [23, 33, 13], [200, 11, 9992]]

    pks_A = [se_A.child_for_path(_).public_key() for _ in A_PATHS]
    pks_B = [se_B.child_for_path(_).public_key() for _ in B_PATHS]

    sum_pks = [a + b for a, b in zip(pks_A, pks_B)]
    puzzles = [
        puzzle_for_public_key_and_hidden_puzzle(pk, DEFAULT_HIDDEN_PUZZLE)
        for pk in sum_pks
    ]
    synthetic_se_list = [
        calculate_synthetic_offset(pk, DEFAULT_HIDDEN_PUZZLE_HASH) for pk in sum_pks
    ]

    COIN_MAX = 1000000

    coins = [
        Coin(
            bytes32_generate(idx),
            puzzle.tree_hash(),
            5 + (uint256_generate(idx) % COIN_MAX),
        )
        for idx, puzzle in enumerate(puzzles)
    ]

    # these are nonsense puzzle hashes, but that's okay
    dest_puzzle_hashes = [
        bytes32_generate(idx, "dest") for idx, _ in enumerate(puzzles)
    ]

    conditions_for_spends = [
        [[CREATE_COIN, dph, coin.amount]]
        for dph, coin in zip(dest_puzzle_hashes, coins)
    ]
    solutions = [
        solution_for_conditions(conditions) for conditions in conditions_for_spends
    ]
    coin_spends = [CoinSpend(*triple) for triple in zip(coins, puzzles, solutions)]

    # now create a signing request
    # let each of A and B sign their part
    # then reconstruct using the signing request + the signatures
    # and generate a `SpendBundle`

    sums_hints = {
        a_pk + b_pk + synthetic_se.public_key(): [a_pk, b_pk, synthetic_se]
        for a_pk, b_pk, synthetic_se in zip(pks_A, pks_B, synthetic_se_list)
    }

    pk_A = se_A.public_key()
    path_hints_a = {pk: (pk_A, path) for pk, path in zip(pks_A, A_PATHS)}
    pk_B = se_B.public_key()
    path_hints_b = {pk: (pk_B, path) for pk, path in zip(pks_B, B_PATHS)}
    path_hints = path_hints_a | path_hints_b

    print(sums_hints)
    print(path_hints)

    from hsms.process.zz import USB

    agg_sig_me_network_suffix = AGG_SIG_ME_ADDITIONAL_DATA
    pst = USB(coin_spends, sums_hints, path_hints, agg_sig_me_network_suffix)

    print("-" * 10)
    signatures_A = pst.sign([se_A])
    print(signatures_A)

    signatures_B = pst.sign([se_B])
    print(signatures_B)

    extra_signatures = pst.sign_extra()
    print(extra_signatures)

    # now let's try adding them all together and creating a `SpendBundle`
    all_signatures = [
        sig_info.signature
        for sig_infos in [signatures_A, signatures_B, extra_signatures]
        for sig_info in sig_infos
    ]
    total_signature = sum(all_signatures, start=all_signatures[0].zero())
    print(total_signature)

    spend_bundle = SpendBundle(coin_spends, total_signature)
    print(bytes(spend_bundle))

    from hsms.util.debug_spend_bundle import debug_spend_bundle

    debug_spend_bundle(spend_bundle)
