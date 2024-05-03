"""
Model and view for editing text code
"""

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QPlainTextEdit, QPlainTextDocumentLayout

from .base import BaseViewModel
from ...entry import Entry, TextEntry


__all__ = ("CodeEditViewModel",)


class TextEntryModel(QTextDocument):
    """A QTextDocument model to work with text entries.

    https://doc.qt.io/qtforpython-5/PySide2/QtGui/QTextDocument.html
    """

    entry: TextEntry

    def __init__(self, text_entry: TextEntry, *args, **kwargs):
        self.entry = text_entry

        # Load the text data into the document
        super().__init__(text_entry.data, *args, **kwargs)

        # Create the document layout
        self.setDocumentLayout(QPlainTextDocumentLayout(self))


class CodeEditView(QPlainTextEdit):
    """A QPlainTextEdit widget view for working with QTextEntry text entries.

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html
    """

    def __init__(self, document: TextEntryModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDocument(document)


class CodeEditViewModel(BaseViewModel):
    """The code edit view model"""

    model: TextEntryModel

    view: CodeEditView

    panel: None

    entry_compatibility = (TextEntry,)

    def __init__(self, entry: Entry, *args, **kwargs):
        self.model = TextEntryModel(text_entry=entry, *args, **kwargs)
        self.view = CodeEditView(document=self.model, *args, **kwargs)
        super().__init__(entry=entry, *args, **kwargs)
