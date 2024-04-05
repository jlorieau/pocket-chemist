"""
The main (root) window 
"""
import typing as t
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QStatusBar, QHBoxLayout, QWidget,
                             QMenuBar, QTextEdit, QToolBar, QListWidget,
                             QTabWidget, QApplication)
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap
from thatway import Setting

__all__ = ('MainWindow',)

class MainWindow(QMainWindow):
    """The main (root) window"""

    #: Main window settings
    window_size = Setting((
        (2560, 1440),
        (1920, 1080),
        (1366, 768),
        (1024, 768)),
        desc="Window size",
    )
    window_width = Setting(800, desc="Default window width")
    window_height = Setting(600, desc="Default window height")
    
    # Default font settings
    font_family = Setting('Helvetica', desc='Default font')
    font_size = Setting(15, desc="Default font size")

    #: Default keyboard shortcuts for actions
    shortcut_open = Setting('Ctrl+O', desc="Open shortcut")
    shortcut_exit = Setting('Ctrl+Q', desc="Exit shortcut")

    # Menubar options
    menubar_native = Setting(True, desc="Use native OS for menubar display")

    # Toolbar options
    toolbar_visible = Setting(True, desc="Display toolbar")

    #: Default project list options
    project_list_width = Setting(10, desc="Default width (chars) for project list")

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
    project_list: QListWidget

    #: Tab workspace view widget
    tabs: QTabWidget

    def __init__(self):
        super().__init__()

        # Configure assets
        self.fonts = {'default': QFont(self.font_family, self.font_size)}
        self._create_icons()

        # Configure the main window
        self.setWindowTitle("xamin")
        self.resize(self.window_width, self.window_height)

        # Create core widgets
        self._create_central_widget()
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
        self.setWindowTitle('xamin')
        self.show()

        # Add tab
        self.tabs.addTab(QTextEdit(), 'Text edit')

    def _create_actions(self):
        """Create actions for menubar and toolbars"""
        self.actions = dict()

        # Exit application action
        exit = self.actions.setdefault('exit', 
                                       QAction(self.icons['exit'], 'Exit', self))
        exit.setShortcut(self.shortcut_exit)
        exit.setStatusTip('Exit')
        exit.triggered.connect(self.close)

        # Open application action
        exit = self.actions.setdefault('open', 
                                       QAction(self.icons['open'], 'Open', self))
        exit.setShortcut(self.shortcut_open)
        exit.setStatusTip('Open')
        # exit.triggered.connect(self.dia)

    def _create_icons(self):
        icons = dict()
        self.icons = icons

        # Populate icons
        base_dir = Path(__file__).parent / 'icons' / 'dark'
        paths = {
            'exit': base_dir / 'actions' / 'application-exit.svg',
            'open': base_dir / 'actions' / 'document-open.svg',
        }
        for name, item in paths.items():
            icons[name] = (QIcon(QPixmap(str(item)))  
                           if isinstance(item, Path) else item)

    def _create_menubar(self):
        """Create menubar for the main window"""
        # Create the menubar
        self.menubar = self.menuBar()

        # Configure the menubar
        self.menubar.setFont(self.get_font('menubar'))
        self.menubar.setNativeMenuBar(self.menubar_native)  # macOS

        # Populate menubar
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(self.actions['exit'])

    def _create_toolbar(self):
        """Create toolbar for the main window"""
        # Create the toolbar
        self.toolbar = QToolBar('toobar')
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
        
        # Add toolbar actions
        self.toolbar.addAction(self.actions['open'])
        self.toolbar.addAction(self.actions['exit'])

        # Configure toolbar
        font = self.get_font('toolbar')
        self.toolbar.setFont(font)

    def _create_central_widget(self):
        """Create the workspace central widget with project files list and work views"""
        self.central_widget = QWidget()

        # Create sub-widgets
        self._create_project_list()
        self._create_tabs()

        # Format the widgets in the workspace
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.tabs)
        hlayout.addWidget(self.project_list)

        self.central_widget.setLayout(hlayout)

    def _create_project_list(self):
        """Create the project listing widget"""
        self.project_list = QListWidget()

        # Configure project list settings
        font = self.get_font('project_list')
        self.project_list.setFont(font)

        width = font.pointSize() * self.project_list_width
        self.project_list.setFixedWidth(width)

        # Add project list items
        self.project_list.addItem('Item 1')

    def _create_tabs(self):
        """Create the tabs widget"""
        self.tabs = QTabWidget()

        # Configure the tabs
        self.tabs.setFont(self.get_font('tabs'))
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
        return self.fonts[match_names[0]] if match_names else self.fonts['default']