"""Tests for Project classes"""

import yaml
import pathlib
from pathlib import Path
from collections import OrderedDict

from xamin.entry import Project, TextEntry
from xamin.entry.project import (
    path_constructor,
    path_representer,
    odict_representer,
    odict_constructor,
    project_representer,
    project_constructor,
)


def test_path_constructor_representer(tmp_path):
    """Test the path_constructor and path_representer functions"""
    path = Path(tmp_path)

    # Setup the dumper
    dumper = yaml.SafeDumper
    dumper.add_representer(pathlib.PosixPath, path_representer)
    dumper.add_representer(pathlib.WindowsPath, path_representer)

    # Setup the loader
    loader = yaml.SafeLoader
    loader.add_constructor("!Path", path_constructor)

    # Convert to yaml text and check the dump
    text = yaml.dump(path, Dumper=dumper)
    assert text == "\n- ".join(("!Path",) + path.parts) + "\n"

    # Convert from yaml and check loaded path
    load = yaml.load(text, Loader=loader)
    assert path == load


def test_odict_constructor_representer(tmp_path, dedent):
    """Test the odict_constructor and odict_representer functions"""
    # Setup the dumper
    dumper = yaml.SafeDumper
    dumper.add_representer(OrderedDict, odict_representer)

    # Setup the loader
    loader = yaml.SafeLoader
    loader.add_constructor("!OrderedDict", odict_constructor)

    # Convert to yaml text and check the dump
    odict = OrderedDict((("a", 1), ("c", 2)))
    odict["b"] = OrderedDict((("d", 4),))
    text = yaml.dump(odict, Dumper=dumper)

    answer = (
        dedent(
            """
        !OrderedDict
        - - a
          - 1
        - - c
          - 2
        - - b
          - !OrderedDict
            - - d
              - 4
        """,
            spaces=8,
        )
        + "\n"
    )

    assert text == answer

    # Convert from yaml and check loaded path
    load = yaml.load(text, Loader=loader)
    assert odict == load


def test_project_constructor_representer(tmp_path, text_entry):
    """Test the project_constructure and project_representer functions"""
    test_file = tmp_path / "test.proj"

    # Create a project with entries. Set the path after create to avoid loading
    # from a non-existant file and raising an exception
    project_filepath = text_entry.path.with_suffix(".proj")
    project = Project(path=None, entries=(text_entry,))
    project.path = project_filepath

    # Setup the dumper
    dumper = yaml.SafeDumper
    dumper.add_representer(pathlib.PosixPath, path_representer)  # Needed for paths
    dumper.add_representer(pathlib.WindowsPath, path_representer)  # Needed for paths
    dumper.add_representer(OrderedDict, odict_representer)
    dumper.add_representer(Project, project_representer)

    # Setup the loader
    loader = yaml.SafeLoader
    loader.add_constructor("!Path", path_constructor)
    loader.add_constructor("!OrderedDict", odict_constructor)
    loader.add_constructor("!Project", project_constructor)

    # Convert to yaml text and check the dump
    text = yaml.dump(project, Dumper=dumper)

    # Try to recreate the project from the yaml text
    load = yaml.load(text, Loader=loader)

    assert isinstance(load, Project)
    assert project.path == load.path
    assert project.meta == load.meta

    assert project.entries["test.txt"] == load.entries["test.txt"]
    assert project.entries == load.entries

    assert project == load

    # Next, if we try to use the normal project_representer, then the path of
    # entries are relative to the project path
    dumper.add_representer(Project, project_representer)

    # Convert to yaml text and check the dump
    text = yaml.dump(project, Dumper=dumper)

    # Try to recreate the project from the yaml text
    load = yaml.load(text, Loader=loader)

    assert project == load
    assert project.path == load.path
    assert project.meta == load.meta
    assert len(project.entries) == len(load.entries)
    assert [e.path for e in project.entries.values()] == [
        load.path.parent / e.path for e in load.entries.values()
    ]


def test_project_setup():
    """Test the instantiation and setup of new projects"""
    project = Project()

    # Current program version
    assert "version" in project.meta
    assert isinstance(project.meta["version"], str)


def test_project_state(project_entry):
    """Test the project __getstate__ and __setstate__ methods"""
    # Generate the state, and try to reconstruct a project from the state
    state = project_entry.__getstate__()

    loaded = Project()
    loaded.__setstate__(state)

    # Check the new loaded project
    assert project_entry.path == loaded.path
    assert project_entry.meta == loaded.meta
    assert len(project_entry.entries) == len(loaded.entries)

    for name_a, name_b in zip(project_entry.entries, loaded.entries):
        entry_a = project_entry.entries[name_a]
        entry_b = loaded.entries[name_b]

        assert name_a == name_b
        assert entry_a.__class__ == entry_b.__class__
        assert entry_a.path == entry_b.path


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

    # Readding an entry doesn't create a new entry
    project.add_entries(yaml_entry)
    assert len(project.entries) == 3


def test_project_add_files(entry):
    """Test the project.add_files method"""
    # Create a project and add an entry
    project = Project()
    project.add_files(entry.path)

    assert len(project.entries) == 1

    _, project_entry = project.entries.popitem()

    assert type(project_entry) == type(entry)
    assert project_entry.path == entry.path
    assert project_entry.data == entry.data
