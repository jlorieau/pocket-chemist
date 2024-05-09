"""
Tests for FileExplorerSidebar
"""

from pathlib import Path

import pytest
from PyQt6.QtCore import QItemSelectionModel

from xamin.gui.activities.explorer import FileExplorerActivity


@pytest.fixture
def setup_fileexplorer(qtbot):
    """Factory wrapper to setup a file explorer with the given file selected in the
    view."""

    def _setup_fileexplorer(path: str | Path):
        path = Path(path)

        # Setup the file explorer activity
        explorer = FileExplorerActivity(rootpath=path.parent)
        sidebar = explorer.sidebars[0]
        qtbot.addWidget(sidebar)

        # Find the model index corresponding to the path
        model = sidebar.model
        index = model.index(str(path))

        assert index.data() == path.name

        # Use the model index to select the item in the tree
        main = sidebar.widgets.main
        selection_model = main.selectionModel()
        selection_model.select(index, QItemSelectionModel.SelectionFlag.Select)

        return explorer

    _setup_fileexplorer.__doc__ = setup_fileexplorer.__doc__
    return _setup_fileexplorer


def test_selected_filepaths(tmp_path, setup_fileexplorer):
    """Test the FileExplorerSidebar test_selected_filepaths method"""
    # Create a FileExplorer activity and get the sidebar view
    explorer = setup_fileexplorer(tmp_path)
    sidebar = explorer.sidebars[0]

    # Check that the selected_filepaths returns the same file
    paths = sidebar.selected_filepaths()
    assert len(paths) == 1
    assert paths == [tmp_path]
