"""
Models and views for projects and project items
"""

import typing as t
from pathlib import Path

from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QListView
from loguru import logger


__all__ = ("ProjectsModel", "ProjectsView", "Entry")


class AbstractEntry(QStandardItem):
    """An abstract project entry"""

    def __repr__(self) -> str:
        return ""


class FileEntry(AbstractEntry):
    """A file project entry"""

    #: The path of the file
    path: Path

    def __init__(self, path):
        super().__init__()
        self.path = path

    def __repr__(self) -> str:
        return str(self.path)


class ProjectsModel(QAbstractListModel):
    """Model for project entries"""

    # A list of project entries with name (key) and entry (value)
    entries = t.List[AbstractEntry]

    def __init__(self):
        super().__init__()
        self.entries = []

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
            return repr(self.entries[index.row()])
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
        existing_paths = {e.path for e in self.entries if isinstance(e, FileEntry)}
        new_paths = [
            FileEntry(p) for p in paths if p.is_file() and p not in existing_paths
        ]

        logger.debug(f"Adding {','.join([str(p) for p in new_paths])}")

        # Append the files
        start_row = self.index(len(self.entries))
        self.entries += new_paths
        end_row = self.index(len(self.entries) + len(new_paths))

        # emit signal
        self.dataChanged.emit(start_row, end_row)
        return len(new_paths)


class ProjectsView(QListView):
    """Tree view for projects"""
