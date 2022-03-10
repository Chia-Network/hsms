import enum

from clvm_tools import binutils

from streamables import Program

from .ConsensusError import ConsensusError, Err


class ConditionOpcode(bytes, enum.Enum):
    AGG_SIG = bytes([50])
    CREATE_COIN = bytes([51])
    ASSERT_COIN_CONSUMED = bytes([52])
    ASSERT_MY_COIN_ID = bytes([53])
    ASSERT_TIME_EXCEEDS = bytes([54])
    ASSERT_BLOCK_INDEX_EXCEEDS = bytes([55])
    ASSERT_BLOCK_AGE_EXCEEDS = bytes([56])


def parse_sexp_to_condition(sexp):
    assert sexp.listp()
    items = sexp.as_python()
    if not isinstance(items[0], bytes):
        raise ConsensusError(Err.INVALID_CONDITION, items)
    assert isinstance(items[0], bytes)
    opcode = items[0]
    try:
        opcode = ConditionOpcode(items[0])
    except ValueError:
        pass
    return [opcode] + items[1:]


def parse_sexp_to_conditions(sexp):
    return [parse_sexp_to_condition(_) for _ in sexp.as_iter()]


def make_create_coin_condition(puzzle_hash, amount):
    return [ConditionOpcode.CREATE_COIN, puzzle_hash, amount]


def make_assert_coin_consumed_condition(coin_name):
    return [ConditionOpcode.ASSERT_COIN_CONSUMED, coin_name]


def make_assert_my_coin_id_condition(coin_name):
    return [ConditionOpcode.ASSERT_MY_COIN_ID, coin_name]


def make_assert_min_time_condition(time):
    return [ConditionOpcode.ASSERT_MIN_TIME, time]


def make_assert_block_index_exceeds_condition(block_index):
    return [ConditionOpcode.ASSERT_BLOCK_INDEX_EXCEEDS, block_index]


def make_assert_block_age_exceeds_condition(block_index):
    return [ConditionOpcode.ASSERT_BLOCK_AGE_EXCEEDS, block_index]


def make_assert_time_exceeds_condition(time):
    return [ConditionOpcode.ASSERT_TIME_EXCEEDS, time]


def conditions_by_opcode(conditions):
    opcodes = sorted(set([_[0] for _ in conditions if len(_) > 0]))
    d = {}
    for _ in opcodes:
        d[_] = list()
    for _ in conditions:
        d[_[0]].append(_)
    return d


def parse_sexp_to_conditions_dict(sexp):
    return conditions_by_opcode(parse_sexp_to_conditions(sexp))


def conditions_to_sexp(conditions):
    return Program.to([binutils.assemble("#q"), conditions])
