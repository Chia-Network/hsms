from typing import Any, Callable, Dict, List, Tuple, Union

from clvm import CLVMObject

from atoms import hexbytes


RecursiveStruct = Union[List, Tuple, Dict, Any]


def remap(s: RecursiveStruct, f: Callable[[Any], Any]) -> RecursiveStruct:
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


def use_hexbytes(s: RecursiveStruct) -> RecursiveStruct:
    """
    Dig through json-like structure s and replace all instances of bytes
    with hexbytes so the repr isn't as ugly.
    """

    def to_hexbytes(s):
        if isinstance(s, bytes):
            return hexbytes(s)
        return s

    return remap(s, to_hexbytes)


def cbor_struct_to_bytes(s: RecursiveStruct) -> bytes:
    """
    Dig through json-like structure s and replace t with bytes(t) for
    every substructure t that supports it. This prepares a structure to
    be serialized with cbor.

    TODO: when we see a CLVM object, stop.
    """

    def to_bytes(k):
        if hasattr(k, "__bytes__"):
            return bytes(k)
        return k

    return remap(s, to_bytes)


def transform_list(
    item_list: List[Any], item_transformation_f: Callable[[Any], Any]
) -> List[Any]:
    r = []
    while item_list.pair:
        this_item, item_list = item_list.pair
        r.append(item_transformation_f(this_item))
    return r


def xform_clvm_list(item_transformation_f):
    """
    Return a function that transforms a list of items by calling
    item_xform(_) on each element _ in the list.
    """

    return lambda clvm_list: transform_list(clvm_list, item_transformation_f)


def transform_dict(program, dict_transformer_f):
    """
    Transform elements of the dict d using the xformer (also a dict,
    where the keys match the keys in d and the values of d are transformed
    by invoking the corresponding values in xformer.
    """
    try:
        r = transform_list(
            program, lambda x: dict_transformer_f(x.pair[0], x.pair[1].pair[0])
        )
    except Exception as ex:
        print(ex)
        breakpoint()
    d = dict(r)
    return d


def xform_clvm_dict(dict_transformer_f):
    """
    Return a function that transforms a list of items by calling
    item_xform(_) on each element _ in the list.
    """
    return lambda x: transform_dict(x, dict_transformer_f)


def transform_by_key(
    key: CLVMObject,
    value: CLVMObject,
    transformation_lookup: Callable[[CLVMObject], Any],
) -> [str, Any]:
    """
    Use this if the key is utf-8 and the value decoding depends on the key.
    """
    key_str = key.atom.decode()
    f = transformation_lookup.get(key_str, lambda x: x)
    final_value = f(value)
    return [key_str, final_value]


def transform_dict_by_key(transformation_lookup: Callable[[CLVMObject], Any]):
    return lambda k, v: transform_by_key(k, v, transformation_lookup)
