from dataclasses import is_dataclass
from types import UnionType
from typing import Any, BinaryIO, Callable, Union, TypeVar, get_type_hints

from chia_base.atoms import uint8, uint32

from clvm_rs import Program

from .type_tree import type_tree


# some helper methods to implement chia serialization
#
def read_bytes(p: Program) -> bytes:
    if p.atom is None:
        raise EncodingError("expected atom for str")
    return p.atom


def read_str(p: Program) -> str:
    return read_bytes(p).decode()


def read_int(p: Program) -> int:
    return Program.int_from_bytes(read_bytes(p))


def serialize_for_list(origin, args, *etc):
    write_item = type_tree(args[0], *etc)

    def serialize_list(items):
        return Program.to([write_item(_) for _ in items])

    return serialize_list


def serialize_for_tuple(origin, args, *etc):
    write_items = [type_tree(_, *etc) for _ in args]

    def serialize_tuple(items):
        return Program.to([write_f(item) for write_f, item in zip(write_items, items)])

    return serialize_tuple


def ser_for_union(origin, args, *etc):
    item_type = optional_from_union(args)
    if item_type is not None:
        write_item = type_tree(item_type, *etc)

        def serialize_optional(f, item):
            c = 0 if item is None else 1
            f.write(bytes([c]))
            if item is not None:
                write_item(f, item)

        return serialize_optional


SERIALIZER_COMPOUND_TYPE_LOOKUP = {
    list: serialize_for_list,
    tuple: serialize_for_tuple,
    # Union: to_program_for_union,
    # UnionType: to_program_for_union,
}


def make_ser_for_dcf(f_name: str, f_type: type, *args):
    ser_for_field = type_tree(f_type, *args)

    def f(obj):
        return ser_for_field(getattr(obj, f_name))

    return f


def fail_ser(t, *args):
    if t in [str, bytes, int]:
        return Program.to

    if is_dataclass(t):
        # TODO: handle key-based data class
        # handle regular dataclass
        fields = get_type_hints(t)

        if hasattr(t, "_use_keys"):
            pass

        streaming_calls = []
        for f_name, f_type in fields.items():
            if f_name.startswith("_"):
                continue
            streaming_calls.append(make_ser_for_dcf(f_name, f_type, *args))

        def serialize_dataclass(item):
            return Program.to([sc(item) for sc in streaming_calls])

        return serialize_dataclass

    raise TypeError(f"can't process {t}")


def fail_deser(t, *args):
    if is_dataclass(t):
        # TODO: handle key-based data class
        # handle regular dataclass
        fields = get_type_hints(t)

        tuple_type = tuple[
            *list(
                f_type
                for f_name, f_type in fields.items()
                if not f_name.startswith("_")
            )
        ]
        des_f = type_tree(tuple_type, *args)

        def des_dataclass(p: Program):
            values = des_f(p)
            return t(*values)

        return des_dataclass

    raise TypeError(f"can't process {t}")


def to_program_for_type(t: type) -> Callable[[dict[str, Any]], Program]:
    return type_tree(
        t,
        {},
        SERIALIZER_COMPOUND_TYPE_LOOKUP,
        fail_ser,
    )


def deser_for_list(origin, args, *etc):
    read_item = type_tree(args[0], *etc)

    def deserialize_list(p: Program) -> tuple[int, Any]:
        return [read_item(_) for _ in p.as_iter()]

    return deserialize_list


def deser_for_tuple(origin, args, *etc):
    read_items = [type_tree(_, *etc) for _ in args]

    def deserialize_tuple(p: Program) -> tuple[int, Any]:
        items = list(p.as_iter())
        if len(items) != len(read_items):
            raise EncodingError("wrong size program")
        return tuple(f(_) for f, _ in zip(read_items, items))

    return deserialize_tuple


def deser_for_union(origin, args, *etc):
    item_type = optional_from_union(args)
    if item_type is not None:
        read_item = type_tree(item_type, *etc)

        def deserialize_optional(f: BinaryIO) -> tuple[int, Any]:
            v = uint8.parse(f)
            if v == 0:
                return None
            return read_item(f)

        return deserialize_optional
    raise TypeError("can't handle unions not of the form `A | None`")


DESERIALIZER_COMPOUND_TYPE_LOOKUP = {
    list: deser_for_list,
    tuple: deser_for_tuple,
    # Union: deser_for_union,
    # UnionType: deser_for_union,
}


def optional_from_union(args: type) -> Callable[[dict[str, Any]], bytes] | None:
    tn = type(None)
    if len(args) == 2 and tn in args:
        return args[0 if args[1] is tn else 1]
    return None


def from_program_for_type(t: type) -> Callable[[memoryview, int], tuple[int, Any]]:
    return type_tree(
        t,
        {bytes: read_bytes, str: read_str, int: read_int},
        DESERIALIZER_COMPOUND_TYPE_LOOKUP,
        fail_deser,
    )


def merging_function_for_callable_parameters(f: Callable) -> Callable:
    parameter_names = [k for k in f.__annotations__.keys() if k != "return"]

    def merging_function(*args, **kwargs) -> tuple[Any]:
        merged_args = args + tuple(kwargs[_] for _ in parameter_names[len(args):])
        return merged_args

    return merging_function
