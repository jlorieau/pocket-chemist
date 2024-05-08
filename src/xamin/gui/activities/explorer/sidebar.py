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

    #: The root path to use with the file explorer.
    rootpath: Path

    #: The default root path to use for the file explorer options: "pwd", "/", "~"
    default_rootpath: str | Path = Setting(
        "cwd", desc="Default root path for file explorer"
    )

    #: Default icon, if one isn't specified
    icon: QIcon

    #: The file system model for the file explorer view
    model: QFileSystemModel

    def __init__(
        self,
        *args,
        rootpath: t.Optional[str] = None,
        icon: t.Optional[QIcon] = None,
        **kwargs,
    ):
        # Set the rootpath
        rootpath = rootpath if rootpath is not None else self.default_rootpath

        if isinstance(rootpath, str):
            # Deal with special values for the rootpath, like cwd (current workind
            # directory) and pwd (present working directory)
            if rootpath in ("cwd", "pwd"):
                rootpath = Path.cwd()
            rootpath = Path(rootpath)
        self.rootpath = rootpath.expanduser()

        # Set a default icon, if one isn't specified
        if icon is None:
            icons = Icons("current")
            icon = icons.actions.folders
        self.icon = icon
        super().__init__(*args, icon=icon, **kwargs)  # parent runs create_main_widget

        # Connect signals
        view: QTreeView = self.widgets.view
        view.doubleClicked.connect(self.load_activity)

    def reset_main_widget(self):
        # Create the File explorer sidebar model
        if not hasattr(self, "model") or self.model is None:
            self.model = QFileSystemModel()
            self.model.setRootPath(QDir.rootPath())
        model = self.model

        # Create the File explorer sidebar view
        if not hasattr(self.widgets, "view") or self.widgets.view is None:
            self.widgets.view = QTreeView()
        view = self.widgets.view

        # Configure the file explorer sidebar
        view.setModel(model)
        view.setRootIndex(model.index(str(self.rootpath)))
        logger.info(f"FileExplorerSidebar loaded rootpath {self.rootpath}")

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
