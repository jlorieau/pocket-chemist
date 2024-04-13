"""Tests for the Entry classes"""

import inspect

import pytest
from xamin.project import Entry, TextEntry, BinaryEntry, CsvEntry


def test_entry_suclasses():
    """Test the Entry.subclasses() static method"""
    subclasses = Entry.subclasses()

    assert (1, TextEntry) in subclasses
    assert (1, BinaryEntry) in subclasses
    assert (2, CsvEntry) in subclasses


def test_entry_depth():
    """Test the Entry.depth() baseclass method."""
    assert Entry.depth() == 0
    assert TextEntry.depth() == 1
    assert BinaryEntry.depth() == 1
    assert CsvEntry.depth() == 2


def test_entry_repr(entry):
    """Test the Entry __repr__ method."""
    assert repr(entry) == f"{entry.__class__.__name__}(path='{entry.path}')"


def test_entry_is_type(entry):
    """Test the Entry.is_type class method."""
    if isinstance(entry, TextEntry):
        assert TextEntry.is_type(entry.path)
        assert not BinaryEntry.is_type(entry.path)
    elif isinstance(entry, BinaryEntry):
        assert BinaryEntry.is_type(entry.path)
        assert not TextEntry.is_type(entry.path)


def test_entry_load(entry):
    """Test the Entry loading of a file"""
    assert len(entry.data) > 0

    if isinstance(entry, CsvEntry):
        assert isinstance(entry.data, list)
        assert entry.shape == (len(entry.data), len(entry.data[0]))
    elif isinstance(entry, TextEntry):
        assert isinstance(entry.data, str)
        assert entry.shape == (len(entry.data),)
    elif isinstance(entry, BinaryEntry):
        assert isinstance(entry.data, bytes)
        assert entry.shape == (len(entry.data),)


def test_entry_is_unsaved(entry):
    """Test the Entry is_unsaved property"""
    # Prepare extra data by type
    if isinstance(entry, CsvEntry):
        extra = [10, 11, 12, 13, 14, 15]
    elif isinstance(entry, TextEntry):
        extra = "some extra stuff"
    elif isinstance(entry, BinaryEntry):
        extra = b"some extra stuff"

    # Data should not be changed before the data method loads it
    assert not entry.is_unsaved

    # Get the original data
    original_data = entry.data
    assert not entry.is_unsaved

    # Modify it and change that the text_entry has changed
    entry.data = original_data + extra
    assert entry.is_unsaved

    # Reset it and the is_unsaved flag should change
    entry.data = original_data
    assert not entry.is_unsaved


def test_entry_save(entry):
    """Test the Entry save method"""
    # Prepare extra data by type
    if isinstance(entry, CsvEntry):
        extra = [10, 11, 12, 13, 14, 15]
    elif isinstance(entry, TextEntry):
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


def test_entry_no_path(entry_cls):
    """Test entry classes with no path"""
    # Don't run if it's an abstract class
    if inspect.isabstract(entry_cls):
        pytest.skip()

    # Instantiate the entry
    entry = entry_cls(path=None)

    assert entry.is_unsaved  # Entries without paths are unsaved and are changed
    assert repr(entry)  # entries can still be converted to strings
    assert entry.hash == ""  # An empty hash is returned
    assert entry.data is None  # It has no data
    assert entry.shape == ()  # The data has no shape

    # Trying to save raises an exception
    with pytest.raises(FileNotFoundError):
        entry.save()
