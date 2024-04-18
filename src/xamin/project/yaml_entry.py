"""
An entry for YAML files
"""

import typing as t
import yaml
from pathlib import Path

from .entry import Entry, HintType

__all__ = ("YamlEntry", "YamlType")

YamlType = t.Union[t.Sequence, t.Mapping]


class YamlEntry(Entry[YamlType]):
    """A YAML file entry in a project"""

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
            or isinstance(data, t.List)  # May be a list or tuple
            or isinstance(data, t.Tuple)
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
    def shape(self) -> t.Tuple[int]:
        """Override parent method to give shape (size) of root tree"""
        data = self.data
        if hasattr(data, "__len__"):
            return (len(data),)
        else:
            return ()

    def default_data(self):
        return dict()

    def load(self, return_data=False, *args, **kwargs):
        """Extends the Entry parent method to load yaml data.

        Parameters
        ----------
        return_data
            If True, return the loaded data rather than set it to self._data
            If False (default), set the loaded data to self._data
        """
        super().pre_load()

        # load the data
        data = None
        if self.path is not None:
            data = yaml.load(self.path.open(), Loader=self.get_loader())

        if not return_data and data:
            self._data = data

        super().post_load(*args, **kwargs)

        if return_data and data:
            return data

    def save(self, overwrite: bool = False, data=None, *args, **kwargs):
        """Extends the Entry parent method to save yaml data to self.path

        Parameters
        ----------
        overwrite
            Whether to overwrite unsaved changes
        data
            If specified, serialize (dump) the given data instead of self._data.

        Raises
        ------
        MissingPath
            Raised if trying to save but the path could not be found.
        UnsavedChanges
            Raised if the destination file exists and its contents are newer
            than those in this entry's data.
        """
        self.pre_save(overwrite=overwrite, *args, **kwargs)

        # Save the data
        data = data if data is not None else self._data  # bypass self.data load

        if self.is_unsaved and self.path is not None:
            yaml.dump(data, Dumper=self.get_dumper(), stream=self.path.open(mode="w"))

        self.post_save(*args, **kwargs)
