"""
An entry for CSV files
"""

import typing as t
import csv
from pathlib import Path
from io import StringIO
from collections.abc import Buffer

from thatway import Setting

from .entry import Entry, Hint


__all__ = ("CsvEntry",)


class CsvEntry(Entry[list]):
    """A csv/tsv file entry in a project"""

    #: Customizable settings
    default_delimiters: t.ClassVar[Setting] = Setting(
        ",\t", desc="The default delimiters to search"
    )

    #: The cached CSV dialect
    _dialect: type[csv.Dialect] | None = None

    @classmethod
    def is_type(cls, path: Path | None, hint: Hint | None = None) -> bool:
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
    def get_dialect(
        cls, path: Path | None, hint: Hint | None = None
    ) -> type[csv.Dialect]:
        """Retrieve the dialect for the csv file"""
        hint = cls.get_hint(path=path) if hint is None else hint
        if hint is not None and hint.utf_8 is not None:
            return csv.Sniffer().sniff(hint.utf_8, delimiters=cls.default_delimiters)
        else:
            raise NotImplementedError

    @property
    def shape(self) -> t.Tuple[int, int] | tuple:
        """Override parent method to give 2d shape in rows, columns"""
        data = self.data
        if hasattr(data, "__len__") and len(data) > 0:
            return (len(data), len(data[0]))
        else:
            return ()

    def default_data(self) -> list:
        return []

    def serialize(self, data: list) -> Buffer | str:
        """Overrides parent's (Entry) serialize implementation"""
        dialect = getattr(self, "_dialect", "excel")

        # serialize the data
        stream = StringIO()
        writer = csv.writer(stream, dialect=dialect)
        writer.writerows(data)  # bypass loading mechanism
        return stream.read()

    def deserialize(self, serialized: Buffer | str) -> list:
        """Overrides parent's (Entry) deserialize implementation"""
        # load the dialect
        self._dialect = self.get_dialect(path=self.path)

        # load the data
        return list(csv.reader(str(serialized), dialect=self._dialect))
