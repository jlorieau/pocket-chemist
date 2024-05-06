"""
Tests for ViewSelector dialog windows
"""

from PyQt6.QtCore import Qt, QModelIndex

from xamin.gui.activities.explorer.dialogs import ActivitySelector


def test_class_to_name(qtbot):
    """Test the ActivitySelector class_to_name and name_to_class methods."""

    # Create a dummy activity selector instance
    selector = ActivitySelector(filepath="")

    class MyTestClass:
        pass

    # Create an activity selector instance

    assert selector.class_to_name(MyTestClass) == "My Test Class"
    assert selector.name_to_class("My Test Class") == MyTestClass


def test_find_entry_types(entry, qtbot):
    """Test the find_entry_types method"""
    # Create the selector
    selector = ActivitySelector(filepath="entry.path")
    qtbot.addWidget(selector)

    # Find the entry types. The top one should match the entry type passed in
    model = selector.find_entry_types(filepath=entry.path)

    cls_name = selector.class_to_name(entry.__class__)
    index = model.index(0, 0)
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == cls_name
