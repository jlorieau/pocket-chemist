"""An entry for text files"""

import typing as t
from pathlib import Path

from .entry import Entry, HintType

__all__ = ("BinaryEntry",)


class BinaryEntry(Entry[bytes]):
    """A binary file entry in a project"""

    encoding = bytes

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Overrides  parent class method to test whether path is a BinaryEntry.

        Examples
        --------
        >>> p = Path(__file__)  # this .py text file
        >>> TextEntry.is_type(p)
        False
        >>> import sys
        >>> e = Path(sys.executable)  # Get the python interpreter executable
        >>> TextEntry.is_type(e)
        True
        """
        hint = hint if hint is not None else cls.get_hint(path)
        return isinstance(hint, bytes)

    def default_data(self):
        return b""
