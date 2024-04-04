"""
The main (root) window 
"""
import typing as t

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QStatusBar, QVBoxLayout, QHBoxLayout, QWidget,
                             QMenuBar, QMenu, QTextEdit, QToolBar)
from PyQt6.QtGui import QIcon, QAction
from thatway import Setting

__all__ = ('MainWindow',)

class MainWindow(QMainWindow):
    """The main (root) window"""

    #: Main window settings
    window_width = Setting(400, desc="Default window width")
    window_height = Setting(400, desc="Default window height")

    #: Central widget of the main window
    central_widget: QWidget

    #: Actions for menu and tool bars
    actions: t.Dict[str, QAction]

    #: Default keyboard shortcuts for actions
    shortcut_exit = Setting('Ctrl+Q', desc="Exit shortcut")

    #: Menu bar for the main window
    menubar: QMenuBar

    #: Tool bar for the main window
    toolbar: QToolBar

    #: Status bar for the main window
    statusbar: QStatusBar

    def __init__(self):
        super().__init__()

        # Populate default mutables
        self.actions = dict()

        # Configure the main window
        self.setWindowTitle("xamin")
        self.resize(self.window_width, self.window_height)

        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        self._create_actions()
        self._create_menubar()
        self._create_toolbar()

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()

    def _create_actions(self):
        """Create actions for menubar and toolbars"""
        # Exit application action
        exit = self.actions.setdefault('exit', 
                                       QAction(QIcon('exit24.png'), 'Exit', self))
        exit.setShortcut(self.shortcut_exit)
        exit.setStatusTip('Exit')
        exit.triggered.connect(self.close)

    def _create_menubar(self):
        """Create menubar for the main window"""
        # Create the menubar
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)  # macOS

        # Populate menubar
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(self.actions['exit'])

    def _create_toolbar(self):
        """Create toolbar for the main window"""
        # Populate toolbar
        self.toolbar = self.addToolBar('E&xit')
        self.toolbar.addAction(self.actions['exit'])



