"""An entry for text files"""

import typing as t
from pathlib import Path

from .entry import Entry, HintType

__all__ = ("BinaryEntry",)


class BinaryEntry(Entry[bytes]):
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

    def default_data(self):
        return b""

    def load(self, *args, **kwargs):
        """Extends the Entry parent method to load binary data"""
        super().pre_load()

        if self.path is not None:
            self._data = self.path.read_bytes()  # load the data

        super().post_load(*args, **kwargs)

    def save(self, overwrite: bool = False, *args, **kwargs):
        """Extends the Entry parent method to save binary data to self.path"""
        self.pre_save(overwrite=overwrite, *args, **kwargs)

        # Save the data
        data = self.data
        if self.is_unsaved and self.path is not None:
            self.path.write_bytes(self._data)  # bypass data loading

        self.post_save(*args, **kwargs)
