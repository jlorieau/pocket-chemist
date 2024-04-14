"""Tests for Project classes"""

from pathlib import Path
from collections import OrderedDict

from xamin.project import Project, TextEntry


def test_project_setup():
    """Test the instantiation and setup of new projects"""
    project = Project()

    # Current program version
    assert "version" in project.meta
    assert isinstance(project.meta["version"], str)


def test_project_assign_unique_names():
    """Test the Project.assign_unique_names method"""
    # Create some test entries
    entries = OrderedDict(
        (
            ("a", TextEntry(path=Path("/") / "usr" / "local" / "bin" / "file1")),
            ("b", TextEntry(path=Path("/") / "usr" / "local" / "bin" / "file2")),
            ("c", TextEntry(path=Path("/") / "usr" / "local" / "src" / "source.cpp")),
            ("d", TextEntry(path=Path("/") / "etc" / "http.conf")),
        )
    )

    project = Project(path=None, entries=entries)
    assert len(project.entries) > 0

    # 1. Assign and check names
    project.assign_unique_names()
    a = str(Path("/") / "usr" / "local" / "bin" / "file1")
    b = str(Path("/") / "usr" / "local" / "bin" / "file2")
    c = str(Path("/") / "usr" / "local" / "src" / "source.cpp")
    d = str(Path("/") / "etc" / "http.conf")

    assert list(project.entries.keys()) == [a, b, c, d]

    # 2. Try popping an element and the common denominator changes
    del project.entries[d]

    project.assign_unique_names()
    a = str(Path("bin") / "file1")
    b = str(Path("bin") / "file2")
    c = str(Path("src") / "source.cpp")
    assert list(project.entries.keys()) == [a, b, c]

    # 3. Try popping an element and the common denominator changes
    del project.entries[c]

    project.assign_unique_names()
    a = str(Path("file1"))
    b = str(Path("file2"))
    assert list(project.entries.keys()) == [a, b]

    # 4. Try removing a path from an entry
    project.entries[b].path = None

    project.assign_unique_names()
    a = str(Path("file1"))
    b = "<unsaved> (2)"
    assert list(project.entries.keys()) == [a, b]


def test_project_add_entries(yaml_entry, csv_entry, text_entry):
    """Test the project.add_entries method"""
    # Create a project with an entry
    project = Project(entries=(yaml_entry, csv_entry, text_entry))

    assert "entries" in project.data
    assert len(project.entries) == 3
    assert list(project.entries.keys()) == ["test.yaml", "test.csv", "test.txt"]
    assert project.entries["test.yaml"] == yaml_entry
    assert project.entries["test.csv"] == csv_entry
    assert project.entries["test.txt"] == text_entry


def test_project_add_files(entry):
    """Test the project.add_files method"""
    # Create a project and add an entry
    project = Project()
    project.add_files(entry.path)

    assert len(project.entries) == 1

    project_entry = list(project.entries.values())[0]

    assert type(project_entry) == type(entry)
    assert project_entry.path == entry.path
    assert project_entry.data == entry.data
