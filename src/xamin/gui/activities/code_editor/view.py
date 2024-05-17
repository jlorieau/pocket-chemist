"""
The Code Editor view
"""

import typing as t

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPlainTextEdit
from thatway import Setting

from .model import CodeEditorModel

__all__ = ("CodeEditorView",)


class CodeEditorView(QPlainTextEdit):
    """A code text editor viewer widget with syntax highlighting

    Parameters
    ----------
    document
        The document (CodeEditorModel) containing the text data to view
    """

    #: The default font to use for the code editor
    font_families: t.ClassVar[Setting] = Setting(
        ("Monaco", "Courier", "Courier New"),
        desc="Default font families for Code Editor",
    )
    font_size: t.ClassVar[Setting] = Setting(14, "Default font size for Code Editor")

    def __init__(self, document: CodeEditorModel) -> None:
        super().__init__()
        self.setDocument(document)

        # Configure the widget
        font = QFont(self.font_families, self.font_size)
        self.setFont(font)
