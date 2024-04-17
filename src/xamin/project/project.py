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

    def __repr__(self):
        """The string representation for this class"""
        cls_name = self.__class__.__name__
        name = f"'{self.path}'" if self.path is not None else "None"
        entries_len = len(self.entries)
        return f"{cls_name}(path={name}, entries={entries_len})"

    def __eq__(self, other):
        """Test the equivalence of two projects"""
        conditions = (
            super().__eq__(other),  # parent are equal
            self.meta == getattr(other, "meta", None),  # same meta
            self.entries == getattr(other, "entries", None),  # same entries
        )
        return all(conditions)

    def __getstate__(self) -> t.Dict:
        """Get a copy of the current state for serialization"""
        state = super().__getstate__()
        state["meta"] = self.meta
        state["entries"] = self.entries
        return state

    def __setstate__(self, state):
        """Set the state for the entry based on the given state copy"""
        super().__setstate__(state)
        self._data["meta"].update(state.get("meta", OrderedDict()))
        self._data["entries"].update(state.get("entries", OrderedDict()))

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
        dumper.add_representer(Project, project_representer_no_relpath)

        return dumper

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


def project_representer(
    dumper: yaml.BaseDumper, project: Project, use_relpath: bool = True
):
    """Deserializer (loader) for a Project from yaml

    Parameters
    ----------
    dumper
        The YAML dumper class to use to produce the YAML representation
    project
        The project entry instance to represent in YAML
    use_relpath
        If True (default), set the paths of entries relative to the project's parent
        path (director).
        If False, do not change the paths of entries
    """

    def project_mapping(project: Project, relpath: t.Optional[Path] = None) -> t.Tuple:
        """Convert a project and its entries into and python mapping that can be
        converted to a YAML mapping"""
        # Prepare the entries, using the project's path
        if relpath is None:
            relpath = project.path.parent if project.path is not None else None

        # Prepare a list of tuples for the entries
        entries = []
        for name, entry in project.entries.items():
            # Get the state dict and other useful info
            state = entry.__getstate__()
            cls_name = entry.__class__.__name__

            # Convert the path relative to this project's path
            if (
                use_relpath
                and relpath is not None
                and "path" in state
                and isinstance(state["path"], Path)
            ):
                try:
                    state["path"] = state["path"].relative_to(relpath)
                except:
                    pass

            # Create a mapping of the state
            if isinstance(entry, Project):
                r = (name, (f"!{cls_name}", project_mapping(entry, relpath)))
            else:
                r = (name, (f"!{cls_name}", tuple(state.items())))

            entries.append(r)

        # Prepare the mapping as a list of (key, value) 2-ples
        return (
            f"!{project.__class__.__name__}",
            (
                ("meta", tuple((k, v) for k, v in project.meta.items())),
                ("path", project.path),
                ("entries", tuple(entries)),
            ),
        )

    # Create a function that pull out python types and can be used recursively
    return dumper.represent_mapping(*project_mapping(project))


def project_representer_no_relpath(*args, **kwargs):
    """A project_representer that does not change the paths of entries"""
    return project_representer(*args, **kwargs, use_relpath=False)


def project_constructor(loader: yaml.BaseLoader, node):
    """Deserializer (loader) for a Project from yaml"""

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
        project = Project(path=path)
        project.meta.update(meta)
        project.entries.update(entries)
        return project

    mapping = loader.construct_mapping(node, deep=True)
    mapping = tuple_to_dict(mapping)  # Convert tree of tuples to tree of OrderedDict
    return construct_project(mapping)
