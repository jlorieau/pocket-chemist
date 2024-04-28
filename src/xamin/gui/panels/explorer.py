"""
A file explorer panel
"""

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView

from .base import BasePanel


class FileExplorer(BasePanel, name="EXPLORER"):
    """A file explorer panel widget"""

    def create_main_widget(self):

        # Create the File explorer panel
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())

        self.widgets.view = QTreeView()
        view = self.widgets.view

        # Configure the file explorer panel
        view.setModel(model)
        view.setRootIndex(model.index(QDir.homePath()))

        view.setIndentation(10)  # the intentation level of children

        # Show only the filename column
        for i in range(1, 4):
            view.hideColumn(i)
        view.setHeaderHidden(True)  # don't show header

        return view
