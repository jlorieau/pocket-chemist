"""Tests for the Entry classes"""

import typing as t

import pytest

from xamin.project import TextEntry


@pytest.fixture
def text_entry(tmp_path) -> TextEntry:
    # Create a test text document
    text = "This is my\ntest text file."
    test_file = tmp_path / "test.txt"
    test_file.write_text(text)
    return TextEntry(test_file)


def test_textentry_load(text_entry):
    """Test the TextEntry loading of a file"""
    assert isinstance(text_entry.data, str)
    assert len(text_entry.data) > 0
    assert text_entry.shape == (len(text_entry.data),)


def test_textentry_is_changed(text_entry):
    """Test the TextEntry is_changed property"""
    # Data should not be changed before the data method loads it
    assert not text_entry.is_changed

    # Get the original data
    original_data = text_entry.data
    assert not text_entry.is_changed

    # Modify it and change that the text_entry has changed
    text_entry.data = original_data + "some extra stuff"
    assert text_entry.is_changed

    # Reset it and the is_changed flag should change
    text_entry.data = original_data
    assert not text_entry.is_changed


def test_textentry_save(text_entry):
    """Test the TextEntry save method"""
    start_mtime = text_entry.path.stat().st_mtime

    # Load the data without unsaved changes should not modify the file
    text_entry.save()
    assert text_entry.path.stat().st_mtime == start_mtime

    # Changing the data produces unsaved changes, which can be saved
    text_entry.data = text_entry.data + "some extra stuff"
    text_entry.save()
    assert text_entry.path.stat().st_mtime > start_mtime
