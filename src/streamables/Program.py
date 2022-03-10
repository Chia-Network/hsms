import hashlib
import io

from typing import Any

from clvm import run_program, SExp, EvalError
from clvm.operators import OPERATOR_LOOKUP, OperatorDict  # noqa
from clvm.serialize import sexp_from_stream, sexp_to_stream

from .sized_bytes import bytes32
from atoms import bin_methods

from clvm_tools.curry import curry


class Program(SExp, bin_methods):
    """
    A thin wrapper around s-expression data intended to be invoked with "eval".
    """

    @classmethod
    def parse(cls, f):
        return sexp_from_stream(f, cls.to)

    def stream(self, f):
        sexp_to_stream(self, f)

    @classmethod
    def from_bytes(cls, blob: bytes) -> Any:
        f = io.BytesIO(blob)
        return cls.parse(f)  # type: ignore # noqa

    def __bytes__(self) -> bytes:
        f = io.BytesIO()
        self.stream(f)  # type: ignore # noqa
        return f.getvalue()

    def __str__(self) -> str:
        return bytes(self).hex()

    def tree_hash(self):
        if self.listp():
            left = self.to(self.first()).tree_hash()
            right = self.to(self.rest()).tree_hash()
            s = b"\2" + left + right
        else:
            atom = self.as_atom()
            s = b"\1" + atom
        return hashlib.sha256(s).digest()

    def run(
        self,
        args,
        max_cost=None,
        strict=False,
    ) -> "Program":
        operator_lookup = OPERATOR_LOOKUP
        prog_args = Program.to(args)
        if strict:

            def fatal_error(op, arguments):
                raise EvalError("unimplemented operator", arguments.to(op))

            operator_lookup = OperatorDict(
                operator_lookup, unknown_op_handler=fatal_error
            )

        cost, r = run_program(
            self,
            prog_args,
            operator_lookup,
            max_cost,
        )

        return Program.to(r)

    def curry(self, *args) -> "Program":
        cost, r = curry(self, list(args))
        return Program.to(r)


class ProgramPointer(bytes32):

    the_hash: bytes32

    def __new__(cls, v):
        if isinstance(v, SExp):
            v = Program(v).tree_hash()
        return bytes32.__new__(cls, v)


# we actually want the revealed name to be ProgramPointer for some reason
ProgramHash = ProgramPointer
