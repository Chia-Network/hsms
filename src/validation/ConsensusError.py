from enum import Enum


class ConsensusError(Exception):
    def __init__(self, code, bad_object):
        self.args = [code, bad_object]
        self.message = str(bad_object)


class Err(Enum):
    # temporary errors. Don't blacklist
    DOES_NOT_EXTEND = -1
    BAD_HEADER_SIGNATURE = -2
    MISSING_FROM_STORAGE = -3

    UNKNOWN = -9999

    # permanent errors. Block is unsalvageable garbage.
    BAD_COINBASE_SIGNATURE = 1
    INVALID_BLOCK_SOLUTION = 2
    INVALID_COIN_SOLUTION = 3
    DUPLICATE_OUTPUT = 4
    DOUBLE_SPEND = 5
    UNKNOWN_UNSPENT = 6
    BAD_AGGREGATE_SIGNATURE = 7
    WRONG_PUZZLE_HASH = 8
    BAD_COINBASE_REWARD = 9
    INVALID_CONDITION = 10
    ASSERT_MY_COIN_ID_FAILED = 11
    ASSERT_COIN_CONSUMED_FAILED = 12
    ASSERT_BLOCK_AGE_EXCEEDS_FAILED = 13
    ASSERT_BLOCK_INDEX_EXCEEDS_FAILED = 14
    COIN_AMOUNT_EXCEEDS_MAXIMUM = 15
    ASSERT_TIME_EXCEEDS_FAILED = 16
