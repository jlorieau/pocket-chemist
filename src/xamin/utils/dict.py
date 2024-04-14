"""
Utilities for dicts
"""

import typing as t

__all__ = ("recursive_update",)


def recursive_update(d: t.Mapping, u: t.Mapping, excludes: t.Tuple[str] = ()):
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
