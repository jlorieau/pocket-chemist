"""
Class for base panel widget and panel switcher
"""

import typing as t
from types import SimpleNamespace

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QStackedWidget, QLabel, QVBoxLayout, QSizePolicy

__all__ = ("BasePanel", "PanelStack")


class BasePanel(QWidget):
    """Base Panel class to define the panel interface

    Parameters
    ----------
    heading
        The heading string of the panel
    toolbar_icon
        The icon to use in the toolbar
    """

    #: The name of the panel
    name: str

    #: The icon to identify the panel in the toolbar
    toolbar_icon: QIcon

    #: The panel sub-widgets
    #: widgets.heading  (the heading of the panel)
    #: widgets.main  (the main widget of the panel)
    widgets: SimpleNamespace

    #: A listing of instantiated subclasses
    _subclasses = []

    #: The panel models

    def __init_subclass__(
        cls, name: str, toolbar_icon: QIcon | None = None, **kwargs
    ) -> None:
        """Initialize required class attributes for subclasses"""
        cls.name = name
        cls.toolbar_icon = toolbar_icon
        BasePanel._subclasses.append(cls)
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
        # self.widgets.heading.setSizePolicy(
        #     QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        # )

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
    def subclasses(cls) -> t.Tuple["BasePanel"]:
        """Return all concrete subclasses of this class"""
        return tuple(BasePanel._subclasses)

    def create_main_widget(self):
        """Create the main widget of the panel"""
        return QWidget


class PanelStack(QStackedWidget):
    """A stacked widget for the different panels"""
