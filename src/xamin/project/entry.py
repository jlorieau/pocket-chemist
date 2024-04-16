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

__all__ = ("Entry", "HintType", "TextEntry", "BinaryEntry")

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
        name = f"'{self.path}'" if self.path is not None else "None"
        return f"{cls_name}(path={name})"

    def __getstate__(self) -> t.Dict:
        """Get a copy of the current state for serialization"""
        return {"path": self.path}

    def __setstate__(self, state):
        """Set the state for the entry based on the given state copy"""
        self.path = state.get("path", None)

    def __eq__(self, other):
        """Test the equivalence of two entries"""
        conditions = (
            self.__class__ == other.__class__,  # same class
            self.path == getattr(other, "path", None),  # same path
        )
        return all(conditions)

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
            This is only checked to retrieve a hint, if one isn't given.
        hint
            The optional hint from the path to be used in the determination.

        Returns
        -------
        is_type
            True, if the file can be loaded as this Entry's type
        """
        return False

    @classmethod
    def guess_type(
        cls, path: Path, hint: HintType = None
    ) -> t.Union[t.Type["Entry"], None]:
        """Try to guess the correct Entry class from the given path and (optional)
        hint.

        Paramters
        ---------
        path
            The path to the file whose contents should be guessed
        hint
            Information of type HintType that can be used to guide the guessing

        Returns
        -------
        entry_type
            The best entry class for the given arguments, or
            None if a best entry class could not be found.
        """
        # Must be a path type, if no hint is specified
        if isinstance(path, Path) or isinstance(path, str):
            path = Path(path)
        elif hint is None:
            # Can't figure out the type without a valid type or a valid hint
            return None

        # Get the hint, if it wasn't specified
        hint = hint if hint is not None else cls.get_hint(path)

        # Find the best class from those with the highest class hierarchy level
        # i.e. the more subclassed, the more specific is a type
        highest_hierarchy = 0
        best_cls = None

        for hierarchy, cls in cls.subclasses():
            if hierarchy > highest_hierarchy and cls.is_type(path=path, hint=hint):
                best_cls = cls

        if best_cls is not None:
            logger.debug(f"Found best Entry class '{best_cls}' for path: {path}")
            return best_cls
        else:
            return None

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
        self.reset_hash()
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
            return (len(data),)
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
