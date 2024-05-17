"""An entry for text files"""

from pathlib import Path
from collections.abc import Buffer

from .entry import Entry, Hint

__all__ = ("TextEntry", "PythonEntry", "HtmlEntry", "XmlEntry")


class TextEntry(Entry[str]):
    """A text file entry in a project"""

    @classmethod
    def score(cls) -> int:
        """Override the Entry base class score to give this generic class lower
        precedence than more specializes entry types like CsvEntry"""
        return 5 if cls == TextEntry else super().score()

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

    def deserialize(self, serialized: Buffer | str) -> str:
        """Override the parent class method to return the string unchanged"""
        return serialized if isinstance(serialized, str) else ""


class PythonEntry(TextEntry):
    """A TextEntry for python files"""

    @classmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
        """Overrides  parent class method to test whether path is a PythonEntry."""
        # See if it qualifies as a TextEntry
        is_type = super().is_type(path=path, hint=hint)
        mimetype = cls.guess_mimetype(path=path)

        # Check to see if the mimetype matches
        return is_type and mimetype == "text/x-python"


class HtmlEntry(TextEntry):
    """A TextEntry for html files"""

    @classmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
        """Overrides  parent class method to test whether path is a HtmlEntry."""
        # See if it qualifies as a TextEntry
        is_type = super().is_type(path=path, hint=hint)
        mimetype = cls.guess_mimetype(path=path)

        # Check to see if the mimetype matches
        return is_type and mimetype == "text/html"


class XmlEntry(TextEntry):
    """A TextEntry for xml files"""

    @classmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
        """Overrides  parent class method to test whether path is a XmlEntry."""
        # See if it qualifies as a TextEntry
        is_type = super().is_type(path=path, hint=hint)
        mimetype = cls.guess_mimetype(path=path)

        # Check to see if the mimetype matches
        return is_type and mimetype == "application/xml"
