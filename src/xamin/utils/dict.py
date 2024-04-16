"""
Utilities for dicts
"""

import typing as t
from collections import OrderedDict

__all__ = ("tuple_to_dict", "recursive_update")


def tuple_to_dict(item) -> t.OrderedDict:
    """Convert a tree of tuples to an ordered dict

    Parameters
    ----------
    item
        The tuple tree to convert to an ordered dict tree

    Returns
    -------
    tree
        The ordered dict tree

    Examples
    --------
    >>> tuple_to_dict((
    ...  ('a', 1), ('b', 2), ('c', 3)
    ...  ))
    OrderedDict({'a': 1, 'b': 2, 'c': 3})
    >>> tuple_to_dict(('a', 1))
    OrderedDict({'a': 1})
    >>> tuple_to_dict((
    ...  ('a', (('a1', 1), ('a2', 2), ('a3', 3))),
    ...  ('b', ('one', 'two')),
    ...  ('c', (1, 2, 3))
    ...  )) # doctest: +NORMALIZE_WHITESPACE
    OrderedDict({'a': OrderedDict({'a1': 1, 'a2': 2, 'a3': 3}),
                 'b': OrderedDict({'one': 'two'}),
                 'c': (1, 2, 3)})
    """
    if not isinstance(item, t.Iterable):
        return item
    if isinstance(item, t.Mapping):
        item = item.items()

    if len(item) >= 2 and all(hasattr(i, "__len__") and len(i) == 2 for i in item):
        # ex: (('a', 1), ('b', 2), ('c', 2))
        return OrderedDict(tuple((k, tuple_to_dict(v)) for k, v in item))
    elif len(item) == 2:
        # ex: ('a', 1)
        return OrderedDict(((item[0], tuple_to_dict(item[1])),))
    elif len(item) == 1:
        # ex: (('a', 1),)
        return tuple_to_dict(item[0])
    else:
        return item


def recursive_update(
    d: t.Mapping, u: t.Mapping, excludes: t.Tuple[str] = ()
) -> t.Mapping:
    """Recursively update mutables in dict 'd' with updates 'u'.

    d
        The dict update
    u
        The updates for the dict
    excludes
        Keys to exclude from the update

    References
    ----------
    - https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

    Examples
    --------
    >>> recursive_update({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
    {'a': 1, 'b': 3, 'c': 4}
    >>> recursive_update({'a': 1, 'b': {'c': 2, 'd': 3}}, {'b': {'c': 4}})
    {'a': 1, 'b': {'c': 4, 'd': 3}}
    >>> recursive_update({'a': 1, 'b': {'c': 2, 'd': 3}}, {'b': 4})  # Mismatched type
    {'a': 1, 'b': 4}
    >>> recursive_update({'a': 1, 'b': 2}, {'b': 3, 'c': 4}, excludes=('b',))
    {'a': 1, 'b': 2, 'c': 4}
    """
    for k, v in u.items():
        if k in excludes:
            continue
        if isinstance(v, t.Mapping):
            d[k] = recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
