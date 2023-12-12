# gratuitous coverage tests

import pathlib
import tempfile
import zlib

from clvm_rs import Program

from hsms.process.sign import verify_pairs_for_conditions
from hsms.puzzles.conlang import AGG_SIG_ME, AGG_SIG_UNSAFE
from hsms.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    calculate_synthetic_secret_key,
    solution_for_hidden_puzzle,
)
from hsms.puzzles.p2_conditions import solution_for_conditions
from hsms.util.byte_chunks import (
    blob_for_chunks,
    blob_for_zlib_chunks,
    create_chunks_for_blob,
    ChunkAssembler,
)

import pytest

from .generate import bytes32_generate, se_generate, pk_generate


def test_cssk():
    se = se_generate(1)
    b32 = bytes32_generate(1)
    xse = 2483436177918370406060013642567697118387289473841058299688804535472357425177
    assert int(calculate_synthetic_secret_key(se, b32)) == xse


def test_sfhp():
    pk = pk_generate(1)
    hp = Program.to("foobar")
    sthp = Program.to("fake solve")
    s = solution_for_hidden_puzzle(pk, hp, sthp)
    ethh = "eca8c5557fe1c4929f8d3dd7a5551d023c9a6c4215e69ebe3eb55f84b5a25c95"
    assert s.tree_hash().hex() == ethh


def test_sfc():
    s = solution_for_conditions(Program.to("a bunch of conditions"))
    ethh = "adabdc6a70925a06b1bd3e148d910793abf879de327adc1ff9ea405d72f29a48"
    assert s.tree_hash().hex() == ethh


def test_byte_chunks():
    blob = b"foo" * 10240
    with pytest.raises(ValueError):
        create_chunks_for_blob(blob, 5)

    chunks_1 = create_chunks_for_blob(blob, 2000)
    chunks_2 = create_chunks_for_blob(blob, 4000)
    with pytest.raises(ValueError):
        bogus_list = [chunks_1[0], chunks_2[0]]
        blob_for_chunks(bogus_list)

    with pytest.raises(ValueError):
        bogus_c1 = bytearray(chunks_1[0])
        bogus_c1[0] += 1
        bogus_c1 = bytes(bogus_c1)
        bogus_list = [chunks_1[0], bogus_c1]
        blob_for_chunks(bogus_list)

    ca = ChunkAssembler()
    assert ca.status() == (0, 0)

    c_blob = zlib.compress(blob)
    out = blob_for_zlib_chunks(create_chunks_for_blob(c_blob, 1000))
    assert out == blob

    with pytest.raises(ValueError):
        blob_for_chunks([chunks_1[0]])


def test_aggsig_me_conditions():
    pk_1 = pk_generate(1)
    pk_2 = pk_generate(2)
    b32_1 = bytes32_generate(1)
    b32_2 = bytes32_generate(2)
    b32_3 = bytes32_generate(3)
    conditions = Program.to(
        [[AGG_SIG_ME, bytes(pk_1), b32_1], [AGG_SIG_UNSAFE, bytes(pk_2), b32_2]]
    )
    pairs = list(verify_pairs_for_conditions(conditions, b32_3))
    msg1 = b32_1 + b32_3
    msg2 = b32_2
    assert pairs == [(pk_1, msg1), (pk_2, msg2)]


def test_hsms_dump_us():
    # for some reason, if this import is move to the global scope,
    # the `test_cmd` test fails. Maybe the stdout capture fails?
    from hsms.cmds import hsm_dump_us

    where = pathlib.Path(__file__)
    d = (where.parent / "cmds" / "hsm_dump_us_1.txt").read_text()
    hex_blob = d.split()[1]
    with tempfile.NamedTemporaryFile("w") as f:
        f.write(hex_blob)
        f.flush()
        hsm_dump_us.main([f.name])
