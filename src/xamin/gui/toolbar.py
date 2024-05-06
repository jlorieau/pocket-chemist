"""
Toolbar for the main window
"""

from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QFont
from thatway import Setting

__all__ = ("Toolbar",)


class Toolbar(QToolBar):
    """Main toolbar for the application

    Parameters
    ----------
    title
        The title for the toolbar
    parent
        The parent widget that owns this toolbar
    actions
        The actions namespace for the main window
    font
        The font to use is styling this toolbar
    """

    # Settings
    orientation = Setting("vertical", desc="Default toolbar orientation")
    movable = Setting(False, desc="Allow toolbar to be repositioned")
    location = Setting("left", desc="Default location of the toolbar")

    def __init__(
        self,
        title: str | None = None,
        parent: QWidget | None = None,
        actions: SimpleNamespace | None = None,
        font: QFont | None = None,
    ):
        title = title or "toolbar"
        super().__init__(title, parent)

        # Configure the toolbar
        self.setFont(font)

        orientation = (
            Qt.Orientation.Vertical
            if self.orientation == "vertical"
            else Qt.Orientation.Horizontal
        )
        self.setOrientation(orientation)

        self.setMovable(self.movable)

        if self.location == "left":
            location = Qt.ToolBarArea.LeftToolBarArea
        elif self.location == "right":
            location = Qt.ToolBarArea.RightToolBarArea
        elif self.location == "bottom":
            location = Qt.ToolBarArea.BottomToolBarArea
        else:
            location = Qt.ToolBarArea.TopToolBarArea

        if parent is not None:
            parent.addToolBar(location, self)

        # Add toolbar actions
        if actions is not None:
            self.addAction(actions.open)
            self.addAction(actions.exit)
