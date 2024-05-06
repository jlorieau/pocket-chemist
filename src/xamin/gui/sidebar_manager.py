"""
Classes for managing sidebars
"""

import typing as t

from PyQt6.QtWidgets import QStackedWidget, QWidget

__all__ = ("SidebarManager",)


class SidebarManager(QStackedWidget):
    """A manager to stack and switch between sidebars and toolbar icons"""
