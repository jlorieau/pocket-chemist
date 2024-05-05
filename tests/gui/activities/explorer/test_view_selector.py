"""
Tests for ViewSelector dialog windows
"""

from xamin.gui.dialogs.view_selector import ViewSelector


def test_class_to_name():
    """Test the ViewSelector class_to_name and name_to_class methods."""

    class MyTestClass:
        pass

    assert ViewSelector.class_to_name(MyTestClass) == "My Test Class"
    assert ViewSelector.name_to_class("My Test Class") == MyTestClass
