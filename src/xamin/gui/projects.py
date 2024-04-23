"""
Models and views for projects and project items
"""

import typing as t
from pathlib import Path
from dataclasses import dataclass

from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QListView
from loguru import logger


__all__ = ("ProjectsModel", "ProjectsView", "Entry")


@dataclass
class AbstractEntry(QStandardItem):
    """An abstract project entry"""

    #: The name representation in the project listing widget
    name: str

    def __repr__(self) -> str:
        return ""


class FileEntry(AbstractEntry):
    """A file project entry"""

    #: The path of the file
    path: Path

    def __init__(self, name, path):
        super().__init__(name)
        self.path = path

    def __repr__(self) -> str:
        return str(self.path)


class ProjectsModel(QAbstractListModel):
    """Model for project entries"""

    # A list of project entries with name (key) and entry (value)
    entries = t.List[AbstractEntry]

    def __init__(self, entries: t.Optional[t.List[AbstractEntry]] = None):
        super().__init__()
        self.entries = [] if entries is None else entries

    def insertRows(self, row, count, parent=QModelIndex()) -> bool:
        """Insert rows into the model's data"""
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.entries[row:row] = [
            AbstractEntry() for i in range(count)
        ]  # Add dummy data
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent=QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.entries[row : row + count]
        self.endRemoveRows()
        return True

    def rowCount(self, parent: QModelIndex):
        """The number of entries"""
        return len(self.entries)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return the data for the given index"""
        # Check for valid values
        if not index.isValid() or index.row() > len(self.entries):
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self.entries[index.row()].name
        return None

    def setData(
        self, index: QModelIndex, value: AbstractEntry, role=Qt.ItemDataRole.EditRole
    ) -> bool:
        """Modify the project entries data"""
        if not index.isValid() or role != Qt.EditRole:
            return False

        self.entries[index.row()] = value
        self.dataChanged.emit(index, index)
        return True

    def supportedDropActions(self):
        return Qt.MoveAction

    def append_files(self, *args) -> int:
        """Append new files from the given arguments and return the number of files
        added."""
        # Convert to paths
        paths = [Path(i) for i in args if type(i) in (str, Path)]

        # Find new paths for existing files
        existing_paths = {
            e.path.absolute() for e in self.entries if isinstance(e, FileEntry)
        }
        existing_names = {e.name for e in self.entries}
        file_entries = []

        for p in paths:
            # Skip non-file paths or paths that have already been added
            if not p.is_file() or p.absolute() in existing_paths:
                continue

            # Otherwise create a new FileEntry
            name = self._find_unique_name(p.name, existing_names=existing_names)
            new_entry = FileEntry(name=name, path=p)

            # Add the entry to the new file_entries listing
            file_entries.append(new_entry)

            # Add the entry's name to the existing entry names (to avoid dupes)
            existing_names.add(name)

        if file_entries:
            logger.debug(
                "Adding FileEntries: " + f"{', '.join([str(e) for e in file_entries])}"
            )

        # Append the file entries
        start_row = self.index(len(self.entries))
        self.entries += file_entries
        end_row = self.index(len(self.entries) + len(file_entries))

        # emit signal
        self.dataChanged.emit(start_row, end_row)
        return len(file_entries)

    @staticmethod
    def _find_unique_name(
        name: str, existing_names: t.Iterable[str], prefix: str = " ({number:1})"
    ) -> str:
        """Given a list of existing names produce a name that is unique.

        Examples
        --------
        >>> ProjectsModel._find_unique_name('test', ('one', 'two'))
        'test'
        >>> ProjectsModel._find_unique_name('one', ('one', 'two'))
        'one (2)'
        >>> ProjectsModel._find_unique_name('one', ('one', 'one (2)'))
        'one (3)'
        """
        if name not in existing_names:
            return name

        for num in range(999):
            new_name = name.strip() + prefix.format(number=num)
            if new_name not in existing_names:
                return new_name

        raise AssertionError(f"Could not find a unique name for {name}")


class ProjectsView(QListView):
    """Tree view for projects"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlternatingRowColors(True)
