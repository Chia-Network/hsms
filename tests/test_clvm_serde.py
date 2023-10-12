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
    Nonexpandable,
    tuple_frugal,
)
from .core.signing_hints import SumHint, PathHint
from .core.unsigned_spend import (
    UnsignedSpend,
    coin_spend_to_tuple,
    coin_spend_from_tuple,
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


def test_serde_nonexpandable():
    @dataclass
    class Foo(Nonexpandable):
        a: int
        b: str

    tp = to_program_for_type(Foo)
    fp = from_program_for_type(Foo)
    p = Program.to((1000, "hello"))
    foo = fp(p)
    assert foo.a == 1000
    assert foo.b == "hello"
    p1 = tp(foo)
    assert p1 == p

    @dataclass
    class Bar(Nonexpandable):
        a: int
        b: str
        c: list[int]

    tp = to_program_for_type(Bar)
    fp = from_program_for_type(Bar)
    p = Program.to((1000, ("hello", [5, 19, 220])))
    foo = fp(p)
    assert foo.a == 1000
    assert foo.b == "hello"
    assert foo.c == [5, 19, 220]
    p1 = tp(foo)
    assert p1 == p


def rnd_coin_spend(seed: int) -> CoinSpend:
    r = random.Random(seed)
    parent = r.randbytes(32)
    puzzle = Program.to(f"puz: {r.randbytes(5).hex()}")
    amount = r.randint(1, 1000) * int(1e3)
    solution = Program.to(f"sol: {r.randbytes(10).hex()}")
    coin = Coin(parent, puzzle.tree_hash(), amount)
    return CoinSpend(coin, puzzle, solution)


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
    assert lsh.public_keys == sum_hint.public_keys
    assert lsh.synthetic_offset == sum_hint.synthetic_offset
    sh1 = fp(p)
    assert sum_hint == sh1


CoinSpendTuple = tuple[bytes, Program, int, Program]


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
    assert lph.root_public_key == path_hint.root_public_key
    assert lph.path == path_hint.path
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


def test_interop_unsigned_spend():
    from hsms.process.unsigned_spend import UnsignedSpend as LegacyUS

    cs_list = [rnd_coin_spend(_) for _ in range(10)]
    cst_list = [coin_spend_to_tuple(_) for _ in cs_list]

    secret_keys = [BLSSecretExponent.from_int(_) for _ in range(5)]
    public_keys = [_.public_key() for _ in secret_keys]
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
    for k in "public_keys synthetic_offset".split():
        for lh, rh in zip(lus.sum_hints, us.sum_hints):
            assert getattr(lh, k) == getattr(rh, k)
    for k in "root_public_key path".split():
        for lh, rh in zip(lus.path_hints, us.path_hints):
            assert getattr(lh, k) == getattr(rh, k)
    assert lus.agg_sig_me_network_suffix == us.agg_sig_me_network_suffix
    us1 = fp(p)
    assert us == us1


def test_tuple_frugal():
    Foo = tuple_frugal[int, str, bytes]

    tp = to_program_for_type(Foo)
    fp = from_program_for_type(Foo)
    p = Program.to((1000, ("hello", b"bob")))
    foo = fp(p)
    assert foo[0] == 1000
    assert foo[1] == "hello"
    assert foo[2] == b"bob"
    p1 = tp(foo)
    assert p1 == p

