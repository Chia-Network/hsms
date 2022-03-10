from clvm.EvalError import EvalError
from clvm.casts import int_from_bytes

from streamables import BLSSignature, Coin, Program

from .Conditions import conditions_by_opcode, parse_sexp_to_conditions, ConditionOpcode


def conditions_for_solution(solution_program):
    # get the standard script for a puzzle hash and feed in the solution
    args = Program.to(solution_program)
    try:
        puzzle_sexp = args.first()
        solution_sexp = args.rest()
        r = puzzle_sexp.run(solution_sexp)
        return parse_sexp_to_conditions(r)
    except EvalError:
        raise


def conditions_dict_for_solution(solution):
    return conditions_by_opcode(conditions_for_solution(solution))


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
        pairs.append(BLSSignature.aggsig_pair(*_[1:]))
    return pairs
