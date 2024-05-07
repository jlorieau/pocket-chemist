"""
The File Explorer activity class for coordinating the file explorer
"""

from typing import Tuple
from PyQt6.QtWidgets import QWidget

from xamin.entry import Entry
from .sidebar import FileExplorerSidebar
from ..base import BaseActivity

__all__ = ("FileExplorerActivity",)


class FileExplorerActivity(BaseActivity):
    """A file activity for loading files"""

    #: A file explorer should always be present
    persistent: bool = True

    def __init__(self, *entries: Tuple[Entry], parent: QWidget | None = None):
        super().__init__(*entries, parent=parent)

        # Create the sidebar
        sidebar = FileExplorerSidebar()
        self.sidebars.append(sidebar)
