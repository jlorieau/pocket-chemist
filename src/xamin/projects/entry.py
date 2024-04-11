import typing as t
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass

from thatway import Setting

__all__ = ("Entry",)

# The types that a 'hint' can adopt
HintType = t.Union[t.Text, t.ByteString, None]


@dataclass
class Entry(ABC):
    """A file entry in a project"""

    #: The (short-)name of the entry
    name: str

    #: The path of the file
    path: t.Optional[Path] = None

    #: Settings to change the default behavior
    hint_size = Setting(2048, desc="Size (in bytes) of the hint to read from the file")

    text_encoding = Setting("utf-8", desc="Default text file encoding")

    @classmethod
    def get_hint(cls, path: Path) -> t.Union[HintType]:
        """Retrieve the hint bytes or text from the given path

        Parameters
        ----------
        path
            The path to get the hint from

        Returns
        -------
        hint
            - The first 'hint_size' bytes of the file given by the path.
            - If a text string (UTF-8) can be decoded, it will be returned.
            - Otherwise a byte string will be returned.
            - If the path doesn't point to a file or the file can't be read, the hint
              is None

        Examples
        --------
        >>> p = Path(__file__)  # this .py text file
        >>> hint = Entry.get_hint(p)
        >>> type(hint)
        <class 'str'>
        >>> import sys
        >>> e = Path(sys.executable)  # Get the python interpreter executable
        >>> hint = Entry.get_hint(e)
        >>> type(hint)
        <class 'bytes'>
        """
        # Read the first 'hint_size' bytes from the file
        try:
            with open(path, "rb") as f:
                bytes = f.read(cls.hint_size)
        except:
            return None

        # Try decoding the bytes to text
        try:
            return bytes.decode(cls.text_encoding)
        except:
            return bytes

    @classmethod
    @abstractmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Determine if the given file hint can be converted to this type"""
        return False

    @abstractmethod
    def is_unsaved(self) -> bool:
        """Determine whether the given entry has unsaved changes"""
        return True


class TextEntry(Entry):
    """A text file entry in a project"""

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Return True if this is a Text File Entry.

        Parameters
        ----------
        path
            The path whose file should be tested whether it matches this type.
        hint
            The optional hint from the path to be used in the determination.

        Returns
        -------
        is_type
            True, if the file can be loaded as this Entry's type

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
        return isinstance(hint, str)
