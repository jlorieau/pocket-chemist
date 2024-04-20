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
from ..utils.dict import tuple_to_dict, recursive_update
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

    @classmethod
    def is_type(
        cls, path: Path, hint: HintType = None, loader: t.Optional[yaml.Loader] = None
    ) -> bool:
        """Overrides YamlEntry parent class method to use a custom loader for project
        entries."""
        hint = hint if hint is not None else cls.get_hint(path)
        loader = cls.get_loader()

        # Check that it matche's the parent's entry type
        if not super().is_type(path, hint=hint, loader=loader):
            return False

        # A project file should always start with a "!Project" tag followed by
        # "meta" entry
        # subentry. e.g.
        # !Project
        # meta:
        stripped = re.sub(r"#.*", "", hint)  # Remove comments
        return stripped.startswith("!Project\nmeta:")

    @classmethod
    def get_loader(cls, *args, **kwargs) -> yaml.BaseLoader:
        """Retrieve the loader to deserialize YAML"""
        loader = super().get_loader(*args, **kwargs)

        # Add custom constructors to loader (see below)
        loader.add_constructor("!path", path_constructor)
        loader.add_constructor("!Project", project_constructor)

        return loader

    @classmethod
    def get_dumper(cls, *args, **kwargs) -> yaml.BaseDumper:
        """Retrieve the dumper to serialize YAML"""
        dumper = super().get_dumper(*args, **kwargs)

        # Add custom representers to loader (see below)
        dumper.add_representer(PosixPath, path_representer)  # Needed for paths
        dumper.add_representer(WindowsPath, path_representer)  # Needed for paths
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

    def post_load(self):
        """Extends the Entry.post_load method to set sub-entries to absolute paths"""
        # Make sure that the entries paths are absolute so that files can be found
        try:
            self.to_absolute_paths()
        except ValueError:
            logger.error(
                f"Project '{self}' unable to convert entries path to absolute paths"
            )
        return super().post_load()

    def load(self, *args, **kwargs):
        """Overrides parent's load method to load the deserialized data to
        'self' instead of 'self._data'."""
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

    def pre_save(self, *args, **kwargs):
        """Extends the Entry.pre_save method to set sub-entries to relative paths"""
        # Set to relative paths before save in case the project and sub-entry files
        # are moved to a new directory on a new computer
        try:
            self.to_relative_paths()
        except ValueError:
            logger.error(
                f"Project '{self}' unable to convert entries path to relative paths"
            )
        return super().pre_save(*args, **kwargs)

    def save(self, overwrite: bool = False, *args, **kwargs):
        """Overrides parent's save method to save the serialized 'self' instead of
        'self._data'."""
        # Perform checks and raise exceptions
        self.pre_save(overwrite=overwrite, *args, **kwargs)

        # Save the data
        if self.is_unsaved and self.path is not None:
            serialized_self = self.serialize(self)
            self.path.write_text(serialized_self, encoding=self.encoding)

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

    def to_absolute_paths(self):
        """Set the paths of entries to absolute paths

        (reverse of to_absolute_paths)

        Raises
        ------
        ValueError
            Raised if a absolute path cannot be determined
        """
        # Retrieve the project parent directory. A project path is needed to calculate
        # absolute paths
        if self.path is None:
            return
        project_parent = self.path.parent

        # Get entries directly to avoid triggering a load
        entries = getattr(self, "_data", dict()).get("entries", dict())

        # Retrieve the paths of entries and convert them to absolute paths
        paths = []
        for entry in entries.values():

            if entry.path is None:
                # If the entry does not have a path, there's nothing that can be done
                paths.append(None)

            # Only convert paths that aren't already absolute
            elif not entry.path.is_absolute():
                # Convert paths to absolute paths by pre-pending the project's parent
                path = project_parent / entry.path
                paths.append(path)

            else:
                # Add the path unmodified
                paths.append(entry.path)

            # See if the entry has a 'to_absolute_paths'--i.e. it's a Project
            if hasattr(entry, "to_absolute_paths"):
                entry.to_absolute_paths()

        # Atomically replace the paths
        for entry, path in zip(entries.values(), paths):
            if path is None:
                continue
            entry.path = path

    def to_relative_paths(self, walk_up: bool = False):
        """Set the paths of entries as relative paths to the project's path

        (reverse of to_relative_paths)

        Parameters
        ----------
        walk_up
            When walk_up is False (the default), the path must start with other.
            When the argument is True, .. entries may be added to form the relative
            path (see: https://docs.python.org/3/library/pathlib.html)

        Raises
        ------
        ValueError
            Raised if a relative path cannot be determined
        """
        # Retrieve the project parent directory. A project path is needed to calculate
        # relative paths.
        if self.path is None:
            return
        project_parent = self.path.parent

        # Get entries directly to avoid triggering a load
        entries = getattr(self, "_data", dict()).get("entries", dict())

        # Retrieve the paths of entries and convert them to relative paths
        paths = []
        for entry in entries.values():

            if entry.path is None:
                # If the entry does not have a path, there's nothing that can be done
                paths.append(None)

            # Only convert paths that are absolute paths
            elif entry.path.is_absolute():
                # Convert paths to absolute paths by pre-pending the project's parent
                path = entry.path.relative_to(project_parent, walk_up=walk_up)
                paths.append(path)

            else:
                # Add the path unmodified
                paths.append(entry.path)

            # See if the entry has a 'to_relative_paths'--i.e. it's a Project
            if hasattr(entry, "to_relative_paths"):
                entry.to_relative_paths(walk_up=walk_up)

        # Atomically replace the paths
        for entry, path in zip(entries.values(), paths):
            if path is None:
                continue
            entry.path = path

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


## YAML constructors and representers for YAML loaders and dumpers


def path_representer(dumper: yaml.BaseDumper, path: Path):
    """Serializer (dumper) from yaml to a pathlib Path"""
    return (
        dumper.represent_sequence(f"!path", list(path.parts))
        if path is not None
        else None
    )


def path_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a pathlib Path from yaml"""
    sequence = loader.construct_sequence(node, deep=True)
    return Path(*sequence) if sequence is not None else None


def project_representer(dumper: yaml.BaseDumper, project: Project):
    """Deserializer (loader) for a Project from yaml

    Note: Access project._data instead of project.data/project.meta/project.entries
    to avoid triggering a load. The file that is being save to is touched by the
    parent's save method.

    Parameters
    ----------
    dumper
        The YAML dumper class to use to produce the YAML representation
    project
        The project entry instance to represent in YAML
    """

    def project_mapping(project: Project) -> t.Tuple:
        """Convert a project and its entries into and python mapping that can be
        converted to a YAML mapping"""
        # Get the project data directly rather than from the data/meta/entries methods
        # This avoids a check to see if the data is stale and a possible re-load of
        # the data on save
        project_data = getattr(project, "_data", OrderedDict())
        project_meta = project_data.get("meta", OrderedDict())
        project_entries = project_data.get("entries", OrderedDict())

        # Prepare a list of tuples for the entries
        entries = []

        for name, entry in project_entries.items():
            # Get the state dict and other useful info
            state = entry.__getstate__()
            cls_name = entry.__class__.__name__

            # Create a mapping of the state
            if isinstance(entry, Project):
                r = (name, (f"!{cls_name}", project_mapping(entry)))
            else:
                r = (name, (f"!{cls_name}", tuple(state.items())))

            entries.append(r)

        # Prepare the mapping as a list of (key, value) 2-ples
        return (
            f"!{project.__class__.__name__}",
            (
                ("meta", tuple((k, v) for k, v in project_meta.items())),
                ("path", project.path),
                ("entries", tuple(entries)),
            ),
        )

    # Create a function that pull out python types and can be used recursively
    return dumper.represent_mapping(*project_mapping(project))


def project_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a Project from yaml

    Parameters
    ----------
    loader
        The YAML loader class to use to produce the YAML representation
    node
        The YAML node to convert to a project
    """

    # Get all the entry subclasses
    sub_classes = {("!" + cls.__name__): cls for _, cls in Entry.subclasses()}

    def construct_project(mapping: t.OrderedDict):
        """Takes a project mapping and populates all the fields"""
        entries_list = mapping.pop("entries", dict())

        entries = OrderedDict()
        for name, value in entries_list.items():
            # The 'value' created by project_representer should create an ordered
            # dict with the entry's class name as the key and the entry's data as the
            # value.
            if not isinstance(value, t.Mapping) or len(value) != 1:
                logger.error(f"Could not parse the entry value: {value}")
                continue

            cls_name, data = value.popitem()

            if cls_name == "!Project":
                # Use this function recursively
                entry = construct_project(value)

            elif cls_name in sub_classes:
                # Re-create the entry class
                cls = sub_classes[cls_name]
                path = data.pop("path", None)

                entry = cls(path=path)
                entry.__dict__.update(data)

            else:
                logger.error(
                    f"Could not find entry class '{cls_name}' with value '{data}'"
                )
                continue

            entries[name] = entry

        # Retrieve the remaining project data
        meta = mapping.pop("meta", dict())
        path = mapping.pop("path", None)

        # Reconstruct the project
        project = Project(path=None)

        project.meta.update(meta)
        project.entries.update(entries)

        # Set path after creating the project so that accessing project.data (through
        # project.meta and project.entries) does not trigger a recursive reload of
        # the project
        project.path = path
        return project

    mapping = loader.construct_mapping(node, deep=True)
    mapping = tuple_to_dict(mapping)  # Convert tree of tuples to tree of OrderedDict
    return construct_project(mapping)
