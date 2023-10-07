from dataclasses import dataclass, field

import random

from chia_base.bls12_381 import BLSPublicKey, BLSSecretExponent
from chia_base.core import Coin, CoinSpend

from clvm_rs import Program

from hsms.process.signing_hints import (
    SumHint as LegacySH,
    PathHint as LegacyPH,
)
from hsms.util.clvm_serde import (
    to_program_for_type,
    from_program_for_type,
    PairTuple,
)


def test_ser():
    tpb = to_program_for_type(bytes)
    fpb = from_program_for_type(bytes)
    tps = to_program_for_type(str)
    fps = from_program_for_type(str)
    for s in ["", "foo", "1" * 1000]:
        p = tps(s)
        assert p == Program.to(s)
        assert fps(p) == s

        b = s.encode()
        p = tpb(b)
        assert p == Program.to(b)
        assert fpb(p) == b

    tt = tuple[str, bytes, int]
    tp = to_program_for_type(tt)
    fp = from_program_for_type(tt)
    for t in [
        ("foo", b"bar", 100),
        ("this is a test", bytes([5, 6, 7]), -94817),
    ]:
        assert tp(t) == Program.to(list(t))

    tt = list[tuple[int, str]]
    tp = to_program_for_type(tt)
    fp = from_program_for_type(tt)
    for t in [
        [(100, "hundred"), (200, "two hundred"), (30, "thirty")],
    ]:
        rhs = list(list(_) for _ in t)
        prhs = Program.to(rhs)
        assert tp(t) == prhs
        assert fp(tp(t)) == t

    tt = PairTuple[int, str]
    tp = to_program_for_type(tt)
    fp = from_program_for_type(tt)
    for v in [
        (100, "hundred"),
        (200, "two hundred"),
        (30, "thirty"),
    ]:
        t = PairTuple(*v)
        rhs = Program.to(t)
        assert tp(t) == rhs
        assert fp(tp(t)) == t

    @dataclass
    class Foo:
        a: int
        b: str

    tp = to_program_for_type(Foo)
    foo = Foo(100, "boss")
    rhs = Program.to([100, "boss"])
    assert tp(foo) == rhs
    fp = from_program_for_type(Foo)
    assert foo == fp(rhs)

    @dataclass
    class Nested:
        a: list[Foo]
        b: int

    tp = to_program_for_type(Nested)
    nested = Nested([foo, Foo(200, "worker")], 5000)
    rhs = Program.to([[[100, "boss"], [200, "worker"]], 5000])
    assert tp(nested) == rhs
    fp = from_program_for_type(Nested)
    assert nested == fp(tp(nested))

    @dataclass
    class Foo:
        a: int
        b: str = field(default="foo", metadata=dict(key="bob"))

    tp = to_program_for_type(Foo)
    foo = Foo(100, "boss")
    rhs = Program.to([100, ("bob", "boss")])
    assert tp(foo) == rhs
    fp = from_program_for_type(Foo)
    assert foo == fp(rhs)

    @dataclass
    class Foo:
        a: int = field(metadata=dict(key="a"))
        b: str = field(default="foo", metadata=dict(key="bob"))

    tp = to_program_for_type(Foo)
    fp = from_program_for_type(Foo)
    p = Program.to([("a", 1000), ("bob", "hello")])
    foo = fp(p)
    assert foo.a == 1000
    assert foo.b == "hello"
    p1 = tp(foo)
    assert p1 == p

    for foo in [Foo(20, "foo"), Foo(999, "bar"), Foo(-294, "baz")]:
        p = tp(foo)
        f1 = fp(p)
        assert f1 == foo


def rnd_coin_spend(seed: int) -> CoinSpend:
    r = random.Random(seed)
    parent = r.randbytes(32)
    puzzle = Program.to(f"puz: {r.randbytes(5).hex()}")
    amount = r.randint(1, 1000) * int(1e3)
    solution = Program.to(f"sol: {r.randbytes(10).hex()}")
    coin = Coin(parent, puzzle.tree_hash(), amount)
    return CoinSpend(coin, puzzle, solution)


SumHint = PairTuple[list[BLSPublicKey], BLSSecretExponent]


def test_interop_sum_hint():
    pks = [BLSSecretExponent.from_int(_).public_key() for _ in range(5)]
    synthetic_offset = BLSSecretExponent.from_int(3**70 & ((1 << 256) - 1))
    sum_hint = SumHint(pks, synthetic_offset)
    tp = to_program_for_type(SumHint)
    fp = from_program_for_type(SumHint)
    p = tp(sum_hint)
    print(bytes(p).hex())
    lsh = LegacySH.from_program(p)
    print(lsh)
    assert lsh.public_keys == sum_hint[0]
    assert lsh.synthetic_offset == sum_hint[1]
    sh1 = fp(p)
    assert sum_hint == sh1


CoinSpendTuple = tuple[bytes, Program, int, Program]


PathHint = PairTuple[BLSPublicKey, list[int]]


def test_interop_path_hint():
    public_key = BLSSecretExponent.from_int(1).public_key()
    ints = [1, 5, 91, 29484, -99]
    path_hint = PathHint(public_key, ints)
    tp = to_program_for_type(PathHint)
    fp = from_program_for_type(PathHint)
    p = tp(path_hint)
    print(bytes(p).hex())
    lph = LegacyPH.from_program(p)
    print(lph)
    assert lph.root_public_key == path_hint[0]
    assert lph.path == path_hint[1]
    ph1 = fp(p)
    assert path_hint == ph1


def test_interop_coin_spend():
    for _ in range(10):
        cs = rnd_coin_spend(_)
        cst = coin_spend_to_tuple(cs)
        tp = to_program_for_type(CoinSpendTuple)
        fp = from_program_for_type(CoinSpendTuple)
        p = tp(cst)
        print(bytes(p).hex())
        cst1 = fp(p)
        assert cst == cst1


@dataclass
class UnsignedSpend:
    coin_spend_tuples: list[CoinSpendTuple] = field(
        default_factory=list, metadata=dict(key="c")
    )
    sum_hints: list[SumHint] = field(
        default_factory=list,
        metadata=dict(key="s"),
    )
    path_hints: list[PathHint] = field(
        default_factory=list,
        metadata=dict(key="p"),
    )
    agg_sig_me_network_suffix: bytes = field(
        default=b"",
        metadata=dict(key="a"),
    )

    def coin_spends(self):
        return [coin_spend_from_tuple(_) for _ in self.coin_spend_tuples]


def coin_spend_from_tuple(cst: CoinSpendTuple) -> CoinSpend:
    coin = Coin(cst[0], cst[1].tree_hash(), cst[2])
    return CoinSpend(coin, cst[1], cst[3])


def coin_spend_to_tuple(coin_spend: CoinSpend) -> CoinSpendTuple:
    coin = coin_spend.coin
    return (
        coin.parent_coin_info,
        coin_spend.puzzle_reveal,
        coin.amount,
        coin_spend.solution,
    )


def sum_hint_as_tuple(sum_hint: SumHint) -> tuple:
    return tuple(getattr(sum_hint, _) for _ in "public_keys synthetic_offset".split())


def path_hint_as_tuple(path_hint: PathHint) -> tuple:
    return tuple(getattr(path_hint, _) for _ in "root_public_key path".split())


def test_interop_unsigned_spend():
    from hsms.process.unsigned_spend import UnsignedSpend as LegacyUS

    cs_list = [rnd_coin_spend(_) for _ in range(10)]
    cst_list = [coin_spend_to_tuple(_) for _ in cs_list]

    public_keys = [BLSSecretExponent.from_int(_).public_key() for _ in range(5)]
    synthetic_offset = BLSSecretExponent.from_int(3**70 & ((1 << 256) - 1))
    sum_hint = SumHint(public_keys, synthetic_offset)
    lsh = LegacySH(public_keys, synthetic_offset)
    pubkey = BLSSecretExponent.from_int(9).public_key()
    ints = [2, 5, 17]
    path_hint = PathHint(pubkey, ints)
    lph = LegacyPH(pubkey, ints)

    suffix = b"a" * 32
    us = UnsignedSpend(cst_list[0:3], [sum_hint], [path_hint], suffix)

    lus = LegacyUS(cs_list[0:3], [lsh], [lph], suffix)
    print(bytes(lus.as_program()).hex())
    tp = to_program_for_type(UnsignedSpend)
    fp = from_program_for_type(UnsignedSpend)
    p = tp(us)
    print(bytes(p).hex())
    lus = LegacyUS.from_program(p)
    assert lus.coin_spends == us.coin_spends()
    assert [sum_hint_as_tuple(_) for _ in lus.sum_hints] == us.sum_hints
    assert [path_hint_as_tuple(_) for _ in lus.path_hints] == us.path_hints
    assert lus.agg_sig_me_network_suffix == us.agg_sig_me_network_suffix
    us1 = fp(p)
    assert us == us1
