from PyQt6.QtWidgets import QStackedWidget, QWidget

from .explorer import FileExplorer

__all__ = ("PanelStack",)


class PanelStack(QStackedWidget):
    """A stacked widget for the different panels"""

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        # Add default widgets
        self.addWidget(FileExplorer())
