"""
The main (root) window 
"""

import typing as t
from types import SimpleNamespace
from pathlib import Path
from platform import system

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QSplitter,
    QTabWidget,
    QApplication,
)
from PyQt6.QtGui import QFont
from loguru import logger
from thatway import Setting

from ..entry import Entry
from .icons import get_icons
from .actions import get_actions
from .menubar import get_menubar
from .toolbar import get_toolbar
from .panels import PanelStack
from .view_models import BaseViewModel

__all__ = (
    "MainApplication",
    "MainWindow",
)

ctrl = "Cmd" if system() == "Darwin" else "Ctrl"


class Shortcuts:
    """Application keyboard shortcuts"""

    open = Setting(f"{ctrl}+o", desc="Open document")
    quit = Setting(f"{ctrl}+q", desc="Exit application")


class MainApplication(QApplication):
    """The Qt GUI appication"""

    style = Setting("Fusion", desc="Widget style name")

    stylesheet_file = Setting("styles/dark.qss", desc="Widget stylesheet file to use")

    def __init__(self, argv: t.List[str]) -> None:
        super().__init__(argv)
        logger.debug(f"MainApplication loaded with args: {argv}")

        # Set style
        self.setStyle(self.style)
        logger.debug(f"MainApplication style loaded: {self.style}")

        qss_file = Path(__file__).parent / self.stylesheet_file
        if qss_file.is_file():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
            logger.debug(f"QApplication style sheet loaded: {qss_file}")


class MainWindow(QMainWindow):
    """The main (root) window"""

    #: Main window settings
    window_size = Setting(
        ((3840, 2160), (2560, 1440), (1920, 1080), (1366, 768), (1024, 768)),
        desc="Window size",
    )
    window_width = Setting(800, desc="Default window width")
    window_height = Setting(600, desc="Default window height")

    # Default font settings
    font_family = Setting("Helvetica", desc="Default font")
    font_size = Setting(15, desc="Default font size")

    #: Default project list options
    panels_width = Setting(10, desc="Default width (chars) for panels")

    #: Actions for menu and tool bars
    actions: SimpleNamespace

    #: Fonts
    fonts: t.Dict[str, QFont]

    #: Icons
    icons: SimpleNamespace

    #: Listing of the loaded data entries
    entries: t.List[Entry]

    #: Lising of the loaded ViewModels
    views: t.List[BaseViewModel]

    #: Child widgets
    #:   widgets.root     (root window/widget)
    #:   widgets.central  (central widget of the root window)
    #:   widgets.menubar  (root menubar widget)
    #:   widgets.toolbar  (root toolbar widget)
    #:   widgets.tabs     (tabs bar widget)
    widgets: SimpleNamespace

    def __init__(self, *args):
        super().__init__(*args)

        # Configure assets
        self.fonts = {"default": QFont(self.font_family, self.font_size)}
        self.icons = get_icons()
        self.entries = []
        self.views = []
        self.widgets = SimpleNamespace()
        self.widgets.root = self

        # Configure the main window
        self.setWindowTitle("xamin")
        self.resize(self.window_width, self.window_height)

        # Create core widgets
        self.create_central_widget(*args)
        self.actions = get_actions(parent=self, icons=self.icons)
        self.widgets.menubar = get_menubar(
            parent=self, actions=self.actions, font=self.get_font("menubar")
        )
        self.widgets.toolbar = get_toolbar(
            parent=self, actions=self.actions, font=self.get_font("toolbar")
        )

        # Configure the central widget
        self.setCentralWidget(self.widgets.central)

        # Configure the window
        screen_size = self.get_screen_size()
        max_sizes = [i for i in self.window_size if i < screen_size]
        self.resize(*max_sizes[0])
        self.setWindowTitle("xamin")
        self.show()

        # Add tab widget
        self.widgets.tabs.addTab(QTextEdit(), "Text edit")

    def create_tabs(self):
        """Create the tabs widget"""
        # Create the widget
        self.widgets.tabs = QTabWidget()
        tabs = self.widgets.tabs

        # Configure the tabs
        tabs.setFont(self.get_font("tabs"))
        tabs.setTabsClosable(True)  # Allow tabs to close
        tabs.setTabBarAutoHide(True)  # Only show tabs when more than 1 present
        tabs.setMovable(True)  # Users can move tabs

    def create_central_widget(self, *args):
        """Create the workspace central widget with project files list and work views"""
        # Create central widget
        self.widgets.central = QSplitter()
        splitter = self.widgets.central

        # Configure splitter
        splitter.setHandleWidth(1)

        # Create sub-widgets
        self.create_tabs()
        self.widgets.panels = PanelStack(parent=self)

        # Format the widgets in the workspace
        splitter.addWidget(self.widgets.panels)
        splitter.addWidget(self.widgets.tabs)

        # Configure the splitter
        font = self.get_font()
        width = font.pointSize() * self.panels_width
        current_size = self.size()
        flex_width = current_size.width() - width
        splitter.setSizes((width, flex_width))

    @staticmethod
    def get_screen_size() -> t.Tuple[int, int]:
        """The size (width, height) of the current screen in pixels"""
        screen = QApplication.primaryScreen()
        size = screen.size()
        return size.width(), size.height()

    def get_font(self, *names) -> QFont:
        """The font given by the given names, giving higher precendence to
        earlier names."""
        match_names = [name for name in names if name in self.fonts]
        return self.fonts[match_names[0]] if match_names else self.fonts["default"]
