"""
Keyboard shortcuts for the GUI
"""

from thatway import Setting, config

shortcuts = config.shortcuts

shortcuts.open = Setting("Ctrl+O", desc="Open documents")
shortcuts.exit = Setting("Ctrl+Q", desc="Quit application")
