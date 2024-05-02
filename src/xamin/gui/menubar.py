"""
Menubar for the main window
"""

from types import SimpleNamespace

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QMenuBar

__all__ = ("MainMenuBar",)


class MainMenuBar(QMenuBar):
    """The menubar for the main window

    Parameters
    ----------
    parent
        The parent widget (main window) to implement the actions for
    actions
        The GUI actions associate with menubar entries
    font
        The font to use in rendering the menubar
    """

    def __init__(
        self,
        parent: QWidget | None,
        actions: SimpleNamespace | None = None,
        font: QFont | None = None,
    ) -> None:
        super().__init__(parent)

        # Configure the menubar
        if font is not None:
            self.setFont(font)

        self.setNativeMenuBar(True)  # use native macOS menubar

        # Populate menubar
        if actions is not None:
            fileMenu = self.addMenu("&File")  # File
            fileMenu.addAction(actions.open)  # File->Open
            fileMenu.addAction(actions.exit)  # File->Exit
