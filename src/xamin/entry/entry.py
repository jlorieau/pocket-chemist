"""Entry base class and exceptions definition.
"""

import typing as t
import pickle
import mimetypes
from abc import ABC, abstractmethod
from collections.abc import Buffer
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256

from thatway import Setting
from loguru import logger

__all__ = ("Entry", "MissingPath", "FileChanged")

# Generic type annotation
T = t.TypeVar("T")


#: A named tuple
@dataclass(slots=True)
class Hint:
    """A dataclass to store data hints from a file in different formats"""

    #: The data hint in bytes
    bytes: bytes

    @property
    def utf_8(self) -> str | None:
        """Convert the bytes hint into utf-8 text, if possible, or None, if not
        possible."""
        try:
            return self.bytes.decode("utf-8")
        except UnicodeDecodeError:
            return None


class EntryException(Exception):
    """Exception raised in processing entries."""


class MissingPath(EntryException):
    """Exception raised when trying to save/load a file but no path is specified"""


class FileChanged(EntryException):
    """Exception raised when an entry tries to save but the file it is saving to
    is newer."""


class Entry(ABC, t.Generic[T]):
    """Entry base class to manage serializing/deserializing data from files and tracking
    changes and loading of data."""

    #: The path of the file
    path: t.Optional[Path] = None

    #: Settings to change the default behavior
    hint_size: t.ClassVar[Setting] = Setting(
        2048, desc="Size (in bytes) of the hint to read from the file"
    )

    #: The encoding for serialize data. Allowed values include "utf-8", "bytes"
    encoding: str = "utf-8"

    #: Cached data
    _data: T

    #: The data hash at load/save time
    _loaded_hash: str = ""

    #: The mtime of the data loaded from a file
    _data_mtime: float | None = None

    #: The cached Entry subclasses
    _subclasses: t.ClassVar[t.Set[t.Type["Entry"]]] = set()

    def __init_subclass__(cls) -> None:
        Entry._subclasses.add(cls)

    def __init__(self, path: t.Optional[Path] = None):
        self.path = Path(path) if path is not None else None
        super().__init__()

    def __repr__(self) -> str:
        """The string representation for this class"""
        cls_name = self.__class__.__name__
        name = f"'{self.path}'" if self.path is not None else "None"
        return f"{cls_name}(path={name})"

    def __eq__(self, other: object) -> bool:
        """Test the equivalence of two entries.

        This method does not check self._data because this can be loaded from the path.
        """
        equal = True

        if self.__class__ != other.__class__:
            # different classes
            equal &= False

        if (
            self.path is not None
            and hasattr(other, "path")
            and isinstance(other.path, Path)
            and self.path.absolute() != other.path.absolute()
        ):
            # If paths available but their absolute paths are not the same
            equal &= False
        elif self.path != getattr(other, "path", None):
            # If paths are unavaible, then they should match
            equal &= False

        return equal

    def __getstate__(self) -> t.Dict:
        """Get a copy of the current state for serialization"""
        return {"path": self.path}

    def __setstate__(self, state: t.Dict) -> None:
        """Set the state for the entry based on the given state copy"""
        self.path = state.get("path", None)

    @classmethod
    def _generics_type(cls) -> tuple[t.Any, ...]:
        """Retrieve the type 'T' of the Entry class or subclass"""
        assert hasattr(cls, "__orig_bases__")
        return t.get_args(cls.__orig_bases__[0])

    @staticmethod
    def subclasses() -> list[type["Entry"]]:
        """Retrieve a list of Entry subclasses sorted by score."""
        sort = sorted([cls for cls in Entry._subclasses], key=lambda cls: cls.score())
        return list(sort)

    @classmethod
    def get_hint(cls, path: Path | None) -> Hint | None:
        """Retrieve the hint bytes from the given path

        Parameters
        ----------
        path
            The path to get the hint from

        Returns
        -------
        hint
            A hint with 'hint_size' bytes of the file given by the path, or
            None if a hint could not be retrieved. This can happen if the file
            is not readable or doesn't exist.
        """
        if path is None:
            return None
        # Read the first 'hint_size' bytes from the file
        try:
            with open(path, "rb") as f:
                return Hint(bytes=f.read(cls.hint_size))
        except:
            return None

    @classmethod
    @abstractmethod
    def is_type(cls, path: Path, hint: Hint | None = None) -> bool:
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
        cls, path: Path, hint: Hint | None = None
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

        # Get the hint, if it wasn't specified
        hint = hint if hint is not None else cls.get_hint(path)

        # Can't retrieve the hint and, therefore, can't figure out which entry
        # type to use.
        if hint is None:
            return None

        # Find the best class from those with the highest class hierarchy level
        # i.e. the more subclassed, the more specific is a type
        highest_score = 0
        best_subcls = None

        for subcls in cls.subclasses():
            score = subcls.score()
            is_type = subcls.is_type(path=path, hint=hint)

            # Set a new higher score class if a compatible class if found
            if score > highest_score and is_type:
                best_subcls = subcls
                highest_score = score

        if best_subcls is not None:
            logger.debug(f"Found best Entry class '{best_subcls}' for path: {path}")
            return best_subcls
        else:
            return None

    @classmethod
    def guess_mimetype(cls, path: Path) -> str | None:
        """Guess the mimetype of the given path"""
        mimetype, encoding = mimetypes.guess_type(path)
        return mimetype

    @classmethod
    def score(cls) -> int:
        """Evaluate the score (precedence) of this class in relation to other
        concrete Entry classes"""
        if hasattr(cls.__base__, "score") and cls.__base__ is not None:
            # Increment the score by 10 for each class inheritance
            return cls.__base__.score() + 10
        else:
            # Start at a base score of 0 for the base "Entry" class
            return 0

    @property
    def is_stale(self) -> bool:
        """Determine whether the data is stale and should be reloaded from self.path."""

        # Setup logger
        if __debug__:

            def state(value: bool, reason: str) -> bool:
                logger.debug(f"{self.__class__.__name__}.is_stale={value}. {reason}")
                return value

        else:

            def state(value: bool, reason: str) -> bool:
                return value

        # Evaluate the state
        if not hasattr(self, "_data"):
            return True

        elif self.path is None:
            return state(False, "No path was specified")

        elif not self.path.exists():
            return state(False, "The file path does not exist")

        elif self.path.exists() and (self._data_mtime is None or self._data is None):
            return state(True, f"File path exists, but not yet loaded: '{self.path}'")

        elif self.is_file_newer:
            return state(True, "The file's mtime is newer than the loaded data mtime")

        else:
            return state(False, "The data mtime is as new as the file's mtime")

    @property
    def is_file_newer(self) -> bool:
        """Determine whether the file is newer than the data that was loaded from it."""
        return (
            self.path is not None
            and self._data_mtime is not None
            and self._data_mtime < self.path.stat().st_mtime
        )

    def reset_mtime(self) -> None:
        """Update the mtime of the loaded data (self._data_mtime) to equal that of
        the file (self.path)"""
        if self.path is not None:
            self._data_mtime = self.path.stat().st_mtime

    @property
    def is_unsaved(self) -> bool:
        """Determine whether the given entry has changed and not been saved.

        By definition, entries without a path aren't saved.
        Otherwise, see if the hash of the loaded data matches the current has. If it
        doesn't the the contents of the data have changed.
        """
        # Setup logger
        if __debug__:

            def state(value: bool, reason: str) -> bool:
                logger.debug(f"{self.__class__.__name__}.is_unsaved={value}. {reason}")
                return value

        else:

            def state(value: bool, reason: str) -> bool:
                return value

        # Evaluate the state
        if getattr(self, "path", None) is None:
            return state(True, "No path was specified")
        elif self.hash != self._loaded_hash:
            return state(True, "Data hash is not equal to the loaded file hash")
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
        if getattr(self, "_data", None) is None:
            return ""
        elif isinstance(self._data, str):
            return sha256(self._data.encode(self.encoding)).hexdigest()
        elif isinstance(self._data, bytes):
            return sha256(self._data).hexdigest()
        else:
            return sha256(pickle.dumps(self._data)).hexdigest()

    def reset_hash(self) -> None:
        """Reset the loaded hash to the new contents of self.data.

        This function is needed when data is freshly loaded from a file, or when
        the data has been freshly saved to the file
        """
        self._loaded_hash = self.hash  # Reset the loaded hash

    @property
    def data(self) -> T:
        """Return the data (or an iterator) of the data.

        Subclasses are responsible for load the data and calling this parent
        property."""
        if self.is_stale:
            self.load()
        return self._data

    @data.setter
    def data(self, value: T) -> None:
        """Set the data with the given value"""
        self._data = value

    @property
    def shape(self) -> tuple[int, ...]:
        """Return the shape of the data--i.e. the length along each data array
        dimension."""
        data = self.data

        if hasattr(data, "shape"):
            return data.shape()
        elif hasattr(data, "__len__"):
            return (len(data),)
        else:
            return ()

    def default_data(self) -> T:
        """A factory method to return a new instance of self.data"""
        raise NotImplementedError

    def serialize(self, data: T) -> Buffer | str:
        """Serialize (dump) this entry or the specified data to text or bytes.

        Parameters
        ----------
        data
            The data to serialize

        Returns
        -------
        serialized
            The data serialized in text (str) or binary (bytes) format.
        """
        if isinstance(data, Buffer | str):
            return data
        else:
            raise NotImplementedError

    def deserialize(self, serialized: Buffer | str) -> T:
        """Deserialize (load) this entry or the specified data to text or bytes.

        Parameters
        ----------
        serialized
            The text (str) or binary data (bytes) for deserialize as data

        Returns
        -------
        data
            The deserialized data
        """
        return self._data

    def pre_load(self) -> None:
        """Before loading data, perform actions, like setting a default, if needed.

        Raises
        ------
        FileChanged
            Raised if the source file has been updated since the data was loaded from
            it, and there are unsaved changes. Reloading at this point would overwrite
            the changes made by the user to self.data.
        """
        if not hasattr(self, "_data"):
            self._data = self.default_data()

        if self.is_file_newer and self.is_unsaved:
            raise FileChanged(
                f"The file '{self.path}' is newer than the data, but there are "
                f"unsaved changes in the data"
            )

    def post_load(self) -> None:
        """After successfully loading data, perform actions, like resetting the
        hash and mtime.

        """
        self.reset_hash()
        self.reset_mtime()

    def load(self) -> None:
        """Load and return the data (self._data) or return a default data instance,
        if the data cannot be loaded from a file.

        Raises
        ------
        FileChanged
            Raised if the source file has been updated since the data was loaded from
            it, and there are unsaved changes. Reloading at this point would overwrite
            the changes made by the user to self.data.
        """
        # Perform check
        self.pre_load()

        if self.path is not None:
            if self.encoding == "bytes":
                contents_bytes: bytes = self.path.read_bytes()
                self._data = self.deserialize(contents_bytes)
            else:
                contents_str = self.path.read_text(encoding=self.encoding)
                self._data = self.deserialize(contents_str)
        else:
            logger.info(
                f"Could not load '{self.__class__.__name__}' because path is None"
            )

        # Reset flags
        self.post_load()

    def pre_save(self, overwrite: bool = False) -> None:
        """Before saving data, perform actions like checking whether a path exists
        and whether.

        Parameters
        ----------
        overwrite
            Whether to overwrite unsaved changes

        Raises
        ------
        MissingPath
            Raised if trying to save but the path could not be found.
        UnsavedChanges
            Raised if the destination file exists and its contents are newer
            than those in this entry's data.
        """
        if getattr(self, "path", None) is None:
            raise MissingPath(
                f"Could not save entry of type "
                f"'{self.__class__.__name__}' because no path is specified."
            )
        if not overwrite and hasattr(self, "_data") and self.is_stale:
            raise FileChanged(f"Cannot overwrite the file at path '{self.path}'")

    def post_save(self) -> None:
        """After successfully saving data, perform actions like resetting the cached
        hash and stored mtime"""
        self.reset_hash()
        self.reset_mtime()

    def save(self, overwrite: bool = False) -> None:
        """Save the data to self.path.

        Parameters
        ----------
        overwrite
            Whether to overwrite unsaved changes

        Raises
        ------
        MissingPath
            Raised if trying to save but the path could not be found.
        UnsavedChanges
            Raised if the destination file exists and its contents are newer
            than those in this entry's data.
        """
        # Perform checks and raise exceptions
        self.pre_save(overwrite=overwrite)  # type: ignore[misc]

        # Save the data
        if self.is_unsaved and self.path is not None:
            serialized = self.serialize(self._data)
            if self.encoding == "bytes" and isinstance(serialized, Buffer):
                self.path.write_bytes(serialized)
            elif isinstance(serialized, str):
                self.path.write_text(serialized, encoding=self.encoding)
            else:
                raise NotImplementedError

        # Resets flags
        self.post_save()
