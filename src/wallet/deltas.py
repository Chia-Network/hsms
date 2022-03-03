from chiasim.validation.chainview import name_puzzle_conditions_list
from chiasim.validation.consensus import conditions_dict_for_solution, created_outputs_for_conditions_dict


def additions_for_solution(coin_name, solution):
    return created_outputs_for_conditions_dict(
        conditions_dict_for_solution(solution), coin_name)


def additions_for_body(body):
    yield body.coinbase_coin
    yield body.fees_coin
    for (coin_name, solution, conditions_dict) in name_puzzle_conditions_list(body.solution_program):
        for _ in created_outputs_for_conditions_dict(conditions_dict, coin_name):
            yield _


def removals_for_body(body):
    return [
        coin_name for (coin_name, solution, conditions_dict) in
        name_puzzle_conditions_list(body.solution_program)]
