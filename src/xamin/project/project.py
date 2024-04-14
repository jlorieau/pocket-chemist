"""
A project containing data entries
"""

import typing as t
import re
from weakref import ref
from pathlib import Path
from collections import OrderedDict
from os import path

from loguru import logger
from thatway import Setting

from .entry import Entry, HintType
from .yaml_entry import YamlEntry
from ..utils.dict import recursive_update
from ..utils.path import is_root
from .. import __version__

__all__ = ("Project",)


class ProjectException(Exception):
    """Exception raised while processing a project"""


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

    def __init__(self, *args, entries: t.Iterable[Entry] = (), **kwargs):
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
        self.add_entries(*entries)

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

    def add_entries(self, *entries: t.Tuple[t.Union[Entry, t.OrderedDict]]):
        """Add entries to a project"""
        for entry in entries:
            # It has to be an entry
            if not isinstance(entry, t.Union[Entry, t.OrderedDict]):
                continue

            if getattr(entry, "path", None) is not None:
                # Use the path as a name, if available
                self.entries[str(entry.path.absolute())] = entry
            else:
                # Otherwise choose a generic name
                num = 0
                while self.default_name.format(num=num) in self.entries:
                    num += 1
                name = self.default_name.format(num=num)
                self.entries[name] = entry

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
        for path in paths:
            hint = Entry.get_hint(path)  # cache the hint

            cls = Entry.guess_type(path, hint)

            if cls is None:
                logger.error(f"Could not find a file entry type for '{path}'")
                continue

            self.entries[str(path.absolute())] = cls(path=path)

        # Update the project names
        self.assign_unique_names()
