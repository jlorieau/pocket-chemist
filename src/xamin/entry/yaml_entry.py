"""
An entry for YAML files
"""

import typing as t
from pathlib import Path
from collections.abc import Buffer

import yaml
import yaml.scanner

from .entry import Entry, Hint

__all__ = ("YamlEntry", "YamlType")

YamlType = t.MutableMapping | t.MutableSequence


class YamlEntry(Entry[YamlType]):
    """A YAML file entry in a project"""

    @classmethod
    def is_type(
        cls,
        path: Path,
        hint: Hint | None = None,
        loader: type[yaml.SafeLoader] | None = None,
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
        text = hint.utf_8 if hint is not None else None
        if text is None:
            return False

        # Remove the last line of the hint
        block = "\n".join(text.splitlines()[:-1])

        # Try parsing this block into an OrderedDict
        try:
            data = yaml.load(block, Loader=loader)
        except Exception:
            return False

        return (
            True
            if isinstance(data, t.Mapping)  # May be a mapping, like a dict
            or isinstance(data, list)  # May be a list or tuple
            or isinstance(data, tuple)
            or isinstance(data, Entry)  # A Project entry may be produced
            else False
        )

    @classmethod
    def get_loader(cls, *args, **kwargs) -> type[yaml.SafeLoader]:
        """Retrieve the loader to deserialize YAML"""
        return yaml.SafeLoader

    @classmethod
    def get_dumper(cls, *args, **kwargs) -> type[yaml.SafeDumper]:
        """Retrieve the dumper to serialize YAML"""
        return yaml.SafeDumper

    @property
    def shape(self) -> tuple[int] | tuple:
        """Override parent method to give shape (size) of root tree"""
        data = self.data
        if hasattr(data, "__len__"):
            return (len(data),)
        else:
            return ()

    def default_data(self):
        return dict()

    def serialize(self, data: t.Sequence | t.Mapping | "YamlEntry") -> Buffer | str:
        """Overrides parent's (Entry) serialize implementation.

        The YamlEntry data option can only be used if a yaml representer was created
        for the YamlEntry type.
        """
        dumper = self.get_dumper()
        return yaml.dump(data, Dumper=dumper)

    def deserialize(self, serialized: Buffer | str) -> YamlType:
        """Overrides parent's (Entry) serialize implementation

        The serialized option may require a yaml constructor if a YamlEntry type
        was serialized. (see :meth:`serialize`)
        """
        loader = self.get_loader()
        serialized = t.cast(str | bytes, serialized)  # Cast to work with yaml.load
        return yaml.load(serialized, Loader=loader)
