"""An entry for text files"""

import typing as t
from pathlib import Path

from .entry import Entry, HintType

__all__ = ("TextEntry",)


class TextEntry(Entry[str]):
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

    def default_data(self):
        return ""

    def load(self, *args, **kwargs):
        """Extends the Entry parent method to load text data"""
        super().pre_load()

        if self.path is not None:
            self._data = self.path.read_text()  # load the data

        super().post_load(*args, **kwargs)

    def save(self, overwrite: bool = False, *args, **kwargs):
        """Extends the Entry parent method to save text data to self.path"""
        self.pre_save(overwrite=overwrite, *args, **kwargs)

        # Save the data
        if self.is_unsaved and self.path is not None:
            self.path.write_text(self._data)  # save the data

        self.post_save(*args, **kwargs)
