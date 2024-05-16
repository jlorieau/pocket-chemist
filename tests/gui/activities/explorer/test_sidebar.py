"""
Tests for FileExplorerSidebar
"""

from pathlib import Path
from collections import namedtuple

import pytest
from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtWidgets import QDialog

from xamin.gui.activities import BaseActivity
from xamin.gui.activities.explorer import FileExplorerActivity


@pytest.fixture
def setup_fileexplorer(monkeypatch, qtbot):
    """Factory wrapper to setup a file explorer with the given file selected in the
    view.

    Parameters
    ----------
    path
        The file path to select in the sidebar's view
    activity_cls
        If specified, return the given activity_cls from the load_activity method
    entry_cls
        If specified, return the given entry_cls from the load_activity method
    """

    def _setup_fileexplorer(path: str | Path, activity_cls=None, entry_cls=None):
        path = Path(path)

        # Setup the file explorer activity
        explorer = FileExplorerActivity(rootpath=path.parent)
        sidebar = explorer.sidebars[0]
        qtbot.addWidget(sidebar)

        # 1. Modify the behavior of self.selected_filepaths
        # Find the model index corresponding to the path
        model = sidebar.model
        index = model.index(str(path))

        assert index.data() == path.name

        # Use the model index to select the item in the tree
        main = sidebar.main_widget
        selection_model = main.selectionModel()
        selection_model.select(index, QItemSelectionModel.SelectionFlag.Select)

        # 2. Modify the behavior of self.selected_filepaths
        class ActivitySelector:
            """Mock class for ActivitySelector dialog"""

            DialogCode = QDialog.DialogCode

            def __init__(self, *args, **kwargs):
                pass

            def exec(self):
                return QDialog.DialogCode.Accepted

            def selected_entry_type(self):
                return entry_cls

            def selected_activity_type(self):
                return activity_cls

        # Monkeypatch the dialog
        monkeypatch.setattr(
            "xamin.gui.activities.explorer.sidebar.ActivitySelector", ActivitySelector
        )

        return explorer

    _setup_fileexplorer.__doc__ = setup_fileexplorer.__doc__
    return _setup_fileexplorer


def test_selected_filepaths(tmp_path, setup_fileexplorer):
    """Test the FileExplorerSidebar selected_filepaths method"""
    # Create a FileExplorer activity and get the sidebar view
    explorer = setup_fileexplorer(tmp_path)
    sidebar = explorer.sidebars[0]

    # Check that the selected_filepaths returns the same file
    path = sidebar.selected_filepath()
    assert path == tmp_path


def test_load_activity(tmp_path, setup_fileexplorer):
    """Test the FileExplorerSidebar load_activity method"""
    MockEntry = namedtuple("MockEntry", "path")

    class MockActivity(BaseActivity):
        pass

    explorer = setup_fileexplorer(
        tmp_path, entry_cls=MockEntry, activity_cls=MockActivity
    )
    sidebar = explorer.sidebars[0]
    activity = sidebar.load_activity()
    entry = activity.entries[0]

    assert isinstance(activity, MockActivity)
    assert isinstance(entry, MockEntry)
