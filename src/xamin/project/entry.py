"""Entry abstract base class and concrete Base classes TextEntry and BinaryEntry"""

import typing as t
import csv
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from hashlib import sha256

from thatway import Setting
from loguru import logger

from ..utils.classes import all_subclasses

__all__ = ("Entry", "HintType", "TextEntry", "BinaryEntry", "CsvEntry")

# The types that a 'hint' can adopt
HintType = t.Union[t.Text, t.ByteString, None]


class Entry(ABC):
    """A file entry in a project"""

    #: The path of the file
    path: t.Optional[Path] = None

    #: Settings to change the default behavior
    hint_size = Setting(2048, desc="Size (in bytes) of the hint to read from the file")

    text_encoding = Setting("utf-8", desc="Default text file encoding")

    #: Cached data
    _data = None

    #: The data hash at load/save time
    _loaded_hash: str = ""

    _subclasses = None

    def __init__(self, path: t.Optional[Path] = None):
        self.path = path
        super().__init__()

    def __repr__(self):
        """The string representation for this class"""
        cls_name = self.__class__.__name__
        path = str(getattr(self, "path", None))
        return f"{cls_name}(path='{path}')"

    @staticmethod
    def subclasses() -> t.List[t.Tuple[int, "Entry"]]:
        """Retrieve all subclasses of the Entry class as well as their class hierarchy
        level."""
        if Entry._subclasses is None:
            Entry._subclasses = [
                (c.depth(), c) for c in all_subclasses(Entry) if hasattr(c, "depth")
            ]
        return Entry._subclasses

    @classmethod
    def depth(cls):
        """Return the class hierarchy depth for this class"""
        parent_depths = [b.depth() for b in cls.__bases__ if hasattr(b, "depth")]
        return parent_depths[0] + 1 if parent_depths else 0

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
    def is_unsaved(self) -> bool:
        """Determine whether the given entry has changed and not been saved.

        By definition, entries without a path aren't saved.
        Otherwise, see if the hash of the loaded data matches the current has. If it
        doesn't the the contents of the data have changed.
        """
        if getattr(self, "path", None) is None:
            return True
        elif self.hash != self._loaded_hash:
            return True
        else:
            return False

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
        elif isinstance(self._data, bytes):
            return sha256(self._data).hexdigest()
        else:
            return sha256(pickle.dumps(self._data)).hexdigest()

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
        if hasattr(data, "shape"):
            return data.shape()
        elif hasattr(data, "__len__"):
            return len(data)
        else:
            return ()

    def reset_hash(self):
        """Reset the loaded hash to the new contents of self.data.

        This function is needed when data is freshly loaded from a file, or when
        the data has been freshly saved to the file
        """
        self._loaded_hash = self.hash  # Reset the loaded hash

    def save(self):
        """Save the data to self.path

        Returns
        -------
        saved
            Whether the file was saved

        Raises
        ------
        FileNotFoundError
            Raised if trying to save but the path could not be found.
        """
        if getattr(self, "path", None) is None:
            raise FileNotFoundError(
                f"Could not save entry of type "
                f"'{self.__class__.__name__}' because no path is specified."
            )


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
        Entry.save(self)  # Checks whether a save can be conducted

        data = self.data
        if self.is_unsaved and data:
            self.path.write_text(data)
            self.reset_hash()


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
        Entry.save(self)  # Checks whether a save can be conducted

        data = self.data
        if self.is_unsaved and data:
            self.path.write_bytes(data)
            self.reset_hash()


class CsvEntry(TextEntry):
    """A csv/tsv file entry in a project"""

    #: Customizable settings
    default_delimiters = Setting(",\t", desc="The default delimiters to search")

    #: The cached CSV dialect
    _dialect: t.Optional[csv.Dialect] = None

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Overrides  parent class method to test whether path is a CsvEntry."""
        hint = hint if hint is not None else cls.get_hint(path)
        try:
            # Try to find the dialect. If successful (without exception or None
            # returned)
            dialect = cls.dialect(path=path, hint=hint)
            return True if dialect is not None else False
        except:
            return False

    @classmethod
    def dialect(cls, path: Path, hint: HintType = None) -> csv.Dialect:
        """Retrieve the dialect for the csv file"""
        hint = cls.get_hint(path=path) if hint is None else hint
        dialect = csv.Sniffer().sniff(hint, delimiters=cls.default_delimiters)

        logger.debug(f"{cls.__name__} CSV dialect select: {dialect}")
        return dialect

    @property
    def data(self) -> t.List[t.Tuple[str]]:
        """Overrides parent class method to return the file's binary contents."""
        # Read in the data, if needed
        if not self._data and self.path:
            dialect = self.dialect(path=self.path)

            with open(self.path, "r") as f:
                reader = csv.reader(f, dialect=dialect)
                self._data = list(reader)
        return super().data

    @data.setter
    def data(self, value):
        """Overrides parent data setter.

        Raises
        ------
        TypeError
            If the given value isn't a byte string.
        """
        if not isinstance(value, t.Iterable):
            raise TypeError("Expected 'iterable' value type")
        self._data = value

    @property
    def shape(self) -> t.Tuple[int, int]:
        """Override parent method to give 2d shape in rows, columns"""
        data = self.data
        if hasattr(data, "__len__") and len(data) > 0:
            return (len(data), len(data[0]))
        else:
            return ()

    def save(self):
        """Overrides the parent method to save the text data to self.path"""
        Entry.save(self)  # Check whether a save can be conducted

        data = self.data
        if self.is_unsaved and data:
            # Try to get a dialect. Default to 'excel' (csv) if a dialect cannot
            # be selected from the path
            try:
                dialect = self.get_dialect(self.path) or "excel"
            except:
                dialect = "excel"

            with open(self.path, "w") as f:
                writer = csv.writer(f, dialect=dialect)
                writer.writerows(data)
            self.reset_hash()
