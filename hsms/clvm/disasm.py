import io

from clvm_rs.program import Program

PRINTABLE = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    r"!#$%&'()*+,-./:;<=>?@[]^_`{|}~ "
)


def type_for_atom(atom) -> str:
    if len(atom) > 2:
        try:
            v = atom.decode("utf8")
            if all(c in PRINTABLE for c in v):
                if '"' in v:
                    if "'" in v:
                        return "H"
                    return "SQ"
                return "DQ"
        except UnicodeDecodeError:
            pass
        return "H"
    if Program.int_to_bytes(Program.int_from_bytes(atom)) == atom:
        return "I"
    return "H"


KWS = (
    # core opcodes 0x01-x08
    ". q a i c f r l x "
    # opcodes on atoms as strings 0x09-0x0f
    "= >s sha256 substr strlen concat . "
    # opcodes on atoms as ints 0x10-0x17
    "+ - * / divmod > ash lsh "
    # opcodes on atoms as vectors of bools 0x18-0x1c
    "logand logior logxor lognot . "
    # opcodes for bls 1381 0x1d-0x1f
    "point_add pubkey_for_exp . "
    # bool opcodes 0x20-0x23
    "not any all . "
    # misc 0x24
    "softfork "
).split()


KEYWORD_FROM_ATOM = {Program.int_to_bytes(k): v for k, v in enumerate(KWS)}
KEYWORD_TO_ATOM = {v: k for k, v in KEYWORD_FROM_ATOM.items()}


def format_pair(f, sexp: Program, keyword_from_atom):
    f.write("(")
    is_first = True
    while sexp.atom is None:
        pair = sexp.pair
        if not is_first:
            f.write(" ")
        format_program(f, pair[0], keyword_from_atom, is_first=is_first)
        sexp = pair[1]
        is_first = False
    if len(sexp.atom) > 0:
        f.write(" . ")
        format_program(f, sexp, keyword_from_atom, is_first=False)
    f.write(")")


def format_program(f, sexp: Program, keyword_from_atom, is_first=False):
    if sexp.pair:
        format_pair(f, sexp, keyword_from_atom)
        return

    atom = sexp.atom

    if is_first:
        kw = keyword_from_atom.get(atom)
        if kw is not None and kw != ".":
            f.write(kw)
            return

    type = type_for_atom(atom)

    if type == "I":
        f.write("%d" % Program.int_from_bytes(atom))
    elif type == "H":
        f.write("0x%s" % atom.hex())
    elif type == "DQ":
        f.write('"%s"' % atom.decode("utf8"))
    elif type == "SQ":
        f.write("'%s'" % atom.decode("utf8"))
    else:
        try:
            f.write(atom.decode("utf8"))
        except UnicodeDecodeError:
            f.write("(indecipherable symbol: %s)" % atom.hex())


def disassemble(sexp, keyword_from_atom=KEYWORD_FROM_ATOM):
    f = io.StringIO()
    format_program(f, sexp, keyword_from_atom=keyword_from_atom)
    return f.getvalue()
