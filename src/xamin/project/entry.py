import typing as t
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from hashlib import sha256

from thatway import Setting

__all__ = ("Entry", "TextEntry", "BinaryEntry")

# The types that a 'hint' can adopt
HintType = t.Union[t.Text, t.ByteString, None]


@dataclass
class Entry(ABC):
    """A file entry in a project"""

    #: The path of the file
    path: Path

    #: The (short-)name of the entry
    name: t.Optional[str] = None

    #: Settings to change the default behavior
    hint_size = Setting(2048, desc="Size (in bytes) of the hint to read from the file")

    text_encoding = Setting("utf-8", desc="Default text file encoding")

    #: Cached data
    _data = None

    #: The data hash at load/save time
    _loaded_hash: str = ""

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
        """Return True if path can be parsed as this Entry's type.

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
        """
        return False

    @property
    def is_changed(self) -> bool:
        """Determine whether the given entry has changed and not been saved."""
        return self.hash != self._loaded_hash

    @property
    def hash(self) -> str:
        """The hash for the current data to determine when the data has changed since
        it was loaded.

        Returns
        -------
        hash
            - Empty string, if a hash could not be calculated
            - A hex hash (sha256) of the data
        """
        if self._data is None:
            return ""
        elif isinstance(self._data, str):
            return sha256(self._data.encode(self.text_encoding)).hexdigest()
        else:
            return sha256(self._data).hexdigest()

    @property
    def data(self) -> t.Any:
        """Return the data (or an iterator) of the data.

        Subclasses are responsible for load the data and calling this parent
        property."""
        self._loaded_hash = self.hash
        return self._data

    @data.setter
    def data(self, value):
        """Set the data with the given value"""
        self._data = value

    @property
    def shape(self) -> t.Tuple[int, ...]:
        """Return the shape of the data--i.e. the length along each data array
        dimension."""
        data = self.data
        return data.shape() if hasattr(data, "shape") else (len(data),)

    def save(self):
        """Save the data to self.path

        Returns
        -------
        saved
            Whether the file was saved
        """
        self._loaded_hash = self.hash  # Reset the loaded hash


class TextEntry(Entry):
    """A text file entry in a project"""

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
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
        return isinstance(hint, str)

    @property
    def data(self) -> str:
        """Overrides parent class method to return the file's text."""
        if not self._data and self.path:
            self._data = self.path.read_text()
        return super().data

    @data.setter
    def data(self, value):
        """Overrides parent data setter.

        Raises
        ------
        TypeError
            If the given value isn't a text string.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' value type")
        self._data = value

    def save(self):
        """Overrides the parent method to save the text data to self.path"""
        if self.is_changed and self._data:
            self.path.write_text(self._data)
            super().save()


class BinaryEntry(Entry):
    """A binary file entry in a project"""

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

    @property
    def data(self) -> str:
        """Overrides parent class method to return the file's binary contents."""
        if not self._data and self.path:
            self._data = self.path.read_bytes()
        return super().data

    @data.setter
    def data(self, value):
        """Overrides parent data setter.

        Raises
        ------
        TypeError
            If the given value isn't a byte string.
        """
        if not isinstance(value, bytes):
            raise TypeError("Expected 'bytes' value type")
        self._data = value

    def save(self):
        """Overrides the parent method to save the text data to self.path"""
        if self.is_changed and self._data:
            self.path.write_bytes(self._data)
            super().save()
