"""
A project containing data entries
"""

import typing as t
from weakref import ref
from pathlib import Path

from loguru import logger

from .entry import Entry


class ProjectException(Exception):
    """Exception raised while processing a project"""


class Project:
    """A project containin data entries"""

    #: All of the currently opened projects
    _opened_projects = []

    #: The project name
    name = "default"

    #: A list of data entries in this project
    entries = []

    def __init__(
        self,
        name: t.Optional[str] = None,
        entries: t.Optional[t.List[Entry]] = None,
    ):
        # Add self as a weakref to the listing opened projects
        Project._opened_projects.append(ref(self))

        # Set the attributes
        self.name = name if isinstance(name, str) else self.name
        self.entries = entries if entries is not None else []

    @classmethod
    def opened(cls) -> t.List["Project"]:
        """Return a listing of opened projects"""
        projects = [p() for p in cls._opened_projects]
        return [p for p in projects if p is not None]  # Remove invalid weakrefs

    @staticmethod
    def _find_unique_name(
        name: str, existing_names: t.Iterable[str], suffix: str = " ({number:1})"
    ) -> str:
        """Given a list of existing names produce a name that is unique.

        Examples
        --------
        >>> Project._find_unique_name('test', ('one', 'two'))
        'test'
        >>> Project._find_unique_name('one', ('one', 'two'))
        'one (2)'
        >>> Project._find_unique_name('one', ('one', 'one (2)'))
        'one (3)'
        """
        if name not in existing_names:
            return name

        for number in range(999):
            new_name = name.strip() + suffix.format(number=number)
            if new_name not in existing_names:
                return new_name

        raise AssertionError(f"Could not find a unique name for {name}")

    def append_file_entries(self, *args) -> int:
        """Append new files entries from the given arguments and return the number of files
        added."""
        # Convert to paths
        paths = [Path(i) for i in args if type(i) in (str, Path)]

        # Find new paths for existing files
        existing_paths = {
            e.path.absolute() for e in self.entries if isinstance(e, Entry)
        }
        existing_names = {e.name for e in self.entries}
        file_entries = []

        for p in paths:
            # Skip non-file paths or paths that have already been added
            if not p.is_file() or p.absolute() in existing_paths:
                continue

            # Otherwise create a new FileEntry
            name = self._find_unique_name(p.name, existing_names=existing_names)
            new_entry = Entry(name=name, path=p)

            # Add the entry to the new file_entries listing
            file_entries.append(new_entry)

            # Add the entry's name to the existing entry names (to avoid dupes)
            existing_names.add(name)

        if file_entries:
            logger.debug(
                "Adding FileEntries: " + f"{', '.join([str(e) for e in file_entries])}"
            )

        # Append the file entries
        self.entries += file_entries

        # emit signal
        self.layoutChanged.emit()
        return len(file_entries)
