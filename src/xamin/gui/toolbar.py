"""
Toolbar for the main window
"""

from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QToolBar
from PyQt6.QtGui import QFont
from thatway import config, Setting

toolbar = None

# Toolbar settings
config.toolbar.orientation = Setting("vertical", desc="Default toolbar orientation")
config.toolbar.movable = Setting(False, desc="Allow toolbar to be repositioned")
config.toolbar.location = Setting("left", desc="Default location of the toolbar")


def get_toolbar(
    parent: QWidget, actions: SimpleNamespace, font: QFont | None = None
) -> QToolBar:
    """Retrieve the main toolbar for the main window.

    Parameters
    ----------
    parent
        The parent widget (main window) to implement the actions for
    actions
        The GUI actions associate with menubar entries
    font
        The font to use in rendering the menubar

    Returns
    -------
    toolbar
        The toolbar widget for the main window
    """
    # Retrieve cached version, if available
    global toolbar
    if toolbar is not None:
        return toolbar

    # Create the toolbar
    toolbar = QToolBar("toolbar")

    # Configure the toolbar
    toolbar.setFont(font)

    orientation = (
        Qt.Orientation.Vertical
        if config.toolbar.orientation == "vertical"
        else Qt.Orientation.Horizontal
    )
    toolbar.setOrientation(orientation)
    toolbar.setMovable(config.toolbar.movable)

    if config.toolbar.location == "left":
        location = Qt.ToolBarArea.LeftToolBarArea
    elif config.toolbar.location == "right":
        location = Qt.ToolBarArea.RightToolBarArea
    elif config.toolbar.location == "bottom":
        location = Qt.ToolBarArea.BottomToolBarArea
    else:
        location = Qt.ToolBarArea.TopToolBarArea

    parent.addToolBar(location, toolbar)

    # Add toolbar actions
    toolbar.addAction(actions.open)
    toolbar.addAction(actions.exit)
