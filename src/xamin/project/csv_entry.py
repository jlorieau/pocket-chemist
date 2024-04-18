"""
An entry for CSV files
"""

import typing as t
import csv
from pathlib import Path

from thatway import Setting
from loguru import logger

from .entry import Entry, HintType


__all__ = ("CsvEntry",)


class CsvEntry(Entry[t.List]):
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
            dialect = cls.get_dialect(path=path, hint=hint)
            return True if dialect is not None else False
        except:
            return False

    @classmethod
    def get_dialect(cls, path: Path, hint: HintType = None) -> csv.Dialect:
        """Retrieve the dialect for the csv file"""
        hint = cls.get_hint(path=path) if hint is None else hint
        return csv.Sniffer().sniff(hint, delimiters=cls.default_delimiters)

    @property
    def shape(self) -> t.Tuple[int, int]:
        """Override parent method to give 2d shape in rows, columns"""
        data = self.data
        if hasattr(data, "__len__") and len(data) > 0:
            return (len(data), len(data[0]))
        else:
            return ()

    def default_data(self):
        return []

    def load(self, *args, **kwargs):
        """Extends the Entry parent method to load text data"""
        super().pre_load()

        if self.path is not None:
            # load the dialect
            self._dialect = self.get_dialect(path=self.path)

            # load the data
            reader = csv.reader(self.path.open(), dialect=self._dialect)
            self._data = list(reader)

        super().post_load(*args, **kwargs)

    def save(self, overwrite: bool = False, *args, **kwargs):
        """Extends the Entry parent method to save text data to self.path"""
        self.pre_save(overwrite=overwrite, *args, **kwargs)

        if self.is_unsaved and self.path is not None:
            # load the dialect, default to excel csv
            dialect = getattr(self, "_dialect", "excel")

            # Save the data
            writer = csv.writer(self.path.open(mode="w"), dialect=dialect)
            writer.writerows(self._data)  # bypass loading mechanism

        self.post_save(*args, **kwargs)
