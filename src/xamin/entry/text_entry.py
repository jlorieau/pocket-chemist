"""An entry for text files"""

from pathlib import Path

from .entry import Entry, Hint

__all__ = ("TextEntry",)


class TextEntry(Entry[str]):
    """A text file entry in a project"""

    @classmethod
    def score(cls) -> int:
        """Override the Entry base class score to give this generic class lower
        precedence than more specializes entry types like CsvEntry"""
        return 5

    @classmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
        """Overrides  parent class method to test whether path is a TextEntry.

        Examples
        --------
        >>> p = Path(__file__)  # this .py text file
        >>> TextEntry.is_type(p)
        True
        >>> import sys
        >>> e = Path(sys.executable)  # Get the python interpreter executable
        >>> TextEntry.is_type(e)
        False
        """
        hint = hint if hint is not None else cls.get_hint(path)
        return True if hint and hint.utf_8 else False

    def default_data(self) -> str:
        return ""
