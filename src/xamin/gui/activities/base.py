"""
Base classes for activities and sidebars that contain groupings of view(s), model(s) and
sidebars 
"""

import typing as t

from PyQt6.QtCore import Qt, QAbstractItemModel, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QAbstractItemView, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon, QAction

from ...entry import Entry

__all__ = ("BaseActivity", "BaseSidebarWidgetsDict", "BaseSidebar")


class BaseActivity(QObject):
    """The Base Activity base class that groups view(s), model(s) and sidebars that
    work together

    Parameters
    ----------
    entries
        The data entries use for the activity
    """

    #: The data entries related to the activity
    entries: t.Sequence[Entry]

    # processors
    # process_queue: list[Processor]

    #: The data model(s) for the view
    models: t.Sequence[QAbstractItemModel]

    #: The view widget(s) associate with the model to display
    views: t.Sequence[QWidget]

    #: The sidebar(s) associated with the view
    sidebars: t.Sequence["BaseSidebar"]

    #: Whether the activity is "uncloseable"
    persistent: bool = False

    #: The parent widget
    parent: t.Callable[[QObject], QObject | None]

    #: Class attribute listing of entry types compatible with this Activity
    entry_compatibility: t.Tuple[t.Type[Entry], ...] = ()

    # Signals
    activity_created: pyqtSignal  # defined below

    #: A listing of subclasses
    _subclasses: list[type["BaseActivity"]] = []

    def __init_subclass__(cls) -> None:
        BaseActivity._subclasses.append(cls)

    def __init__(self, *entries: Entry, parent: QWidget | None = None):
        super().__init__(parent)

        # Configure attributes
        self.entries = list(entries)

        for attr in ("models", "views", "sidebars"):
            if not hasattr(self, attr):
                setattr(self, attr, [])

        # Emit the signal
        self.activity_created.emit(self)

    @staticmethod
    def subclasses() -> tuple[type["BaseActivity"], ...]:
        """Return a tuple of concrete BaseActivity subclasses"""
        return tuple(BaseActivity._subclasses)

    @staticmethod
    def compatibilities(entry_type: t.Type[Entry]) -> set[type["BaseActivity"]]:
        """A set of compatible Activity classes for the given entry type"""
        return set(
            cls
            for cls in BaseActivity.subclasses()
            if entry_type in cls.entry_compatibility
        )

    def has_view(self, views: t.Iterable[QAbstractItemView]) -> bool:
        """Whether the activity has the given view"""
        return len(self.views) > 0

    # Slots

    def activate(self) -> None:
        """A slot to activate this activity"""
        pass

    def deactivate(self) -> None:
        """A slot to deactivate this activity"""
        pass


#: Signal emitted when a new activity is created
BaseActivity.activity_created = pyqtSignal(BaseActivity)


## Sidebar classes


class BaseSidebarWidgetsDict(t.TypedDict):
    """The namespace for BaseSidebar widgets"""

    #: The sidebar heading widget
    heading: QLabel

    #: The sidebar main widget
    main: QWidget


class BaseSidebar(QWidget):
    """Base sidebar class to define the sidebar interface

    Parameters
    ----------
    name
        The name string of the sidebar
    toolbar_icon
        The icon to use in the toolbar
    """

    #: The name of the sidebar
    name: str

    #: The action associated with activating this sidebar
    action: QAction
    icon: QIcon | None

    #: Signal emitted when a data entry is loaded
    entry_loaded = pyqtSignal()

    #: A listing of subclasses
    _subclasses: t.ClassVar[list[type["BaseSidebar"]]] = []

    def __init_subclass__(cls, name: str) -> None:
        """Initialize required class attributes for subclasses"""
        super().__init_subclass__()
        cls.name = name
        BaseSidebar._subclasses.append(cls)

    def __init__(
        self,
        icon: QIcon | None = None,
        parent: QWidget | None = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ):
        super().__init__(parent=parent, flags=flags)

        # Load the widgets
        self.widgets

        # Create the action
        if icon is not None:
            self.action = QAction(icon, self.name, self.parent())
        elif hasattr(self, "icon") and self.icon is not None:
            self.action = QAction(self.icon, self.name, self.parent())
        else:
            self.action = QAction(self.name, self.parent())

    @property
    def heading_widget(self) -> QLabel:
        """The widget for the heading label"""
        heading = self.findChild(QLabel, "heading")
        if heading is None:
            heading = QLabel(self.name, parent=self)
            heading.setObjectName("heading")
            heading.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return heading

    @property
    def main_widget(self) -> QWidget:
        """The main sidebar widget"""
        main = self.findChild(QWidget, "main")
        if main is None:
            main = QWidget(parent=self)
            main.setObjectName("main")
        return main

    @property
    def widgets(self) -> BaseSidebarWidgetsDict:
        """Override parent method to return the File Explorer sidebar widgets"""
        heading = self.heading_widget
        main = self.main_widget

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.addWidget(heading)
            layout.addWidget(main)

            layout.setContentsMargins(0, 0, 0, 0)  # Remove padding in the layout
            layout.setSpacing(0)  # Remove space between widgets

            self.setLayout(layout)

        return {"heading": heading, "main": main}

    @classmethod
    def subclasses(cls) -> tuple[type["BaseSidebar"], ...]:
        """Return all concrete subclasses of this class"""
        return tuple(BaseSidebar._subclasses)

    def reset_main_widget(self) -> QWidget:
        """Create and reset the main widget of the sidebar"""
        return QWidget()
