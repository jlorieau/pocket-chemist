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
    if getattr(entry, "path", None) is not None:
        assert repr(entry) == f"{entry.__class__.__name__}(path='{entry.path}')"
    else:
        assert repr(entry) == f"{entry.__class__.__name__}(path=None)"


def test_entry_getstate(entry):
    """Test the Entry __getstate__ method"""
    assert entry.__getstate__() == {"path": entry.path}


def test_entry_setstate(entry):
    """Test the Entry __setstate__ method"""
    loaded = entry.__class__(path=None)
    loaded.__setstate__({"path": entry.path})
    assert entry == loaded


def test_entry_is_type(entry):
    """Test the Entry.is_type class methods."""
    assert entry.__class__.is_type(entry.path)


def test_entry_guess_type(entry):
    """Test the Entry.guess_type class method"""
    # For all entry types, the guess_type should match the entry's original class
    guessed_cls = entry.guess_type(entry.path)
    assert guessed_cls == type(entry)

    # None as a parameter won't work
    assert entry.guess_type(None) is None


def test_entry_load(entry):
    """Test the Entry loading of a file"""
    assert len(entry.data) > 0

    shape = entry.shape
    if len(shape) == 2:
        # 2-dimensional shape
        assert shape == (len(entry.data), len(entry.data[0]))
    elif len(shape) == 1:
        # 1-dimensional shape
        assert shape == (len(entry.data),)
    else:
        raise NotImplementedError("Other data shapes are not yet implemented")


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


def test_is_unsaved(entry, extra_data):
    """Test the Entry is_unsaved property"""
    # Load the extra data for entry
    extra = extra_data(entry)

    # Data should not be changed before the data method loads it
    assert not entry.is_unsaved

    # Get the original data
    original_data = entry.data
    assert not entry.is_unsaved

    # Modify it and change that the text_entry has changed
    entry.data = (
        entry.data + extra if not isinstance(extra, dict) else entry.data | extra
    )
    assert entry.is_unsaved

    # Reset it and the is_unsaved flag should change
    entry.data = original_data
    assert not entry.is_unsaved


def test_entry_save(entry, extra_data):
    """Test the Entry save method"""
    # Load the extra data for entry
    extra = extra_data(entry)

    # Get the current mtime of the file to test when it is modified
    start_mtime = entry.path.stat().st_mtime

    # Load the data without unsaved changes should not modify the file
    entry.save()
    assert entry.path.stat().st_mtime == start_mtime

    # Changing the data produces unsaved changes, which can be saved
    entry.data = (
        entry.data + extra if not isinstance(extra, dict) else entry.data | extra
    )

    entry.save()
    assert entry.path.stat().st_mtime >= start_mtime
