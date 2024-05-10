"""
Tests for assets classes
"""

from xamin.gui.assets import Icons

from PyQt6.QtGui import QIcon


def test_icons(qtbot):
    """Test the Icons instantiation and attributes"""
    icons = Icons("dark")
    icons2 = Icons("dark")

    # Same object (i.e. singleton)
    assert id(icons) == id(icons2)

    # Test a random icon
    assert isinstance(icons.actions.document_open, QIcon)
