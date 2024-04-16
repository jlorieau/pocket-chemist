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

    @classmethod
    def is_type(
        cls, path: Path, hint: HintType = None, loader: t.Optional[yaml.Loader] = None
    ) -> bool:
        """Overrides TextEntry parent class method to test whether a path or hint
        points to a YAML file.

        Parameters
        ----------
        path
            The path whose file should be tested whether it matches this type.
            This is only checked to retrieve a hint, if one isn't given.
        hint
            The optional hint from the path to be used in the determination.
        loader
            The YAML loader to use in parsing the hint.

        Returns
        -------
        is_type
            True, if the file can be loaded as this Entry's type
        """
        hint = hint if hint is not None else cls.get_hint(path)
        loader = loader if loader is not None else cls.get_loader()
        # Yaml has to be text strings--not binary
        if not isinstance(hint, str):
            return False

        # Remove the last line of the hint
        block = "\n".join(hint.splitlines()[:-1])  #
        # Try parsing this block into an OrderedDict
        try:
            data = yaml.load(block, Loader=loader)
        except yaml.constructor.ConstructorError as e:
            return False

        return (
            True
            if isinstance(data, t.Mapping)  # May be a mapping, like a dict
            or isinstance(data, t.Iterable)  # May be an iterable, like a list
            or isinstance(data, Entry)  # A Project entry may be produced
            else False
        )

    @classmethod
    def get_loader(cls, *args, **kwargs) -> yaml.BaseLoader:
        """Retrieve the loader to deserialize YAML"""
        return yaml.SafeLoader

    @classmethod
    def get_dumper(cls, *args, **kwargs) -> yaml.BaseDumper:
        """Retrieve the dumper to serialize YAML"""
        return yaml.SafeDumper

    @property
    def data(self) -> YamlType:
        """Overrides parent class method to return the file's formatted contents"""
        # Read in the data, if needed
        if not self._data and self.path:
            with open(self.path, "r") as f:
                data = yaml.load(f, Loader=self.get_loader())

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
        """Overrides the Entry parent method to save the yaml data to self.path"""
        Entry.save(self)  # Check whether a save can be conducted

        data = data if data is not None else self.data

        if self.is_unsaved and data:
            with open(self.path, "w") as f:
                f.write(yaml.dump(data, Dumper=self.get_dumper()))
            self.reset_hash()
