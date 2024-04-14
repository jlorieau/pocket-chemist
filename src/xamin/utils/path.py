"""
Utilities for paths
"""

import typing as t
from pathlib import Path
from itertools import takewhile


def common_path(*paths: t.Tuple[Path]) -> t.Union[Path, None]:
    """Find the common path for the given paths

    Parameters
    ----------
    paths
        The paths to check for a common denominator

    Returns
    -------
    common_path
        The common path between all the given paths, or
        None if a common path could not be found.

    Examples
    --------
    >>> r = common_path(Path("src/header.h"), Path("src/README.txt"),
    ...                 Path("src/setup.cfg"))
    >>> r.parts
    ('src',)
    >>> r = common_path(Path("/usr/local/bin/python"),
    ...                 Path("/usr/local/src/header.h"))
    >>> r.parts
    ('/', 'usr', 'local')
    >>> r = common_path(Path("src/header.h"), Path("src"))
    >>> r.parts
    ('src',)
    >>> common_path(Path("src/header.h"), Path("README.txt"))  # No common path
    """
    # Filter out paths or path-like objects
    paths = [Path(p) for p in paths if isinstance(p, Path) or isinstance(p, str)]

    # Find all of the absolute paths and split into parts. For example,
    # [("/", "usr", "local", "bin", "python"),
    #  ("/", "usr", "local", "src", "header.h")]
    if any(p.is_absolute() for p in paths):
        parts = [p.absolute().parts for p in paths]
    else:
        parts = [p.parts for p in paths]

    # Take the transpose of the parts list and create a set from each part
    # [{"/"}, {"usr"}, {"local"}, {"bin", "src"}, {"python", "header.h"}]
    parts_t = map(set, zip(*parts))  # transpose

    # Find up to which part the paths are all common
    # ["/", "usr", "local"]
    common_parts = [i.pop() for i in takewhile(lambda s: len(s) == 1, parts_t)]

    # Reconstruct the common path
    return Path(*common_parts) if len(common_parts) > 0 else None
