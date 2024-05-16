"""
The Code Editor data model
"""

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QPlainTextDocumentLayout

from xamin.entry import TextEntry

__all__ = ("CodeEditorModel",)


class CodeEditorModel(QTextDocument):
    """A text document data model for source code editing

    https://doc.qt.io/qtforpython-5/PySide2/QtGui/QTextDocument.html

    Parameters
    ----------
    entry
        The text data entry
    """

    entry: TextEntry

    def __init__(self, entry: TextEntry) -> None:
        self.entry = entry

        # Load the text data into the document
        super().__init__(entry.data)

        # Create the document layout
        self.setDocumentLayout(QPlainTextDocumentLayout(self))
