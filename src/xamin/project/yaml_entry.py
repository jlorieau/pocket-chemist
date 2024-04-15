"""
An entry for YAML files
"""

import typing as t
import yaml
from pathlib import Path
from collections import OrderedDict

from .entry import Entry, TextEntry, HintType

__all__ = ("YamlEntry", "YamlType")

YamlType = t.Union[t.List, t.OrderedDict]


class YamlEntry(TextEntry):
    """A YAML file entry in a project"""

    # Locally cached data
    _data: YamlType

    # The YAML loader and dumper to use for the YAMLEntry
    _loader = yaml.SafeLoader
    _dumper = yaml.SafeDumper

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Overrides  parent class method to test whether path is a CsvEntry."""
        hint = hint if hint is not None else cls.get_hint(path)

        # Remove the last line of the hint
        block = "\n".join(hint.splitlines()[:-1])  #

        # Try parsing this block into an OrderedDict
        data = yaml.safe_load(block)
        return True if isinstance(data, dict) or isinstance(data, list) else False

    @property
    def data(self) -> YamlType:
        """Overrides parent class method to return the file's formatted contents"""
        # Read in the data, if needed
        if not self._data and self.path:
            with open(self.path, "r") as f:
                data = yaml.load(f, Loader=self._loader)

                if isinstance(data, dict):
                    self._data = OrderedDict(data)
                elif isinstance(data, list):
                    self._data = data
                else:
                    pass
        return super().data

    @data.setter
    def data(self, value):
        """Overrides parent data setter.

        Raises
        ------
        TypeError
            If the given value isn't DictType string.
        """
        if not isinstance(value, YamlType):
            raise TypeError(f"Expected '{YamlType}' value type")
        self._data = value

    @property
    def shape(self) -> t.Tuple[int]:
        """Override parent method to give shape (size) of root tree"""
        data = self.data
        if hasattr(data, "__len__"):
            return (len(data),)
        else:
            return ()

    def save(self, data=None):
        """Overrides the Entry parent method to save the text data to self.path"""
        Entry.save(self)  # Check whether a save can be conducted

        data = data if data is not None else self.data
        if self.is_unsaved and data:
            with open(self.path, "w") as f:
                f.write(yaml.dump(data, Dumper=self._dumper))
            self.reset_hash()
