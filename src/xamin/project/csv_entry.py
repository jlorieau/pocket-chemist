"""
An entry for CSV files
"""

import typing as t
import csv
from pathlib import Path

from thatway import Setting
from loguru import logger

from .entry import Entry, TextEntry, HintType


__all__ = ("CsvEntry",)


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
