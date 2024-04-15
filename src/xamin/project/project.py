"""
A project containing data entries
"""

import typing as t
import re
from weakref import ref
from pathlib import Path, PosixPath, WindowsPath
from collections import OrderedDict
from os import path

import yaml
from loguru import logger
from thatway import Setting

from .entry import Entry, HintType
from .yaml_entry import YamlEntry
from ..utils.dict import recursive_update
from ..utils.path import is_root
from .. import __version__

__all__ = ("Project", "get_dumper", "get_loader")


# Types of entries that can be added to a project
EntryAddedType = t.Union[Entry, t.Iterable[Entry], t.OrderedDict[str, Entry]]


class Project(YamlEntry):
    """A project containin data entries"""

    # Settings
    default_name = Setting(
        "<unsaved> ({num})",
        desc="Default name pattern to use for entries without a path",
    )

    #: All of the currently opened projects
    _opened_projects = []

    #: A dict of data entries in this project. The following fields (keys) are included:
    #:   - metadata: The project's metadata
    #:   - files: The file entries that are part of the project
    _data: t.OrderedDict[str, t.Union[Entry, t.OrderedDict]]

    def __init__(self, *args, entries: EntryAddedType = (), **kwargs):
        # Populate an empty path, if a path wasn't specified
        if len(args) == 0 and "path" not in kwargs:
            super().__init__(path=None, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)

        # Add self as a weakref to the listing opened projects.
        Project._opened_projects.append(ref(self))

        # Set the attributes
        self.meta["version"] = __version__

        # populate initial entries
        self.add_entries(entries)

    @property
    def _dumper(self) -> yaml.Dumper:
        """The YAML dumper to use for Project entries"""
        if getattr(self, "path", None) is not None:
            current_path = self.path.parent
        else:
            current_path = Path.cwd()
        return get_dumper(rel_path=current_path)

    @property
    def _loader(self) -> yaml.Loader:
        """The YAML loader to use for Project entries"""
        return get_loader()

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Override parent class method"""
        hint = hint if hint is not None else cls.get_hint(path)

        # Check that it matche's the parent's entry type
        if not super().is_type(path, hint):
            return False

        # A project file should always start with a "meta" entry and a "version"
        # subentry. e.g.
        # meta:
        #   version: 0.6.3
        stripped = re.sub(r"#.*", "", hint)  # Remove comments
        return re.match(r"\s*meta\:\s*version\:", stripped, re.MULTILINE) is not None

    @classmethod
    def opened(cls) -> t.List["Project"]:
        """Return a listing of opened projects"""
        projects = [p() for p in cls._opened_projects]
        return [p for p in projects if p is not None]  # Remove invalid weakrefs

    @property
    def data(self) -> t.OrderedDict:
        """The data dict for the project"""
        if getattr(self, "_data", None) is None:
            self._data = OrderedDict()
        return self._data

    @property
    def meta(self) -> t.OrderedDict:
        """The metadata dict for the project"""
        return self.data.setdefault("meta", OrderedDict())

    @property
    def entries(self) -> t.OrderedDict:
        """The Entry instances for the project"""
        return self.data.setdefault("entries", OrderedDict())

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

    def save(self, data=None):
        """Overrides the YamlEntry parent method to save the yaml data to self.path"""
        # Instead of encoding self._data, encode the project entry itself, which
        # has a special yaml representer (see below)
        return super().save(data=self)


## YAML constructors and representers for YAML loaders and dumpers


def constructor_factory(entry_cls: t.Type[Entry]):
    """A YAML deserializer (loader) function factor to create Entry instances"""

    def constructor(
        loader: yaml.SafeLoader, node: yaml.nodes.MappingNode
    ) -> t.Type[Entry]:
        # Process the arguments (deep parses sub-elements)
        mapping = loader.construct_mapping(node, deep=True)

        # Convert path parts into a path object (if available)
        mapping["path"] = Path(*mapping["path"]) if "path" in mapping else None

        # Create the entry instance
        return entry_cls(**mapping)

    constructor.__doc__ = representer_factory.__doc__.replace(
        "Entry", entry_cls.__name__
    )
    return constructor


def representer_factory(entry_cls: t.Type[Entry], rel_path: Path):
    """A YAML serializer (data dumper) function factory for Entry instances."""

    def representer(dumper: yaml.SafeDumper, entry: Entry) -> yaml.nodes.MappingNode:
        # Format the path.
        if getattr(entry, "path", None) is None:
            # No path specified for the entry.
            path = None
        else:
            try:
                # Try to get the relative path, if possible.
                path = entry.path.relative_to(rel_path)
            except ValueError:
                # Otherwise just use the absolute path
                path = entry.path.absolute()

        return dumper.represent_mapping(
            f"!{entry_cls.__name__}",
            {"path": path.parts},
        )

    representer.__doc__ = representer_factory.__doc__.replace(
        "Entry", entry_cls.__name__
    )
    return representer


def project_representer(
    dumper: yaml.SafeDumper, entry: Project
) -> yaml.nodes.MappingNode:
    """A YAML representer for Project entries"""

    return dumper.represent_mapping(
        f"!Project",
        (
            # Preserve the ordering of items rather than return an unordered dict
            ("meta", tuple((k, v) for k, v in entry.meta.items())),
            ("entries", tuple((k, v) for k, v in entry.entries.items())),
        ),
    )


def path_representer(dumper: yaml.SafeDumper, path: Path) -> yaml.nodes.MappingNode:
    """A YAML representer for pathlib.Path objects"""
    return dumper.represent_list(path.parts)


## YAML loader and dumper


def get_loader():
    """Add constructors to a YAML deserializer (loader)"""
    safe_loader = yaml.SafeLoader

    # Use the constructor_factor to create entry constructors
    for _, entry_cls in Entry.subclasses():
        safe_loader.add_constructor(
            f"!{entry_cls.__name__}", constructor_factory(entry_cls)
        )

    return safe_loader


def get_dumper(rel_path: Path):
    """Add representers to a YAML serializer (dumper)"""
    safe_dumper = yaml.SafeDumper

    # Add a modified representer for projects
    safe_dumper.add_representer(Project, project_representer)

    # Use the representer_factory to create entry representers
    for _, entry_cls in Entry.subclasses():
        if entry_cls == Project:
            continue
        safe_dumper.add_representer(entry_cls, representer_factory(entry_cls, rel_path))

    # Add a representer for pathlib.Path objects
    for cls in (Path, PosixPath, WindowsPath):
        safe_dumper.add_representer(cls, path_representer)
    return safe_dumper
