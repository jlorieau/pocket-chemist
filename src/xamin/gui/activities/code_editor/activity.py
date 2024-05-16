"""
The Code Editor activity
"""

from PyQt6.QtWidgets import QWidget

from xamin.entry import TextEntry
from .model import CodeEditorModel
from .view import CodeEditorView
from ..base import BaseActivity

__all__ = ("CodeEditorActivity",)


class CodeEditorActivity(BaseActivity):
    """An activity to edit the text of files with source code highlighting"""

    entry_compatibility = (TextEntry,)

    def __init__(self, *entries: TextEntry, parent: QWidget | None = None):
        super().__init__(*entries, parent=parent)

        # Find applicable TextEntry objects from the given parameters
        text_entries = [entry for entry in self.entries if isinstance(entry, TextEntry)]

        # If a viable TextEntry was found, use it to construct the activity's model
        # and view
        if len(text_entries) > 0:
            entry = text_entries[0]

            # Create the text document model
            model = CodeEditorModel(entry=entry)
            self.models.append(model)

            # Create the code editor view
            view = CodeEditorView(document=model)
            self.views.append(view)
