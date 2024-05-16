"""
The Code Editor view
"""

from PyQt6.QtWidgets import QPlainTextEdit

from .model import CodeEditorModel

__all__ = ("CodeEditorView",)


class CodeEditorView(QPlainTextEdit):
    """A code text editor viewer widget with syntax highlighting

    Parameters
    ----------
    document
        The document (CodeEditorModel) containing the text data to view
    """

    def __init__(self, document: CodeEditorModel) -> None:
        super().__init__()
        self.setDocument(document)
