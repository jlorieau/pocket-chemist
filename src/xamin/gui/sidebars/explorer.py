"""
A file explorer sidebar
"""

from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView
from loguru import logger

from .base import BaseSidebar
from ..dialogs import ViewSelector

__all__ = ("FileExplorer",)


class FileExplorer(BaseSidebar, name="EXPLORER"):
    """A file explorer sidebar widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Connect signals
        view: QTreeView = self.widgets.view
        view.doubleClicked.connect(self.load_filepath)

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

    def load_filepath(self, index):
        """Load the selected filepath"""
        # Find the selected item
        item = self.widgets.view.selectedIndexes()[0]
        model: QFileSystemModel = item.model()
        filepath: str = model.filePath(index)
        logger.debug(f"Filepath selected: {filepath}")

        # Load a ViewSelector dialog
        dialog = ViewSelector(filepath=Path(filepath), parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            entry_type = dialog.selected_entry_type()
            view_model_type = dialog.selected_view_model_type()

            # Create the entry and view mode
            entry = entry_type(path=filepath)
            view_model = view_model_type(entry=entry)

            # Emit the signal
            self.fileopen.emit(entry, view_model)
