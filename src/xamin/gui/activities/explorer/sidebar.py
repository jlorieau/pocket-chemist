"""
Sidebar functionality for the FileExplorer activity
"""

import typing as t
from pathlib import Path

from PyQt6.QtCore import QDir, QModelIndex
from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QFileSystemModel, QIcon
from loguru import logger
from thatway import Setting

from .dialogs import ActivitySelector
from ..base import BaseSidebar, BaseActivity
from ...assets import Icons


__all__ = ("FileExplorerSidebar",)


class FileExplorerSidebar(BaseSidebar, name="EXPLORER"):
    """The file explorer sidebar"""

    #: The initial path to use for the file explorer options: "pwd", "/", "~"
    rootpath: str | Path = Setting("pwd", desc="Default root path for file explorer")

    #: Default icon, if one isn't specified
    icon: QIcon

    def __init__(
        self, *args, rootpath: str | None = None, icon: QIcon | None = None, **kwargs
    ):
        # Set a default icon, if one isn't specified
        if icon is None:
            icons = Icons("current")
            icon = icons.actions.folders
        self.icon = icon
        super().__init__(*args, icon=icon, **kwargs)  # parent runs create_main_widget

        # Set the rootpath

        # Connect signals
        view: QTreeView = self.widgets.view
        view.doubleClicked.connect(self.load_activity)

    def create_main_widget(self):
        # Create the File explorer sidebar
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())

        self.widgets.view = QTreeView()
        view = self.widgets.view

        # Configure the file explorer sidebar
        view.setModel(model)
        view.setRootIndex(model.index(QDir.homePath()))

        view.setIndentation(10)  # the intentation level of children

        # Show only the filename column
        for i in range(1, 4):
            view.hideColumn(i)
        view.setHeaderHidden(True)  # don't show header

        return view

    def selected_filepaths(
        self, *indices: t.Tuple[QModelIndex, ...]
    ) -> t.Tuple[Path, ...]:
        """Retrieve the selected filepath"""
        # Retrieve selected indices if no indices were passed
        view: QTreeView = self.widgets.view
        indices: t.Tuple[QModelIndex] = indices if indices else view.selectedIndexes()

        filepaths = []
        for index in indices:
            filepath = index.model().filePath(index)
            filepaths.append(Path(filepath))

        return filepaths

    def load_activity(
        self, *indices: t.Tuple[QModelIndex, ...]
    ) -> t.Tuple[BaseActivity, ...]:
        """Load the selected filepaths as entries into an activity"""
        # Find the selected item
        filepaths = self.selected_filepaths(*indices)
        logger.info(f"Loading filepaths: {', '.join(map(str, filepaths))}")

        # Load a ActivitySelector dialog
        activities = []
        for filepath in filepaths:
            dialog = ActivitySelector(filepath=Path(filepath), parent=self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                entry_type = dialog.selected_entry_type()
                activity_type = dialog.selected_activity_type()

                # Create the entry and activity
                entry = entry_type(path=filepath)
                activity = activity_type(entry)
                activities.append(activity)

        return activities
