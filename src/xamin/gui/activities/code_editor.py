"""
A text code editor activity
"""

import typing as t

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QPlainTextEdit, QPlainTextDocumentLayout

from .base import BaseActivity
from ...entry import TextEntry

__all__ = ("CodeEditorActivity",)


class CodeEditorModel(QTextDocument):
    """A text document data model for source code editing

    https://doc.qt.io/qtforpython-5/PySide2/QtGui/QTextDocument.html

    Parameters
    ----------
    entry
        The text data entry
    """

    entry: TextEntry

    def __init__(self, entry: TextEntry, *args, **kwargs):
        self.entry = entry

        # Load the text data into the document
        super().__init__(entry.data, *args, **kwargs)

        # Create the document layout
        self.setDocumentLayout(QPlainTextDocumentLayout(self))


class CodeEditorView(QPlainTextEdit):
    """A code text editor viewer widget with syntax highlighting

    Parameters
    ----------
    document
        The document (CodeEditorModel) containing the text data to view
    """

    def __init__(self, document: CodeEditorModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDocument(document)


class CodeEditorActivity(BaseActivity):
    """An activity to edit the text of files with source code highlighting"""

    #: The text document entries.
    #: Only the first entry is displayed
    entries: t.List[TextEntry]

    model: CodeEditorModel
    view: CodeEditorView
    sidebar = None

    entry_compatibility = (TextEntry,)

    def __init__(self, entry: TextEntry, *args, **kwargs):
        super().__init__(entry)
        self.model = CodeEditorModel(entry=entry, *args, **kwargs)
        self.view = CodeEditorView(document=self.model, *args, **kwargs)
