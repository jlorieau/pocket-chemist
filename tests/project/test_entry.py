"""Tests for the Entry classes"""

import inspect
from copy import deepcopy

import pytest
from xamin.project import Entry, TextEntry, BinaryEntry, CsvEntry, MissingPath
from xamin.utils.dict import recursive_update


def test_entry_suclasses():
    """Test the Entry.subclasses() static method"""
    subclasses = Entry.subclasses()
    print(subclasses)
    assert (1, TextEntry) in subclasses
    assert (1, BinaryEntry) in subclasses
    assert (1, CsvEntry) in subclasses


def test_entry_depth():
    """Test the Entry.depth() baseclass method."""
    assert Entry.depth() == 0
    assert TextEntry.depth() == 1
    assert BinaryEntry.depth() == 1
    assert CsvEntry.depth() == 1


def test_entry_getstate(entry):
    """Test the Entry __getstate__ method"""
    state = entry.__getstate__()
    assert state["path"] == entry.path


def test_entry_setstate(entry):
    """Test the Entry __setstate__ method"""
    loaded = entry.__class__(path=None)
    state = entry.__getstate__()
    loaded.__setstate__(state)
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
    assert entry.data == entry.default_data()  # It has default empty data

    # Trying to save raises an exception
    with pytest.raises(MissingPath):
        entry.save()


def test_is_unsaved(entry, extra_data):
    """Test the Entry is_unsaved property"""
    # Load the extra data for entry
    extra = extra_data(entry)

    # Data should not be changed before the data method loads it
    assert not entry.is_unsaved

    # Get the original data
    original_data = deepcopy(entry.data)
    assert not entry.is_unsaved

    # Modify it and change that the text_entry has changed
    if isinstance(extra, dict):
        recursive_update(entry.data, extra)
    else:
        entry.data += extra

    assert entry.is_unsaved

    # Reset it and the is_unsaved flag should change
    if isinstance(extra, dict):
        entry.data.clear()
        entry.data.update(original_data)
    else:
        entry.data = original_data
    assert not entry.is_unsaved


def test_is_stale(entry):
    """Test the Entry is_stale property"""
    # Create a new, empty entry
    new = entry.__class__()

    # Before data is loaded, the entry is_stale--i.e. it needs to be loaded
    assert new.is_stale
    assert not hasattr(new, "_date")  # No data, it needs to be loaded
    assert new.path is None  # No path specified, data needs to be loaded

    # Load the data from a path, and the new entry should no longer be stale
    new.path = entry.path
    new.load()

    assert not new.is_stale

    # But, if the file gets updated (touched), the data in new will become stale
    new.path.touch()
    assert new.is_stale


def test_entry_load(entry):
    """Test the Entry loading of a file"""
    # Get the generics/data type for the entry
    data_type = entry._generics_type()

    assert isinstance(entry.data, data_type)

    shape = entry.shape
    if len(shape) == 2:
        # 2-dimensional shape
        assert shape == (len(entry.data), len(entry.data[0]))
    elif len(shape) == 1:
        # 1-dimensional shape
        assert shape == (len(entry.data),)
    else:
        raise NotImplementedError("Other data shapes are not yet implemented")


def test_entry_save(entry, extra_data):
    """Test the Entry save method"""

    # Load the extra data for entry
    extra = extra_data(entry)

    # Get the current mtime of the file to test when it is modified
    entry.data  # make sure the data is loaded the data
    start_mtime = entry.path.stat().st_mtime

    # The entry does not have unsaved changes
    assert not entry.is_unsaved
    assert not entry.is_stale
    entry.save()
    assert entry.path.stat().st_mtime == start_mtime

    # Changing the data produces unsaved changes, which can be saved
    if isinstance(extra, dict):
        recursive_update(entry.data, extra)
    else:
        entry.data += extra

    assert entry.is_unsaved
    assert not entry.is_stale  # entry's data is newer than the file

    entry.save()
    assert entry.path.stat().st_mtime >= start_mtime
