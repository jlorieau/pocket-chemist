"""
The main (root) application and window 
"""

import typing as t
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QSplitter,
    QStackedWidget,
)
from loguru import logger
from thatway import Setting

from .shortcuts import Shortcuts
from .actions import Actions
from .assets import Icons
from .activities import BaseActivity
from .menubar import Menubar
from .toolbar import Toolbar

__all__ = (
    "MainApplication",
    "MainWindow",
)


class MainApplication(QApplication):
    """The Qt GUI appication"""

    style = Setting("Fusion", desc="Widget style name")

    stylesheet_file = Setting(
        "assets/styles/dark.qss", desc="Widget stylesheet file to use"
    )

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


# Main Window classes


class MainWindowWidgets:
    """The collection of widgets for the window"""

    __slots__ = ("root", "menubar", "toolbar", "splitter", "sidebars", "tabs")

    #: The root main window
    root: "MainWindow"

    #: The main window menubar
    menubar: Menubar

    #: The main toolbar
    toolbar: Toolbar

    #: The splitter between the sidebars and the main views
    splitter: QSplitter

    #: The stack of sidebars from activities
    sidebars: QStackedWidget

    #: The tabs for activity views
    tabs: QTabWidget


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
    sidebars_width = Setting(12, desc="Default width (chars) for sidebars")

    #: Fonts
    fonts: t.Dict[str, QFont]

    #: Icons
    icons: Icons

    #: Keyboard shortcuts for the main window
    shortcuts: Shortcuts

    #: Widget tree for the main window
    widgets: MainWindowWidgets

    #: Activities owned by the main window
    activities: t.List[BaseActivity]

    #: Actions for menubars/toolbars
    _actions: Actions

    def __init__(
        self, parent: QWidget | None = None, flags: Qt.WindowType = Qt.WindowType.Window
    ) -> None:
        """Initialize the class

        Parameters
        ----------
        args
            The command-line arguments for opening the window
        """
        super().__init__(parent, flags)

        # Configure assets
        self.fonts = {"default": QFont(self.font_family, self.font_size)}
        self.icons = Icons("current")
        self.shortcuts = Shortcuts()
        self._actions = Actions(shortcuts=self.shortcuts, icons=self.icons, parent=self)
        self.activities = []

        # Create and configure window and widgets
        self.reset_window()
        self.reset_widgets()
        self.reset_activities()

    def get_font(self, *names: str) -> QFont:
        """The font given by the given names, giving higher precendence to
        earlier names."""
        match_names = [name for name in names if name in self.fonts]
        return self.fonts[match_names[0]] if match_names else self.fonts["default"]

    @property
    def screen_size(self) -> t.Tuple[int, int] | None:
        """The size (width, height) of the current screen in pixels"""
        screen = QApplication.primaryScreen()
        if screen is not None:
            size = screen.size()
            return size.width(), size.height()
        else:
            return None

    def reset_window(self) -> None:
        """Reset settings for the main window"""
        self.setWindowTitle("xamin")

        # Resize the window to the largest size available
        max_sizes = [i for i in self.window_size if i < self.screen_size]
        self.resize(*max_sizes[0])

        # Resize the splitter

    def reset_widgets(self) -> MainWindowWidgets:
        """Create and reset the configuration for widgets of the main window

        This method is intended to be run idempotently and (re-)configure widgets
        """
        if not hasattr(self, "widgets"):
            # Set the widget namespace
            self.widgets = MainWindowWidgets()

        if not hasattr(self.widgets, "root"):
            self.widgets.root = self

        # Create and configure the menubar (owner: main window)
        if not hasattr(self.widgets, "menubar"):
            self.widgets.menubar = Menubar(
                parent=self, actions=self._actions, font=self.get_font("menubar")
            )

        self.setMenuBar(self.widgets.menubar)

        # Create and configure the toolbar (owner: main window)
        if not hasattr(self.widgets, "toolbar"):
            self.widgets.toolbar = Toolbar(
                parent=self, actions=self._actions, font=self.get_font("toolbar")
            )

        # Create and configure the splitter (central widget, owner: main window)
        if not hasattr(self.widgets, "splitter"):
            self.widgets.splitter = QSplitter()

        self.widgets.splitter.setHandleWidth(1)

        # Create and configure the sidebars (owner: splitter)
        if not hasattr(self.widgets, "sidebars"):
            parent = self.widgets.splitter
            self.widgets.sidebars = QStackedWidget(parent=parent)

        self.widgets.splitter.addWidget(self.widgets.sidebars)

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

    def reset_activities(self) -> None:
        """Create and configure persistent activities"""
        persistent_clses = [cls for cls in BaseActivity.subclasses() if cls.persistent]

        # Find missing activity types
        current_clses = [activity.__class__ for activity in self.activities]
        missing_clses = [cls for cls in persistent_clses if cls not in current_clses]

        for missing_cls in missing_clses:
            activity = missing_cls()
            self.add_activity(activity=activity)

    def focus_activity(self) -> None:
        """Change focus to the given activity"""

    def add_activity(self, activity: BaseActivity) -> None:
        """Add an activity to the window"""
        # Add the activity to the listings
        self.activities.append(activity)
        logger.info(f"Loading activity '{activity}'")

        # Connect the sidebar(s)
        sidebars: QStackedWidget = self.widgets.sidebars
        for sidebar in activity.sidebars:
            logger.info(f"Adding sidebar '{sidebar}'")

            # Add the widget
            sidebars.addWidget(sidebar)

            # Add any actions to the toolbar
            action = sidebar.action
            action.triggered.connect(lambda: sidebars.setCurrentWidget(sidebar))
            self.widgets.toolbar.addAction(action)

        # Connect the view(s)
        for view in activity.views:
            logger.info(f"Adding view '{view}' to tabs")
            self.widgets.tabs.addTab(view, "tab")  # FIXME: Change tab name

    # def remove_activity():
    #     """Remove activity"""
