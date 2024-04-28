"""
Side panels for the main window
"""

from .base import BasePanel, PanelStack
from .explorer import FileExplorer


def get_panels() -> PanelStack:
    """Retrieve the panels for the main window."""
    panels = PanelStack()
    panels.addWidget(FileExplorer())
    return panels
