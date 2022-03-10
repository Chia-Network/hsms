from clvm.EvalError import EvalError
from clvm.casts import int_from_bytes

from bls12_381 import BLSPublicKey, BLSSignature
from streamables import bytes32, Coin, CoinSpend

from .Conditions import conditions_by_opcode, parse_sexp_to_conditions, ConditionOpcode


def conditions_for_coin_spend(coin_spend: CoinSpend):
    try:
        r = coin_spend.puzzle_reveal.run(coin_spend.solution)
        return parse_sexp_to_conditions(r)
    except EvalError:
        raise


def conditions_dict_for_coin_spend(coin_spend: CoinSpend):
    return conditions_by_opcode(conditions_for_coin_spend(coin_spend))


def created_outputs_for_conditions_dict(conditions_dict, input_coin_name):
    output_coins = []
    for _ in conditions_dict.get(ConditionOpcode.CREATE_COIN, []):
        # TODO: check condition very carefully
        # (ensure there are the correct number and type of parameters)
        # maybe write a type-checking framework for conditions
        # and don't just fail with asserts
        assert len(_) == 3
        opcode, puzzle_hash, amount_bin = _
        amount = int_from_bytes(amount_bin)
        coin = Coin(input_coin_name, puzzle_hash, amount)
        output_coins.append(coin)
    return output_coins


def hash_key_pairs_for_conditions_dict(conditions_dict):
    pairs = []
    for _ in conditions_dict.get(ConditionOpcode.AGG_SIG, []):
        # TODO: check types
        assert len(_) == 3
        pair = BLSSignature.aggsig_pair(BLSPublicKey.from_bytes(_[1]), bytes32(_[2]))
        pairs.append(pair)
    return pairs
