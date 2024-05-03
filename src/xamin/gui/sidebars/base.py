"""
Class for base panel widget and panel switcher
"""

import typing as t
from types import SimpleNamespace

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

__all__ = ("BaseSidebar",)


class BaseSidebar(QWidget):
    """Base Panel class to define the sidebar interface

    Parameters
    ----------
    heading
        The heading string of the sidebar
    toolbar_icon
        The icon to use in the toolbar
    """

    #: The name of the sidebar
    name: str

    #: The icon to identify the sidebar in the toolbar
    toolbar_icon: QIcon

    #: The sidebar sub-widgets
    #: widgets.heading  (the heading of the sidebar)
    #: widgets.main  (the main widget of the sidebar)
    widgets: SimpleNamespace

    #: Signal emitted when a file is opened.
    #: Arguments: Entry instance, ViewModel instance
    fileopen = pyqtSignal(object, object)

    #: A listing of subclasses
    _subclasses = []

    def __init_subclass__(
        cls, name: str, toolbar_icon: QIcon | None = None, **kwargs
    ) -> None:
        """Initialize required class attributes for subclasses"""
        cls.name = name
        cls.toolbar_icon = toolbar_icon
        BaseSidebar._subclasses.append(cls)
        return super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert hasattr(
            self, "name"
        ), f"{self.__class__.__name__} must have a class attribute name specified."

        # Create the widgets
        self.widgets = SimpleNamespace()
        self.widgets.heading = QLabel(self.name)
        self.widgets.heading.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.widgets.main = self.create_main_widget()

        # Create the models namespace
        self.models = SimpleNamespace()

        # Place in VBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.widgets.heading)
        layout.addWidget(self.widgets.main)

        layout.setContentsMargins(0, 0, 0, 0)  # Remove padding in the layout
        layout.setSpacing(0)  # Remove space between widgets

        self.setLayout(layout)

    @classmethod
    def subclasses(cls) -> t.Tuple["BaseSidebar"]:
        """Return all concrete subclasses of this class"""
        return tuple(BaseSidebar._subclasses)

    def create_main_widget(self):
        """Create the main widget of the sidebar"""
        return QWidget
