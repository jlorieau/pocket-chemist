"""
Utilities for lists
"""
import typing as t


def wraplist(obj, default=None) -> t.List:
    """Wrap the object in a list, if needed

    Parameters
    ----------
    obj
        The object to wrap in a list
    default
        If obj is None, return the default instead. Not that if a default
        is not specified, the default returned object is an empty list.

    Examples
    --------
    >>> wraplist(None)
    []
    >>> wraplist('test')
    ['test']
    >>> wraplist([1, 2, 3])
    [1, 2, 3]
    """
    if obj is None:
        return default if default is not None else []
    elif hasattr(obj, '__iter__') and not isinstance(obj, str):
        # Nothing to do, we've good
        return obj
    else:
        # wrap in a list
        return [obj]
