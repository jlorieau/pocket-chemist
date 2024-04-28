"""
Menubar for the main window
"""

from types import SimpleNamespace

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QMenuBar

menubar = None


def get_menubar(
    parent: QWidget, actions: SimpleNamespace, font: QFont | None = None
) -> QMenuBar:
    """Retrieve the menubar for the main window.

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
    menubar
        The menubar widget for the main window
    """
    # Retrieve cached version, if available
    global menubar
    if menubar is not None:
        return menubar

    # Create the menubar
    menubar = parent.menuBar()

    # Configure the menubar
    if font is not None:
        menubar.setFont(font)

    menubar.setNativeMenuBar(True)  # use native macOS menubar

    # Populate menubar
    fileMenu = menubar.addMenu("&File")  # File
    fileMenu.addAction(actions.open)  # File->Open
    fileMenu.addAction(actions.exit)  # File->Exit

    return menubar
