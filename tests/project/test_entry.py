"""Tests for the Entry classes"""

import os

import pytest

from xamin.project import TextEntry, BinaryEntry


@pytest.fixture(params=["text", "binary"])
def entry(request, tmp_path) -> TextEntry:
    # Create a test text document
    if request.param == "text":
        data = "This is my\ntest text file."
        test_file = tmp_path / ("test" + ".txt")
        test_file.write_text(data)
        return TextEntry(test_file)

    elif request.param == "binary":
        data = os.urandom(16)  # 16-bytes of binary
        test_file = tmp_path / ("test" + ".bin")
        test_file.write_bytes(data)
        return BinaryEntry(test_file)

    else:
        raise AssertionError("Unknown type")


def test_entry_load(entry):
    """Test the Entry loading of a file"""
    if isinstance(entry, TextEntry):
        assert isinstance(entry.data, str)
    elif isinstance(entry, BinaryEntry):
        assert isinstance(entry.data, bytes)
    assert len(entry.data) > 0
    assert entry.shape == (len(entry.data),)


def test_entry_is_changed(entry):
    """Test the Entry is_changed property"""
    # Prepare extra data by type
    if isinstance(entry, TextEntry):
        extra = "some extra stuff"
    elif isinstance(entry, BinaryEntry):
        extra = b"some extra stuff"

    # Data should not be changed before the data method loads it
    assert not entry.is_changed

    # Get the original data
    original_data = entry.data
    assert not entry.is_changed

    # Modify it and change that the text_entry has changed
    entry.data = original_data + extra
    assert entry.is_changed

    # Reset it and the is_changed flag should change
    entry.data = original_data
    assert not entry.is_changed


def test_entry_save(entry):
    """Test the Entry save method"""
    # Prepare extra data by type
    if isinstance(entry, TextEntry):
        extra = "some extra stuff"
    elif isinstance(entry, BinaryEntry):
        extra = b"some extra stuff"

    # Get the current mtime of the file to test when it is modified
    start_mtime = entry.path.stat().st_mtime

    # Load the data without unsaved changes should not modify the file
    entry.save()
    assert entry.path.stat().st_mtime == start_mtime

    # Changing the data produces unsaved changes, which can be saved
    entry.data = entry.data + extra
    entry.save()
    assert entry.path.stat().st_mtime >= start_mtime
