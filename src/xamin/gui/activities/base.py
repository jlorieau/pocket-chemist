"""
Base classes for activities and sidebars that contain groupings of view(s), model(s) and
sidebars 
"""

import typing as t

from PyQt6.QtCore import Qt, QAbstractItemModel, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QAbstractItemView, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon, QAction

from ...entry import Entry

__all__ = ("BaseActivity", "BaseSidebarWidgets", "BaseSidebar")


class BaseActivity(QObject):
    """The Base Activity base class that groups view(s), model(s) and sidebars that
    work together

    Parameters
    ----------
    entries
        The data entries use for the activity
    """

    #: The data entries related to the activity
    entries: list[Entry]

    # processors
    # process_queue: list[Processor]

    #: The data model(s) for the view
    models: list[QAbstractItemModel]

    #: The view widget(s) associate with the model to display
    views: list[QWidget]

    #: The sidebar(s) associated with the view
    sidebars: list["BaseSidebar"]

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

    def activate(self, *args):
        """A slot to activate this activity"""
        pass

    def deactivate(self, *args):
        """A slot to deactivate this activity"""
        pass


#: Signal emitted when a new activity is created
BaseActivity.activity_created = pyqtSignal(BaseActivity)


## Sidebar classes


class BaseSidebarWidgets:
    """The namespace for BaseSidebar widgets"""

    __slots__ = ("heading", "main")

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

    #: The sidebar sub-widgets
    widgets: BaseSidebarWidgets

    #: Signal emitted when a data entry is loaded
    entry_loaded = pyqtSignal()

    #: A listing of subclasses
    _subclasses: t.ClassVar[list[type["BaseSidebar"]]] = []

    #: The widgets class to use
    _widgets_cls: t.ClassVar[type[BaseSidebarWidgets]]

    def __init_subclass__(
        cls, name: str, widgets_cls: type[BaseSidebarWidgets]
    ) -> None:
        """Initialize required class attributes for subclasses"""
        super().__init_subclass__()
        cls.name = name
        cls._widgets_cls = widgets_cls
        BaseSidebar._subclasses.append(cls)

    def __init__(self, *args, icon: t.Optional[QIcon] = None, **kwargs):
        super().__init__(*args, **kwargs)

        # Create the widgets
        self.widgets = self.__class__._widgets_cls()
        self.widgets.heading = QLabel(self.name)
        self.widgets.heading.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.widgets.main = self.reset_main_widget()

        # Place in VBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.widgets.heading)
        layout.addWidget(self.widgets.main)

        layout.setContentsMargins(0, 0, 0, 0)  # Remove padding in the layout
        layout.setSpacing(0)  # Remove space between widgets

        self.setLayout(layout)

        # Create the action
        if icon is not None:
            self.action = QAction(icon, self.name, self.parent())
        elif hasattr(self, "icon") and self.icon is not None:
            self.action = QAction(self.icon, self.name, self.parent())
        else:
            self.action = QAction(self.name, self.parent())

    @classmethod
    def subclasses(cls) -> tuple[type["BaseSidebar"], ...]:
        """Return all concrete subclasses of this class"""
        return tuple(BaseSidebar._subclasses)

    def reset_main_widget(self):
        """Create and reset the main widget of the sidebar"""
        return QWidget()
