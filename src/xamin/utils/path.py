"""
Utilities for paths
"""

import typing as t
from pathlib import Path
from itertools import takewhile

__all__ = ("is_root",)


def is_root(path: Path) -> bool:
    """Test whether a path is a root path

    Examples
    --------
    >>> is_root(Path("/usr/src"))
    False
    >>> is_root(Path("README.txt"))
    False
    >>> is_root(Path("/"))
    True
    >>> is_root(Path(""))
    False
    """
    if isinstance(path, Path) and len(path.absolute().parts) == 1:
        return True
    else:
        return False
