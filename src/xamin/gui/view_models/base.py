"""
Abstract base class for ViewModels that contain groupings of view(s), model(s) and
panels 
"""

import typing as t

from PyQt6.QtCore import QAbstractItemModel
from PyQt6.QtWidgets import QAbstractItemView, QWidget

from ...entry import Entry

__all__ = ("BaseViewModel",)


class BaseViewModel:
    """The Base ViewModel componsite base class that groups view(s), model(s) and
    panels that work together"""

    #: The data model for the view
    model: QAbstractItemModel

    #: The view widget associate with the model to display
    view: QAbstractItemView

    #: The panel associated with the view
    panel: QWidget | None

    #: Listing of entry types compatible with this ViewModel
    entry_compatibility: t.Tuple[t.Type[Entry]]

    #: A listing of instantiated subclasses
    _subclasses = []

    def __init_subclass__(cls) -> None:
        BaseViewModel._subclasses.append(cls)

    def __init__(self, entry: Entry, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def subclasses() -> t.Tuple[t.Type["BaseViewModel"]]:
        """Return a tuple of concrete BaseViewModel subclasses"""
        return tuple(BaseViewModel._subclasses)
