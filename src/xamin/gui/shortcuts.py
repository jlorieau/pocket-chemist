"""
Keyboard shortcuts for the GUI
"""

from thatway import Setting


class Shortcuts:
    """Global shortcuts for the app"""

    open = Setting("Ctrl+O", desc="Open documents")
    exit = Setting("Ctrl+Q", desc="Quit application")
