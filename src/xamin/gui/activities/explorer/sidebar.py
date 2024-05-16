"""
Sidebar functionality for the FileExplorer activity
"""

from pathlib import Path

from PyQt6.QtCore import QDir, QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import QTreeView, QWidget, QAbstractItemView
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
    default_rootpath: str = Setting("cwd", desc="Default root path for file explorer")

    #: Default icon, if one isn't specified
    icon: QIcon

    #: The file system model for the file explorer sidebar
    model: QFileSystemModel

    #: Signal emitted when an new activity is created by this sidebar
    activity_created: pyqtSignal = pyqtSignal(BaseActivity)

    def __init__(
        self,
        rootpath: str | None = None,
        icon: QIcon | None = None,
        parent: QWidget | None = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ):
        # Set the rootpath
        rootpath = rootpath if rootpath is not None else self.default_rootpath

        # Deal with special values for the rootpath, like cwd (current workind
        # directory) and pwd (present working directory)
        if rootpath in ("cwd", "pwd"):
            self.rootpath = Path.cwd()
        else:
            self.rootpath = Path(rootpath).expanduser()

        # Set a default icon, if one isn't specified
        if icon is None:
            icons = Icons("current")
            icon = icons.actions.folders
        self.icon = icon

        # parent runs create_main_widget
        super().__init__(icon=icon, parent=parent, flags=flags)

        # Connect signals
        main = self.main_widget
        main.doubleClicked.connect(self.load_activity)

    @property
    def main_widget(self) -> QTreeView:
        """Override parent method to return a tree view"""
        # Create the file system model
        model = getattr(self, "model", None)
        if model is None:
            model = QFileSystemModel()
            model.setRootPath(QDir.rootPath())
            self.model = model
        model = self.model

        # Get or create the main widget
        main = self.findChild(QTreeView, "main")
        if main is None:
            main = QTreeView()
            main.setObjectName("main")

            # Configure the file explorer sidebar
            main.setModel(model)
            main.setRootIndex(model.index(str(self.rootpath)))
            logger.info(f"FileExplorerSidebar loaded rootpath {self.rootpath}")

            # Configure the intentation level of children
            main.setIndentation(10)

            # Configure to show only the filename column
            for i in range(1, 4):
                main.hideColumn(i)
            main.setHeaderHidden(True)  # don't show header

            # Only allow 1 item to be selected or opened at a time
            main.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        return main

    def selected_filepath(self, index: QModelIndex | None = None) -> Path | None:
        """Retrieve the filepath for the given index or the selected index from the
        main tree view widget."""
        # If no index was specified, get the selected indices from the widget
        main = self.main_widget
        if index is None:
            if main.selectedIndexes():
                index = main.selectedIndexes()[0]
            else:
                return None

        model = index.model()
        assert isinstance(model, QFileSystemModel)

        filepath = model.filePath(index)
        return Path(filepath)

    def load_activity(self, index: QModelIndex | None = None) -> BaseActivity | None:
        """Load the selected filepaths as entries into an activity"""
        # Find the selected items and pick the first one
        filepath = self.selected_filepath(index)
        if filepath is None:
            return None

        # Load a ActivitySelector dialog
        dialog = ActivitySelector(filepath=Path(filepath), parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            entry_type = dialog.selected_entry_type()
            activity_type = dialog.selected_activity_type()

            if entry_type is None or activity_type is None:
                logger.error("Could not find selected entry_type or activity type")
                return None

            # Create the entry and activity
            entry = entry_type(path=filepath)
            activity = activity_type(entry)

            # Emit signal and return
            logger.info(
                f"Created activity '{activity.__class__.__name__}' for "
                f"filepath '{filepath}'"
            )
        self.activity_created.emit(activity)
        return activity
