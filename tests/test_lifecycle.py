from tests.generate import se_generate, bytes32_generate, uint256_generate

from hsms.debug.debug_spend_bundle import debug_spend_bundle
from hsms.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    DEFAULT_HIDDEN_PUZZLE,
    puzzle_for_public_key_and_hidden_puzzle,
    solution_for_conditions,
    calculate_synthetic_offset,
)
from hsms.streamables import bytes96, Coin, CoinSpend, SpendBundle
from hsms.process.sign import sign, generate_synthetic_offset_signatures
from hsms.process.signing_hints import SumHint, PathHint
from hsms.process.unsigned_spend import UnsignedSpend
from hsms.puzzles.conlang import CREATE_COIN
from hsms.util.byte_chunks import ChunkAssembler, create_chunks_for_blob


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

    # create "sum public keys" that are the sum of pubkeys from each of A and B
    sum_pks = [a + b for a, b in zip(pks_A, pks_B)]

    # create a standard puzzle using the sum public keys
    puzzles = [
        puzzle_for_public_key_and_hidden_puzzle(pk, DEFAULT_HIDDEN_PUZZLE)
        for pk in sum_pks
    ]

    # work out the synthetic private keys as we'll need it later to finish the signing
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

    # the destination puzzle hashes are nonsense, but that's okay
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

    # create the "sum hints" which give information on how the public keys that
    # appear in the `AGG_SIG_ME` conditions were constructed

    sum_hints = [
        SumHint([a_pk, b_pk], synthetic_se)
        for a_pk, b_pk, synthetic_se in zip(pks_A, pks_B, synthetic_se_list)
    ]

    # create the "path hints" which give information on how to get from the
    # root public key to the public keys used as inputs to the sum keys
    #
    # If the public key is also the root public key, you don't need this hint

    pk_A = se_A.public_key()
    path_hints_a = [PathHint(pk_A, path) for pk, path in zip(pks_A, A_PATHS)]
    pk_B = se_B.public_key()
    path_hints_b = [PathHint(pk_B, path) for pk, path in zip(pks_B, B_PATHS)]

    path_hints = path_hints_a + path_hints_b

    print(sum_hints)
    print(path_hints)

    unsigned_spend = UnsignedSpend(
        coin_spends, sum_hints, path_hints, AGG_SIG_ME_ADDITIONAL_DATA
    )

    assert unsigned_spend == UnsignedSpend.from_chunks(unsigned_spend.chunk(500))

    spend_chunks = create_chunks_for_blob(bytes(unsigned_spend), 250)
    assembler = ChunkAssembler()
    assembler.add_chunk(spend_chunks[0])
    assembler.add_chunk(spend_chunks[0])
    assert assembler.status() == (1, len(spend_chunks))
    assert not assembler.is_assembled()
    for i in range(1, len(spend_chunks)):
        assembler.add_chunk(spend_chunks[i])
    assert assembler.is_assembled()
    assert assembler.status() == (len(spend_chunks), len(spend_chunks))
    assert unsigned_spend == UnsignedSpend.from_bytes(assembler.assemble())

    print("-" * 10)

    # this simulates giving the `UnsignedSpend` to A and getting signatures back

    signatures_A = sign(unsigned_spend, [se_A])
    print(signatures_A)

    # this simulates giving the `UnsignedSpend` to B and getting signatures back

    signatures_B = sign(unsigned_spend, [se_B])
    print(signatures_B)

    signatures = signatures_A + signatures_B
    spend_bundle = create_spend_bundle(unsigned_spend, signatures)
    print(bytes(spend_bundle))

    validates = debug_spend_bundle(spend_bundle)
    assert validates is True


def create_spend_bundle(unsigned_spend, signatures):
    extra_signatures = generate_synthetic_offset_signatures(unsigned_spend)

    # now let's try adding them all together and creating a `SpendBundle`

    all_signatures = [sig_info.signature for sig_info in signatures + extra_signatures]
    total_signature = sum(all_signatures, start=all_signatures[0].zero())

    return SpendBundle(unsigned_spend.coin_spends, bytes96(total_signature))
