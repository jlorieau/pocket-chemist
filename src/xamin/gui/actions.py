"""
GUI actions
"""

from types import SimpleNamespace

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QAction
from thatway import Config

from .icons import get_icons
from .shortcuts import shortcuts

__all__ = ("MainActions",)


class MainActions(SimpleNamespace):
    """The GUI actions

    Parameters
    ----------
    shortcuts
        The namespace for shortcuts associated with actions
    icons
        The namespace to use for icons (QIcon instances)
    parent
        The main window widget that controls the actions
    """

    def __init__(
        self, shortcuts: Config, icons: SimpleNamespace, parent: QWidget | None = None
    ):
        super().__init__()

        # Get the icon namespace to use with scheme
        icons = icons if icons is not None else get_icons()

        # Exit application action
        self.exit = QAction(icons.actions.application_exit, "Exit", parent=parent)
        self.exit.setShortcut(shortcuts.exit)
        self.exit.setStatusTip("Exit")
        self.exit.triggered.connect(parent.close)

        # Open application action
        self.open = QAction(icons.actions.document_open, "Open", parent=parent)
        self.open.setShortcut(shortcuts.open)
        self.open.setStatusTip("Open")
