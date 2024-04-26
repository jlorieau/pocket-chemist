"""
GUI actions
"""

from types import SimpleNamespace

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QAction
from thatway import Config

from .icons import get_icons
from .shortcuts import shortcuts


actions = None


def get_actions(
    parent: QWidget,
    shortcuts: Config = shortcuts,
    icons: SimpleNamespace | None = None,
    scheme: str = "dark",
) -> SimpleNamespace:
    """Retrieve GUI actions

    Parameters
    ----------
    parent
        The parent widget (main window) to implement the actions for
    shortcuts
        The namespace for shortcuts associated with actions
    icons
        The namespace to use for icons (QIcon instances)
    scheme
        The color scheme of the icons to use

    """
    # Use the cached copy, if available
    global actions
    if actions is not None:
        return actions

    # Create the actions name space
    actions = SimpleNamespace()

    # Get the icon namespace to use with scheme
    icons = icons if icons is None else get_icons()
    icons = getattr(icons, scheme)

    # Exit application action
    actions.exit = QAction(icons.actions.application_exit, "Exit", parent=parent)
    actions.exit.setShortcut(shortcuts.exit)
    actions.exit.setStatusTip("Exit")
    actions.exit.triggered.connect(parent.close)

    # Open application action
    actions.open = QAction(icons.actions.document_open, "Open", parent=parent)
    actions.open.setShortcut(shortcuts.open)
    actions.open.setStatusTip("Open")
    # actions.open.triggered.connect(self.add_project_files)

    return actions
