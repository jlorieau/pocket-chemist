"""
An entry for CSV files
"""

import typing as t
import csv
from pathlib import Path
from io import StringIO

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

    def serialize(self, data: Entry | None) -> str | bytes:
        dialect = getattr(self, "_dialect", "excel")

        # serialize the data
        stream = StringIO()
        writer = csv.writer(stream, dialect=dialect)
        writer.writerows(data)  # bypass loading mechanism
        return stream.read()

    def deserialize(self, serialized: str | bytes) -> t.List | Entry:
        # load the dialect
        self._dialect = self.get_dialect(path=self.path)

        # load the data
        return list(csv.reader(serialized, dialect=self._dialect))
