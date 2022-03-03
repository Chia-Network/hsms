from typing import BinaryIO, Type

from . import uint16

from .bin_methods import bin_methods


def streamable_list(the_type):
    """
    This creates a streamable homogenous list of the given streamable object. It has
    a 16-bit unsigned prefix length, so lists are limited to a length of 65535.
    """

    cls_name = "%sList" % the_type.__name__

    def __init__(self, items):
        self._items = tuple(items)

    def __iter__(self):
        return iter(self._items)

    @classmethod
    def parse(cls: Type[cls_name], f: BinaryIO) -> cls_name:
        count = uint16.parse(f)
        items = []
        for _ in range(count):
            item = the_type.parse(f)
            items.append(item)
        return cls(items)

    def stream(self, f: BinaryIO) -> None:
        count = uint16(len(self._items))
        count.stream(f)
        for _ in self._items:
            _.stream(f)

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        return repr(self._items)

    namespace = dict(
        __init__=__init__, __iter__=__iter__, parse=parse,
        stream=stream, __str__=__str__, __repr__=__repr__)
    streamable_list_type = type(cls_name, (bin_methods,), namespace)
    return streamable_list_type
