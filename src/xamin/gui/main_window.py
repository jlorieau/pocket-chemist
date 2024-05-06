"""
The main (root) application and window 
"""

import typing as t
from pathlib import Path
from types import SimpleNamespace

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QSplitter
from loguru import logger
from thatway import Setting

from xamin.entry import Entry
from .shortcuts import Shortcuts
from .actions import Actions
from .assets import Icons
from .activities import BaseActivity
from .menubar import Menubar
from .toolbar import Toolbar
from .sidebar_manager import SidebarManager

__all__ = (
    "MainApplication",
    "MainWindow",
)


class MainApplication(QApplication):
    """The Qt GUI appication"""

    style = Setting("Fusion", desc="Widget style name")

    stylesheet_file = Setting("styles/dark.qss", desc="Widget stylesheet file to use")

    def __init__(self, argv: t.List[str]) -> None:
        super().__init__(argv)
        logger.info(f"MainApplication loaded with args: {argv}")

        # Set style
        self.setStyle(self.style)
        logger.info(f"MainApplication style loaded: {self.style}")

        qss_file = Path(__file__).parent / self.stylesheet_file
        if qss_file.is_file():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
            logger.info(f"QApplication style sheet loaded: {qss_file}")


class MainWindow(QMainWindow):
    """The main (root) window"""

    # Default window sizes
    window_size = Setting(
        ((3840, 2160), (2560, 1440), (1920, 1080), (1366, 768), (1024, 768)),
        desc="Default window size",
    )

    # Default font settings
    font_family = Setting("Helvetica", desc="Default font")
    font_size = Setting(15, desc="Default font size")

    #: Default project list options
    sidebars_width = Setting(10, desc="Default width (chars) for sidebars")

    #: Fonts
    fonts: t.Dict[str, QFont]

    #: Icons
    icons: Icons

    #: Keyboard shortcuts for the main window
    shortcuts: Shortcuts

    #: Actions for menubars/toolbars
    actions: Actions

    #: Widget tree for the main window
    widgets: SimpleNamespace

    #: Entries owned by the main window
    entries: t.List[Entry]

    #: Activities owned by the main window
    activities: t.List[BaseActivity]

    def __init__(self, *args: t.Tuple[str, ...]):
        """Initialize the class

        Parameters
        ----------
        args
            The command-line arguments for opening the window
        """
        super().__init__(*args)

        # Configure assets
        self.fonts = {"default": QFont(self.font_family, self.font_size)}
        self.icons = Icons("current")
        self.shortcuts = Shortcuts()
        self.actions = Actions(shortcuts=self.shortcuts, icons=self.icons, parent=self)

        self.reset_window()
        self.reset_widgets()

        self.entries = []
        self.activities = []

    def reset_window(self):
        """Reset settings for the main window"""
        self.setWindowTitle("xamin")

        # Resize the window to the largest size available
        max_sizes = [i for i in self.window_size if i < self.screen_size]
        self.resize(*max_sizes[0])

        # Resize the splitter

    def reset_widgets(self) -> SimpleNamespace:
        """Create and reset the configuration for widgets of the main window

        This method is intended to be run idempotently and (re-)configure widgets
        """
        if not hasattr(self, "widgets"):
            # Set the widget namespace
            self.widgets = SimpleNamespace()

        if not hasattr(self.widgets, "root"):
            self.widgets.root = self

        # Create and configure the menubar (owner: main window)
        if not hasattr(self.widgets, "menubar"):
            self.widgets.menubar = Menubar(
                parent=self, actions=self.actions, font=self.get_font("menubar")
            )

        self.setMenuBar(self.widgets.menubar)

        # Create and configure the toolbar (owner: main window)
        if not hasattr(self.widgets, "toolbar"):
            self.widgets.toolbar = Toolbar(
                parent=self, actions=self.actions, font=self.get_font("toolbar")
            )

        # Create and configure the splitter (central widget, owner: main window)
        if not hasattr(self.widgets, "splitter"):
            self.widgets.splitter = QSplitter()

        self.widgets.splitter.setHandleWidth(1)

        # Create and configure the sidebar manager (owner: splitter)
        if not hasattr(self.widgets, "sidebar_manager"):
            parent = self.widgets.splitter
            self.widgets.sidebar_manager = SidebarManager(parent=parent)

        self.widgets.splitter.addWidget(self.widgets.sidebar_manager)

        # Create the tab widget (owner: splitter)
        if not hasattr(self.widgets, "tabs"):
            parent = self.widgets.splitter
            self.widgets.tabs = QTabWidget(parent=parent)

        self.widgets.tabs.setFont(self.get_font("tabs"))
        self.widgets.tabs.setTabsClosable(True)
        self.widgets.tabs.setTabBarAutoHide(True)
        self.widgets.tabs.setMovable(True)

        # Set the central widget
        self.setCentralWidget(self.widgets.splitter)

        # Configure the splitter size
        font = self.get_font()
        width = font.pointSize() * self.sidebars_width
        current_size = self.size()
        flex_width = current_size.width() - width
        self.widgets.splitter.setSizes((width, flex_width))

        return self.widgets

    def get_font(self, *names) -> QFont:
        """The font given by the given names, giving higher precendence to
        earlier names."""
        match_names = [name for name in names if name in self.fonts]
        return self.fonts[match_names[0]] if match_names else self.fonts["default"]

    @property
    def screen_size(self) -> t.Tuple[int, int]:
        """The size (width, height) of the current screen in pixels"""
        screen = QApplication.primaryScreen()
        size = screen.size()
        return size.width(), size.height()

    def focus_activity():
        """Change focus to the given activity"""

    def remove_activity():
        """Remove activity"""
