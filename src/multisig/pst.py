from atoms import hexbytes
from hashable import BLSSignature, CoinSolution, Program


def remap(s, f):
    """
    Iterate through a json-like structure, applying remap(_, f) recursively
    to all items in collectives and f(_) to all non-collectives
    within the structure.
    """
    if isinstance(s, list):
        return [remap(_, f) for _ in s]
    if isinstance(s, tuple):
        return tuple([remap(_, f) for _ in s])
    if isinstance(s, dict):
        return [[remap(k, f), remap(v, f)] for k, v in s.items()]
    return f(s)


def use_hexbytes(s):
    """
    Dig through json-like structure s and replace all instances of bytes
    with hexbytes so the repr isn't as ugly.
    """

    def to_hexbytes(s):
        if isinstance(s, bytes):
            return hexbytes(s)
        return s

    return remap(s, to_hexbytes)


def cbor_struct_to_bytes(s):
    """
    Dig through json-like structure s and replace t with bytes(t) for
    every substructure t that supports it. This prepares a structure to
    be serialized with cbor.
    """

    def to_bytes(k):
        if hasattr(k, "__bytes__"):
            return bytes(k)
        return k

    return remap(s, to_bytes)


class PartiallySignedTransaction(dict):
    @classmethod
    def from_bytes(cls, blob):
        pst = Program.from_bytes(blob)
        return cls(transform_pst(pst))

    def __bytes__(self):
        cbor_obj = cbor_struct_to_bytes(self)
        return bytes(Program.to(cbor_obj))


def xform_aggsig_sig_pair(pair):
    """
    Transform a pair (aggsig_pair_bytes, sig_bytes)
    to (aggsig_pair, BLSSignature).
    """
    aggsig = BLSSignature.aggsig_pair.from_bytes(pair[0])
    sig = BLSSignature.from_bytes(pair[1])
    return (aggsig, sig)


def xform_clvm_list(item_xform):
    """
    Return a function that transforms a list of items by calling
    item_xform(_) on each element _ in the list.
    """

    def xform(item_list):
        r = []
        while item_list.pair:
            this_item, item_list = item_list.pair
            r.append(item_xform(this_item))
        return r

    return xform


def transform_dict(program_pairs, xformers):
    """
    Transform elements of the dict d using the xformer (also a dict,
    where the keys match the keys in d and the values of d are transformed
    by invoking the corresponding values in xformer.
    """
    r = xform_clvm_list(lambda x: [x.pair[0].atom.decode(), x.pair[1].pair[0]])(
        program_pairs
    )
    breakpoint()
    d = {}
    for k, v in r:
        v_transformer = xformers.get(k, lambda x: x)
        d[k] = v_transformer(v)
    return d


def xform_dict(xformers):
    """
    Return a function that transforms a list of items by calling
    item_xform(_) on each element _ in the list.
    """
    return lambda x: transform_dict(x, xformers)


def to_str(b: bytes) -> str:
    return b.decode()


HINT_TRANSFORMS = dict()


PST_TRANSFORMS = dict(
    coin_solutions=xform_clvm_list(lambda x: CoinSolution.from_bytes(x.atom)),
    sigs=xform_clvm_list(xform_aggsig_sig_pair),
    delegated_solution=lambda x: Program.from_bytes(x.atom),
    hd_hints=xform_dict(HINT_TRANSFORMS),
)


def transform_pst(pst):
    """
    Turn a pst `Program` into its corresponding constituent parts.
    """
    return xform_dict(PST_TRANSFORMS)(pst)
