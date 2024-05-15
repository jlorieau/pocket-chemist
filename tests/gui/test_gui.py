"""
Tests for GUI classes.
"""

import pytest

from xamin.gui.main_window import MainWindow
from xamin.gui.activities.explorer.sidebar import FileExplorerSidebar


@pytest.mark.parametrize("cls", (MainWindow, FileExplorerSidebar))
def test_widgets(cls, qtbot):
    """Test GUI classes "widgets" property"""
    obj = cls()
    widgets = obj.widgets

    assert len(widgets) > 0

    # Reset the widgets shouldn't create a new item
    new_widgets = obj.widgets

    mismatched_widgets = set()
    for name, widget in widgets.items():
        new_widget = new_widgets[name]
        if id(widget) != id(new_widget):
            mismatched_widgets.add(name)

    assert len(mismatched_widgets) == 0, (
        f"The following widgets for '{cls.__name__}' were re-created: "
        f"{mismatched_widgets}"
    )
