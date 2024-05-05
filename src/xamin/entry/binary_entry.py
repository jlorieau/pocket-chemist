"""An entry for text files"""

import typing as t
from pathlib import Path

from .entry import Entry, Hint

__all__ = ("BinaryEntry",)


class BinaryEntry(Entry[bytes]):
    """A binary file entry in a project"""

    encoding = bytes

    @classmethod
    def score(cls) -> int:
        """Override the Entry base class score to give this generic class lower
        precedence than more specializes entry types"""
        return 5

    @classmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
        """Overrides  parent class method to test whether path is a BinaryEntry.

        Examples
        --------
        >>> p = Path(__file__)  # this .py text file
        >>> BinaryEntry.is_type(p)
        False
        >>> import sys
        >>> e = Path(sys.executable)  # Get the python interpreter executable
        >>> BinaryEntry.is_type(e)
        True
        """
        hint = hint if hint is not None else cls.get_hint(path)

        return False if hint and hint.utf_8 else True

    def default_data(self):
        return b""
