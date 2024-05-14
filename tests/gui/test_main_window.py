"""
Tests for the MainApplication and MainWindow classes.
"""

from xamin.gui.main_window import MainWindow


def test_main_window_widgets(qtbot):
    """Test the structure of widgets for the MainWindow"""
    win = MainWindow()
    widgets = win.widgets()

    assert len(widgets) > 0

    # Reset the widgets shouldn't create a new item
    new_widgets = win.widgets()

    mismatched_widgets = set()
    for name, widget in widgets.items():
        new_widget = new_widgets[name]
        if id(widget) != id(new_widget):
            mismatched_widgets.add(name)

    assert (
        len(mismatched_widgets) == 0
    ), f"The following widgets were re-created: {mismatched_widgets}"
