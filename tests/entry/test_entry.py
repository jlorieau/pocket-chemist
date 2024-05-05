"""Tests for the Entry classes"""

import inspect
from copy import deepcopy

import pytest
from xamin.entry import (
    Entry,
    MissingPath,
    FileChanged,
)


def test_entry_suclasses(entry):
    """Test the Entry.subclasses() static method"""
    subclasses = Entry.subclasses()
    assert entry.__class__ in subclasses


def test_entry_depth(entry):
    """Test the Entry.score() class method."""
    entry_cls = entry.__class__

    # Concrete classes should have a score higher than the base score of 0
    assert entry_cls.score() > 0

    if entry_cls.__name__ in ("TextEntry", "BinaryEntry"):
        # These classes are generic have lower score than more specialize classes
        assert entry_cls.score() == 5
    else:
        # Other concrete classes should have a score of 10 higher than the base class
        parent_cls = entry_cls.__mro__[1]
        assert entry_cls.score() == parent_cls.score() + 10


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


def test_is_unsaved(entry, add_extra):
    """Test the Entry is_unsaved property"""
    # Data should not be changed before the data method loads it
    assert not entry.is_unsaved

    # Get the original data
    original_data = deepcopy(entry.data)
    assert not entry.is_unsaved

    # Modify it and change that the text_entry has changed
    add_extra(entry)

    assert entry.is_unsaved

    # Reset it and the is_unsaved flag should change
    if isinstance(entry.data, dict):
        entry.data.clear()
        entry.data.update(original_data)
    else:
        entry.data = original_data

    assert not entry.is_unsaved


def test_is_stale(entry):
    """Test the Entry is_stale property"""
    # Create a new, empty entry
    new = entry.__class__()

    # Make sure the new entry is a defaul
    if hasattr(new, "_data"):
        del new._data

    # Before data is loaded, the entry is_stale--i.e. it needs to be loaded
    assert new.path is None  # No path specified, data needs to be loaded
    assert not hasattr(new, "_data")  # No data specified
    assert new.is_stale

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


@pytest.mark.parametrize("order", ("forward", "backward"))
def test_entry_load_file_newer(entry, add_extra, order):
    """Test the re-loading of a file that has changed when the data has been updated"""
    # (Re-)load the data
    entry.load()

    # 1. Check that entry has loaded data and a hash
    assert entry._data_mtime
    assert entry._loaded_hash

    assert not entry.is_file_newer
    assert not entry.is_unsaved

    if order == "forward":
        # 2. Touch the file (is_file_newer is True, is_unsaved is False)
        entry.path.touch()

        assert entry.is_file_newer
        assert not entry.is_unsaved

        # 3. Change the data (is_file_newer is False, is_unsaved is True)
        #    This triggers an update before adding the data, so is_file_newer is False
        add_extra(entry)

        assert not entry.is_file_newer
        assert entry.is_unsaved

    else:
        # 2. Change the data (is_file_newer is False, is_unsaved is True)
        add_extra(entry)

        assert not entry.is_file_newer
        assert entry.is_unsaved

        entry.path.touch()

        assert entry.is_file_newer
        assert entry.is_unsaved

        # 4. Try loading and check for exception
        with pytest.raises(FileChanged):
            entry.load()


def test_entry_save(entry, add_extra):
    """Test the Entry save method"""

    # Get the current mtime of the file to test when it is modified
    entry.data  # make sure the data is loaded the data
    start_mtime = entry.path.stat().st_mtime

    # The entry does not have unsaved changes
    assert not entry.is_unsaved
    assert not entry.is_stale
    entry.save()
    assert entry.path.stat().st_mtime == start_mtime

    # Changing the data produces unsaved changes, which can be saved
    add_extra(entry)

    assert entry.is_unsaved
    assert not entry.is_stale  # entry's data is newer than the file

    entry.save()
    assert entry.path.stat().st_mtime >= start_mtime
