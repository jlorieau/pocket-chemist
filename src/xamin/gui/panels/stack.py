from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QStackedWidget, QWidget

from .explorer import FileExplorer

__all__ = ("PanelStack",)


class PanelStack(QStackedWidget):
    """A stacked widget for the different panels"""

    #: Signal emitted when a file is opened.
    #: Arguments: Entry instance, ViewModel instance
    fileopen = pyqtSignal(object, object)

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        # Add default widgets
        explorer = FileExplorer()
        self.addWidget(explorer)

        # Connect signals
        # self.fileopen.connect(explorer.fileopen)
        explorer.fileopen.connect(self.fileopen)
