"""
A project containing data entries
"""

import typing as t
from weakref import ref
from pathlib import Path
from dataclasses import dataclass
from collections import OrderedDict

from loguru import logger

from .entry import Entry, HintType

__all__ = ("Project",)


class ProjectException(Exception):
    """Exception raised while processing a project"""


EntriesType = t.OrderedDict[str, Entry]


@dataclass(init=False)
class Project(Entry):
    """A project containin data entries"""

    #: All of the currently opened projects
    _opened_projects = []

    #: A list of data entries in this project
    entries: EntriesType

    def __init__(self, *args, entries: t.Optional[EntriesType] = None, **kwargs):
        super().__init__(*args, **kwargs)

        # Add self as a weakref to the listing opened projects
        Project._opened_projects.append(ref(self))

        # Set the attributes
        self.entries = OrderedDict()
        if entries is not None:
            self.entries.update(entries)

    @classmethod
    def is_type(cls, path: Path, hint: HintType = None) -> bool:
        """Override parent class method"""
        return False

    @classmethod
    def opened(cls) -> t.List["Project"]:
        """Return a listing of opened projects"""
        projects = [p() for p in cls._opened_projects]
        return [p for p in projects if p is not None]  # Remove invalid weakrefs

    def assign_unique_names(self):
        """Assign unique names to this project's entries."""
        # Find all of the absolute paths of entries
        parts = [
            entry.path.parent.absolute().parts
            for entry in self.entries.values()
            if getattr(entry, "path", None) is not None
        ]
        parts_t = map(set, zip(*parts))  # transpose

        # Find up to which part the paths are all common
        common_parts = []
        for s in parts_t:
            if len(s) > 1:
                break
            common_parts.append(s.pop())

        # Find the names from the common parts
        common_path = Path(*common_parts) if len(common_parts) > 1 else None
        current_entries = list(self.entries.values())
        self.entries.clear()

        for i, entry in enumerate(current_entries, 1):

            # Create a name from the common_path, if possible, or create a dummy
            # unknown name
            if not hasattr(entry, "path") or entry.path is None:
                name = f"unknown ({i})"
            elif common_path is not None:
                name = entry.path.relative_to(common_path)
            else:
                name = entry.path

            self.entries[str(name)] = entry
