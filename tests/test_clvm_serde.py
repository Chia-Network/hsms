from dataclasses import dataclass

from clvm_rs import Program

from hsms.util.clvm_serde import to_program_for_type, from_program_for_type


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
        assert tp(t) == Program.to(rhs)
        assert fp(tp(t)) == t

    @dataclass
    class Foo:
        a: int
        b: str

    tp = to_program_for_type(Foo)
    foo = Foo(100, "boss")
    assert tp(foo) == Program.to([100, "boss"])
    fp = from_program_for_type(Foo)
    assert foo == fp(tp(foo))

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

    Foo._use_keys = 1
