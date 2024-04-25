"""
The main (root) window 
"""

import typing as t
from types import SimpleNamespace
from pathlib import Path
from platform import system

from PyQt6.QtCore import Qt, QDir
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QWidget,
    QMenuBar,
    QTextEdit,
    QToolBar,
    QFileDialog,
    QSplitter,
    QTabWidget,
    QApplication,
    QTreeView,
)
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap, QFileSystemModel
from loguru import logger
from thatway import Setting

from .icons import get_icons
from .plugins import get_plugin_manager, EntryViewsType

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

    # Menubar options
    menubar_native = Setting(True, desc="Use native OS for menubar display")

    # Toolbar options
    toolbar_visible = Setting(True, desc="Display toolbar")

    #: Default project list options
    panels_width = Setting(10, desc="Default width (chars) for panels")

    #: Actions for menu and tool bars
    actions: SimpleNamespace

    #: Fonts
    fonts: t.Dict[str, QFont]

    #: Icons
    icons: SimpleNamespace

    #: Entry views
    entry_views: EntryViewsType

    #: Listing of widgets
    widgets: SimpleNamespace

    def __init__(self, *args):
        super().__init__()

        # Load hooks
        self.load_hooks()

        # Configure assets
        self.widgets = SimpleNamespace()
        self.fonts = {"default": QFont(self.font_family, self.font_size)}
        self.icons = get_icons()

        # Configure the main window
        self.setWindowTitle("xamin")
        self.resize(self.window_width, self.window_height)

        # Create core widgets
        self.create_central_widget(*args)
        self.create_actions()
        self.create_menubar()
        if self.toolbar_visible:
            self.create_toolbar()

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

    def create_actions(self):
        """Create actions for menubar and toolbars"""
        # Create the actions name space
        self.actions = SimpleNamespace()
        actions = self.actions

        # Get the icon namespace to use
        icons = self.icons.current

        # Exit application action
        actions.exit = QAction(icons.actions.application_exit, "Exit", self)
        actions.exit.setShortcut(Shortcuts.quit)
        actions.exit.setStatusTip("Exit")
        actions.exit.triggered.connect(self.close)

        # Open application action
        actions.open = QAction(icons.actions.document_open, "Open", self)
        actions.open.setShortcut(Shortcuts.open)
        actions.open.setStatusTip("Open")
        actions.open.triggered.connect(self.add_project_files)

    def create_menubar(self):
        """Create menubar for the main window"""
        # Create the menubar
        self.widgets.menubar = self.menuBar()
        menubar = self.widgets.menubar

        # Configure the menubar
        menubar.setFont(self.get_font("menubar"))
        menubar.setNativeMenuBar(self.menubar_native)  # macOS

        # Populate menubar
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(self.actions.open)
        fileMenu.addAction(self.actions.exit)

    def create_toolbar(self):
        """Create toolbar for the main window"""
        # Create the toolbar
        self.widgets.toolbar = QToolBar("toobar")
        toolbar = self.widgets.toolbar

        # Configure the toolbar
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)

        # Add toolbar actions
        toolbar.addAction(self.actions.open)
        toolbar.addAction(self.actions.exit)

        # Configure toolbar
        font = self.get_font("toolbar")
        toolbar.setFont(font)

    def create_panels(self, *args):
        """Create the panels widgets"""
        # Create the panels namespace
        self.widgets.panels = SimpleNamespace()

        # Create the File explorer panel
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())

        self.widgets.panels.file = QTreeView()
        view = self.widgets.panels.file

        # Configure the file explorer panel
        view.setModel(model)
        view.setRootIndex(model.index(QDir.homePath()))

        # Show only the filename column
        for i in range(1, 4):
            view.hideColumn(i)
        view.setHeaderHidden(True)  # don't show header

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

        # Create sub-widgets
        self.create_tabs()
        self.create_panels()

        # Format the widgets in the workspace
        splitter.addWidget(self.widgets.panels.file)
        splitter.addWidget(self.widgets.tabs)

        # Configure the splitter
        font = self.get_font()
        width = font.pointSize() * self.panels_width
        current_size = self.size()
        flex_width = current_size.width() - width
        splitter.setSizes((width, flex_width))

    def load_hooks(self):
        """Load plugin hooks"""
        # Get the plugin manager
        pm = get_plugin_manager()

        # Load entry views
        self.entry_views = dict()
        pm.hook.add_entry_views(entry_views=self.entry_views)
        logger.debug(f"{self.__class__.__name__}.entry_views: {self.entry_views}")

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

    def add_project_files(self) -> None:
        """Add project files with the file dialog"""
        dialog = QFileDialog()
        files, filter = dialog.getOpenFileNames()
