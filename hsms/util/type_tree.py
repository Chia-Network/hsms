from typing import Callable, get_origin, get_args, TypeVar


_T = TypeVar("_T")
SimpleTypeLookup = dict[type, _T]
CompoundLookup = dict[
    type,
    Callable[
        [type, type, SimpleTypeLookup[_T], "CompoundLookup[_T]", "OtherHandler[_T]"], _T
    ],
]
OtherHandler = Callable[
    [type, SimpleTypeLookup[_T], CompoundLookup[_T], "OtherHandler[_T]"], _T
]


def type_tree(
    t: type,
    simple_type_lookup: SimpleTypeLookup[_T],
    compound_type_lookup: CompoundLookup[
        Callable[
            [type, type, SimpleTypeLookup[_T], CompoundLookup[_T], OtherHandler[_T]], _T
        ]
    ],
    other_f: OtherHandler[_T],
) -> _T:
    """
    Recursively descend a "type tree" invoking the appropriate functions.

    `simple_type_lookup`: a type to callable look-up. Must return a `_T` value.
    `compound_type_lookup`: recursively handle compound types like `list` and `tuple`.
    `other_f`: a function to take a type and return

    This function is helpful for run-time building a complex function that operates
    on a complex type out of simpler functions that operate on base types.
    """
    origin = get_origin(t)
    f = compound_type_lookup.get(origin)
    if f:
        return f(origin, get_args(t), simple_type_lookup, compound_type_lookup, other_f)
    f = simple_type_lookup.get(t)
    if f:
        return f
    return other_f(t, simple_type_lookup, compound_type_lookup, other_f)
