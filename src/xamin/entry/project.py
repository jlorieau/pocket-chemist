"""
A project containing data entries
"""

import typing as t
import re
from pathlib import Path, PosixPath, WindowsPath
from collections import OrderedDict
from os import path
from copy import deepcopy

import yaml
from loguru import logger
from thatway import Setting

from .entry import Entry, Hint
from .yaml_entry import YamlEntry
from ..utils.path import is_root
from .. import __version__

__all__ = ("Project",)


# Types of entries that can be added to a project
EntryAddedType = t.Union[Entry, t.Iterable[Entry], t.OrderedDict[str, Entry]]


class Project(YamlEntry):
    """A project containin data entries"""

    # Settings
    default_name = Setting(
        "<unsaved> ({num})",
        desc="Default name pattern to use for entries without a path",
    )

    #: A dict of data entries in this project. The following fields (keys) are included:
    #:   - metadata: The project's metadata
    #:   - files: The file entries that are part of the project
    _data: t.OrderedDict[str, t.Union[Entry, t.OrderedDict]]

    def __init__(self, *args, entries: EntryAddedType = (), **kwargs):
        super().__init__(*args, **kwargs)

        # Load default entries for meta and entries
        self.meta
        self.entries

        # populate initial entries
        self.add_entries(entries)

    def __repr__(self):
        """The string representation for this class"""
        cls_name = self.__class__.__name__
        name = f"'{self.path}'" if self.path is not None else "None"

        # Retrieve the meta dict directly and bypass data to avoid triggering a load
        entries = getattr(self, "_data", dict()).get("entries", dict())
        entries_len = len(entries)
        return f"{cls_name}(path={name}, entries={entries_len})"

    def __getstate__(self) -> t.Dict:
        """Extend parent method (Entry) get state method to include Project data"""
        # Get the paren't initial state
        state = super().__getstate__()

        # Retrieve the Project data that needs to be saved in the state
        data = getattr(self, "_data", dict())
        meta = data.get("meta", OrderedDict())
        entries = data.get("entries", OrderedDict())

        # Find the project.path parent directory
        project_path = self.path.parent if self.path is not None else None

        # Add entries to the state as an OrderedDict
        state["entries"] = state.get("entries", dict())
        state["entries"] = OrderedDict(state["entries"])

        for name, entry in entries.items():
            entry_state = state["entries"].setdefault(name, dict())

            entry_state["class"] = entry.__class__.__name__
            entry_state.update(entry.__getstate__())

            # Convert the entries paths to relative paths, if possible
            try:
                path = entry_state["path"]
                entry_state["path"] = path.relative_to(project_path)
            except (ValueError, KeyError, AttributeError):
                pass

        # Add the data to the state
        state["meta"] = deepcopy(meta)

        return state

    def __setstate__(self, state: t.Dict):
        """Extend parent method (Entry) set state method with Project data"""
        # Run the parent state
        super().__setstate__(state)

        # Retrieve the Project data to be updated with the state
        data = getattr(self, "_data", dict())
        meta = data.get("meta", OrderedDict())
        entries = data.get("entries", OrderedDict())

        # Update the meta data
        meta_state = state.get("meta", OrderedDict())
        meta.update(meta_state)

        # Update the entries data
        entries_state = state.get("entries", OrderedDict())
        subclasses = {cls.__name__: cls for _, cls in self.subclasses()}
        project_path = self.path.parent if self.path is not None else None

        for name, entry_state in entries_state.items():

            if "class" not in entry_state or entry_state["class"] not in subclasses:
                continue
            cls_name = entry_state["class"]
            cls = subclasses[cls_name]

            # Convert the entries paths to relative paths, if possible
            try:
                entry_state["path"] = (project_path / entry_state["path"]).absolute()
            except (KeyError, ValueError, AttributeError, TypeError):
                pass

            entry = cls()
            entry.__setstate__(entry_state)

            entries[name] = entry

    @classmethod
    def is_type(
        cls,
        path: Path,
        hint: Hint | None = None,
        loader: t.Optional[yaml.Loader] = None,
    ) -> bool:
        """Overrides YamlEntry parent class method to use a custom loader for project
        entries."""
        hint = hint if hint is not None else cls.get_hint(path)
        text = hint.utf_8

        # Project files start with a "!Project" tag followed by "meta" entry. e.g.
        # !Project
        # meta:
        if text is not None:
            stripped = re.sub(r"#.*", "", text).strip()  # Remove comments, whitespace
            return re.match("!Project\n\s*(meta|entries):", stripped)
        else:
            return False

    @classmethod
    def get_loader(cls, *args, **kwargs) -> yaml.BaseLoader:
        """Retrieve the loader to deserialize YAML"""
        loader = super().get_loader(*args, **kwargs)

        # Add custom constructors to loader (see below)
        loader.add_constructor("!Path", path_constructor)
        loader.add_constructor("!OrderedDict", odict_constructor)
        loader.add_constructor("!Project", project_constructor)

        return loader

    @classmethod
    def get_dumper(cls, *args, **kwargs) -> yaml.BaseDumper:
        """Retrieve the dumper to serialize YAML"""
        dumper = super().get_dumper(*args, **kwargs)

        # Add custom representers to loader (see below)
        dumper.add_representer(PosixPath, path_representer)  # Needed for paths
        dumper.add_representer(WindowsPath, path_representer)  # Needed for paths
        dumper.add_representer(OrderedDict, odict_representer)
        dumper.add_representer(Project, project_representer)

        return dumper

    def default_data(self):
        items = (
            ("meta", OrderedDict()),
            ("entries", OrderedDict()),
        )
        return OrderedDict(items)

    @property
    def meta(self) -> t.OrderedDict:
        """The metadata dict for the project"""
        meta = self.data["meta"]
        _ = meta.setdefault("version", __version__)  # set version, if needed
        return self.data["meta"]

    @property
    def entries(self) -> t.OrderedDict:
        """The Entry instances for the project"""
        return self.data["entries"]

    def load(self, *args, **kwargs):
        """Overrides parent's load method to load the deserialized data to
        'self' instead of 'self._data'.
        """
        # Perform check
        self.pre_load(*args, **kwargs)

        if self.path is not None:
            contents = self.path.read_text(encoding=self.encoding)

            loaded_project = self.deserialize(contents)

            # Transfer '_data' (with 'meta' and 'entries') to self.
            # Use _data to avoid trigerring a load
            self._data.update(getattr(loaded_project, "_data", OrderedDict()))
            self.path = loaded_project.path

        # Reset flags
        self.post_load(*args, **kwargs)

    def save(self, overwrite: bool = False, *args, **kwargs):
        """Overrides parent's save method to save the serialized 'self' instead of
        'self._data'."""
        try:
            # Perform checks and raise exceptions
            self.pre_save(overwrite=overwrite, *args, **kwargs)

            # Save the data
            if self.is_unsaved and self.path is not None:
                serialized_self = self.serialize(self)
                self.path.write_text(serialized_self, encoding=self.encoding)

        except Exception as e:
            raise e

        finally:
            # Resets flags
            self.post_save(*args, **kwargs)

    def assign_unique_names(self):
        """Assign unique names to this project's entries.

        This function will also remove duplicate entries.
        """
        entries = list(self.entries.values())

        # Find the common path for all entry paths
        paths = [e.path for e in entries if getattr(e, "path", None) is not None]
        try:
            common = Path(path.commonpath(paths))
        except ValueError:
            common = None

        # Clear the current entries so that their names (keys) can be re-assigned
        self.entries.clear()

        # Find the names (dict keys) from the common path
        for num, entry in enumerate(entries, 1):
            # Create a name from the common path, if possible, or create a dummy
            # unknown name
            if getattr(entry, "path", None) is None:
                # No path, give a default name
                name = self.default_name.format(num=num)

            elif common is not None:
                # A common base path was found

                if common.absolute() == entry.path.absolute():
                    # The common path is the same as the entry's path. This happens,
                    # for example, when only 1 entry with a entry.path is available.
                    # In this case, give the filename only.
                    name = entry.path.name
                elif is_root(common):
                    # The common path is the root path, so removing the common
                    # path is not desirable, as it will remove the root from
                    # an absolute path
                    # e.g.: /etc/http.conf -> etc/http.conf
                    name = entry.path

                else:
                    # try to construct the name by removing the common path from
                    # the entry's entry.path
                    try:
                        name = entry.path.absolute().relative_to(
                            common.absolute(), walk_up=True
                        )
                    except ValueError:
                        name = entry.path

            else:
                # Otherwise just use the path as a name
                name = entry.path

            # Name and place the entry in the entries dict
            self.entries[str(name)] = entry

    def add_entries(self, *entries: EntryAddedType):
        """Add entries to a project"""
        for value in entries:
            if isinstance(value, t.Mapping):
                # For OrderDict and other dicts
                self.entries.update(value)

            else:
                # Convert to a tuple, if needed
                if not isinstance(value, t.Iterable):
                    value = (value,)

                # Add each entry from the 'value' iterable
                name = lambda num: str(self.default_name.format(num=num))
                num = 0
                for entry in value:
                    if not isinstance(entry, Entry):
                        continue

                    # Find a unique name
                    while name(num=num) in self.entries:
                        num += 1
                    self.entries[name(num)] = entry

        # Update the project names
        self.assign_unique_names()

    def add_files(self, *paths: t.Tuple[t.Union[str, Path]]):
        """Add files and create new entries to a project"""
        # Find the paths for entries that are already registered
        existing_paths = {
            e.path.absolute()
            for e in self.entries.values()
            if getattr(self, "path", None) is not None
        }

        # Convert the arguments to paths and find only new paths
        paths = [
            Path(a)
            for a in paths
            if (isinstance(a, str) or isinstance(a, Path))
            and Path(a).absolute() not in existing_paths
        ]

        # For each path, find the most specific Entry type (highest hierarchy level),
        # and use it to create an entry
        entries = []
        for path in paths:
            hint = Entry.get_hint(path)  # cache the hint

            cls = Entry.guess_type(path, hint)

            if cls is None:
                logger.error(f"Could not find a file entry type for '{path}'")
                continue

            entries.append(cls(path=path))

        self.add_entries(*entries)


## Utility functions


## YAML constructors and representers for YAML loaders and dumpers


def path_representer(dumper: yaml.BaseDumper, path: Path):
    """Serializer (dumper) from yaml to a pathlib Path"""
    return (
        dumper.represent_sequence(f"!Path", list(path.parts))
        if path is not None
        else None
    )


def path_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a pathlib Path from yaml"""
    sequence = loader.construct_sequence(node, deep=True)
    return Path(*sequence) if sequence is not None else None


def odict_representer(dumper: yaml.BaseDumper, odict: OrderedDict):
    """Serializer (dumper) from yaml to an OrderedDict"""
    return dumper.represent_sequence(f"!OrderedDict", odict.items())


def odict_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a pathlib Path from yaml"""
    sequence = loader.construct_sequence(node, deep=True)
    return OrderedDict(sequence) if sequence is not None else None


def project_representer(dumper: yaml.BaseDumper, project: Project):
    """Deserializer (loader) for a Project from yaml

    Parameters
    ----------
    dumper
        The YAML dumper class to use to produce the YAML representation
    project
        The project entry instance to represent in YAML
    """
    return dumper.represent_mapping(f"!Project", project.__getstate__())


def project_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a Project from yaml

    Parameters
    ----------
    loader
        The YAML loader class to use to produce the YAML representation
    node
        The YAML node to convert to a project
    """
    # Retrieve the state from the node
    state = loader.construct_mapping(node, deep=True)

    # Construct project
    project = Project()
    project.__setstate__(state)
    return project
