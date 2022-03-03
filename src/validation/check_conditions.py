from clvm.casts import int_from_bytes

from .Conditions import ConditionOpcode
from .ConsensusError import ConsensusError, Err


def assert_coin_consumed(condition, coin, context):
    for coin_name in condition[1:]:
        if coin_name not in context["removals"]:
            raise ConsensusError(Err.ASSERT_COIN_CONSUMED_FAILED, (coin, coin_name))


def assert_my_coin_id(condition, coin, context):
    if coin.name() != condition[1]:
        raise ConsensusError(Err.ASSERT_MY_COIN_ID_FAILED, (coin, condition))


def assert_block_index_exceeds(condition, coin, context):
    try:
        expected_block_index = int_from_bytes(condition[1])
    except ValueError:
        raise ConsensusError(Err.INVALID_CONDITION, (coin, condition))
    if context["block_index"] <= expected_block_index:
        raise ConsensusError(
            Err.ASSERT_BLOCK_INDEX_EXCEEDS_FAILED, (coin, condition))


def assert_block_age_exceeds(condition, coin, context):
    try:
        unspent = context["coin_to_unspent"][coin.name()]
        expected_block_age = int_from_bytes(condition[1])
        expected_block_index = expected_block_age + unspent.confirmed_block_index
    except ValueError:
        raise ConsensusError(Err.INVALID_CONDITION, (coin, condition))
    if context["block_index"] <= expected_block_index:
        raise ConsensusError(
            Err.ASSERT_BLOCK_AGE_EXCEEDS_FAILED, (coin, condition))


def assert_time_exceeds(condition, coin, context):
    min_time = int_from_bytes(condition[1])
    if context['creation_time'] <= min_time:
        raise ConsensusError(
            Err.ASSERT_TIME_EXCEEDS_FAILED, (coin, condition))


CONDITION_CHECKER_LOOKUP = {
    ConditionOpcode.ASSERT_COIN_CONSUMED: assert_coin_consumed,
    ConditionOpcode.ASSERT_MY_COIN_ID: assert_my_coin_id,
    ConditionOpcode.ASSERT_BLOCK_INDEX_EXCEEDS: assert_block_index_exceeds,
    ConditionOpcode.ASSERT_BLOCK_AGE_EXCEEDS: assert_block_age_exceeds,
    ConditionOpcode.ASSERT_TIME_EXCEEDS: assert_time_exceeds,
}
