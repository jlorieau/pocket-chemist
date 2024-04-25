"""
Model and view for editing text code
"""

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QPlainTextEdit
from pluggy import HookimplMarker

from ...entry import TextEntry


__all__ = ("QCodeEdit",)


# Setup the plug-in hook marker
hookimpl = HookimplMarker("xamin")


# Setup the plugin
@hookimpl
def add_entry_views(entry_views):
    """Add compatible views for data entries"""
    entry_views = entry_views if entry_views is not None else dict()

    # Add the view to compatible entry classes
    for cls in (TextEntry,):
        views = entry_views.setdefault(cls, set())
        views.add(QPlainTextEdit)

    return entry_views


# Define classes
class QTextEntry(QTextDocument):
    """A QTextDocument model to work with text entries.

    https://doc.qt.io/qtforpython-5/PySide2/QtGui/QTextDocument.html
    """

    entry: TextEntry

    def __init__(self, text_entry: TextEntry, *args, **kwargs):
        self.entry = text_entry

        # Load the text data into the document
        super().__init__(text=text_entry.data, *args, **kwargs)


class QCodeEdit(QPlainTextEdit):
    """A QPlainTextEdit widget view for working with QTextEntry text entries.

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html
    """

    #: A listing of Entry classes which can work for this view
    available_entries = [TextEntry]

    #: Model class to be used with this view
    model_cls = QTextEntry

    def __init__(self, text_entry: TextEntry, *args, **kwargs):
        super().__init__(*args, **args)

        # Set the document model
        document = QTextEntry(text_entry)
        self.setDocument(document)
