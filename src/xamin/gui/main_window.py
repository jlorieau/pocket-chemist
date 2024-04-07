"""
The main (root) window 
"""

import typing as t
from pathlib import Path
from platform import system

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMenuBar,
    QTextEdit,
    QToolBar,
    QLabel,
    QListWidget,
    QFileDialog,
    QSplitter,
    QTabWidget,
    QApplication,
)
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap, QKeySequence
from thatway import Setting

from .projects import ProjectsModel, ProjectsView

__all__ = ("MainWindow",)

ctrl = "Cmd" if system() == "Darwin" else "Ctrl"


class Shortcuts:
    """Application keyboard shortcuts"""

    open = Setting(f"{ctrl}+o", desc="Open document")
    quit = Setting(f"{ctrl}+q", desc="Exit application")


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
    projects_view_width = Setting(10, desc="Default width (chars) for project listing")

    #: Central widget of the main window
    central_widget: QWidget

    #: Actions for menu and tool bars
    actions: t.Dict[str, QAction]

    #: Fonts
    fonts: t.Dict[str, QFont]

    #: Icons
    icons: t.Dict[str, QIcon]

    #: Menu bar widget for the main window
    menubar: QMenuBar

    #: Tool bar widget for the main window
    toolbar: QToolBar

    #: Status bar widget for the main window
    statusbar: QStatusBar

    #: Project listing widget for the main window
    projects_model: ProjectsModel
    projects_view: ProjectsView

    #: Tab workspace view widget
    tabs: QTabWidget

    def __init__(self, *args):
        super().__init__()

        # Configure assets
        self.fonts = {"default": QFont(self.font_family, self.font_size)}
        self._create_icons()

        # Configure the main window
        self.setWindowTitle("xamin")
        self.resize(self.window_width, self.window_height)

        # Create core widgets
        self._create_central_widget(*args)
        self._create_actions()
        self._create_menubar()
        if self.toolbar_visible:
            self._create_toolbar()

        # Configure the central widget
        self.setCentralWidget(self.central_widget)

        # Configure the window
        screen_size = self.get_screen_size()
        max_sizes = [i for i in self.window_size if i < screen_size]
        self.resize(*max_sizes[0])
        self.setWindowTitle("xamin")
        self.show()

        # Add tab
        self.tabs.addTab(QTextEdit(), "Text edit")

    def _create_actions(self):
        """Create actions for menubar and toolbars"""
        self.actions = dict()

        # Exit application action
        exit = self.actions.setdefault(
            "exit", QAction(self.icons["exit"], "Exit", self)
        )
        exit.setShortcut(Shortcuts.quit)
        exit.setStatusTip("Exit")
        exit.triggered.connect(self.close)

        # Open application action
        open = self.actions.setdefault(
            "open", QAction(self.icons["open"], "Open", self)
        )
        open.setShortcut(Shortcuts.open)
        open.setStatusTip("Open")
        open.triggered.connect(self.add_project_files)

    def _create_icons(self):
        icons = dict()
        self.icons = icons

        # Populate icons
        base_dir = Path(__file__).parent / "icons" / "dark"
        paths = {
            "exit": base_dir / "actions" / "application-exit.svg",
            "open": base_dir / "actions" / "document-open.svg",
        }
        for name, item in paths.items():
            icons[name] = QIcon(QPixmap(str(item))) if isinstance(item, Path) else item

    def _create_menubar(self):
        """Create menubar for the main window"""
        # Create the menubar
        self.menubar = self.menuBar()

        # Configure the menubar
        self.menubar.setFont(self.get_font("menubar"))
        self.menubar.setNativeMenuBar(self.menubar_native)  # macOS

        # Populate menubar
        fileMenu = self.menubar.addMenu("&File")
        fileMenu.addAction(self.actions["open"])
        fileMenu.addAction(self.actions["exit"])

    def _create_toolbar(self):
        """Create toolbar for the main window"""
        # Create the toolbar
        self.toolbar = QToolBar("toobar")
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Add toolbar actions
        self.toolbar.addAction(self.actions["open"])
        self.toolbar.addAction(self.actions["exit"])

        # Configure toolbar
        font = self.get_font("toolbar")
        self.toolbar.setFont(font)

    def _create_central_widget(self, *args):
        """Create the workspace central widget with project files list and work views"""
        # Create sub-widgets
        self._create_projects(*args)
        self._create_tabs()

        # Format the widgets in the workspace
        splitter = QSplitter()
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.projects_view)

        # Configure the splitter
        font = self.get_font()
        width = font.pointSize() * self.projects_view_width
        current_size = self.size()
        flex_width = current_size.width() - width
        splitter.setSizes((flex_width, width))

        self.central_widget = splitter

    def _create_projects(self, *args):
        """Create the project listing widget"""
        self.projects_model = ProjectsModel()
        self.projects_view = ProjectsView()

        # Configure model and view
        self.projects_model.append_files(*args)
        self.projects_view.setModel(self.projects_model)

        # Configure project list settings
        font = self.get_font("projects")
        self.projects_view.setFont(font)

    def _create_tabs(self):
        """Create the tabs widget"""
        self.tabs = QTabWidget()

        # Configure the tabs
        self.tabs.setFont(self.get_font("tabs"))
        self.tabs.setTabsClosable(True)  # Allow tabs to close
        self.tabs.setTabBarAutoHide(True)  # Only show tabs when more than 1 present
        self.tabs.setMovable(True)  # Users can move tabs

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
        files = dialog.getOpenFileNames()
