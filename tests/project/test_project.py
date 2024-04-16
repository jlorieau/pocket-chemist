"""Tests for Project classes"""

import yaml
import re
import pathlib
from pathlib import Path
from collections import OrderedDict

from xamin.project import Project, TextEntry
from xamin.project.project import (
    path_constructor,
    path_representer,
    project_representer,
    project_representer_no_relpath,
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
    loader.add_constructor("!path", path_constructor)

    # Convert to yaml text and check the dump
    text = yaml.dump(path, Dumper=dumper)
    assert text == "\n- ".join(("!path",) + path.parts) + "\n"

    # Convert from yaml and check loaded path
    load = yaml.load(text, Loader=loader)
    assert path == load


def test_project_constructor_representer(text_entry):
    """Test the project_constructure and project_representer functions"""
    # Create a project with entries
    project_filepath = text_entry.path.with_suffix(".proj")
    project = Project(path=project_filepath, entries=(text_entry,))

    # Setup the dumper
    dumper = yaml.SafeDumper
    dumper.add_representer(pathlib.PosixPath, path_representer)  # Needed for paths
    dumper.add_representer(pathlib.WindowsPath, path_representer)  # Needed for paths
    dumper.add_representer(Project, project_representer_no_relpath)

    # Setup the loader
    loader = yaml.SafeLoader
    loader.add_constructor("!path", path_constructor)
    loader.add_constructor("!Project", project_constructor)

    # Convert to yaml text and check the dump
    text = yaml.dump(project, Dumper=dumper)

    # Try to recreate the project from the yaml text
    load = yaml.load(text, Loader=loader)
    assert project == load

    # Next, if we try to use the normal project_representer, then the path of
    # entries are relative to the project path
    dumper.add_representer(Project, project_representer)

    # Convert to yaml text and check the dump
    text = yaml.dump(project, Dumper=dumper)

    # Try to recreate the project from the yaml text
    load = yaml.load(text, Loader=loader)
    assert project != load
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

    project_entry = list(project.entries.values())[0]

    assert type(project_entry) == type(entry)
    assert project_entry.path == entry.path
    assert project_entry.data == entry.data


def test_project_yaml_loader_entry(entry):
    """Test the Yaml loader for entries"""
    text = f"!{entry.__class__.__name__}\npath:\n- {entry.path.name}\n"

    # Generate python from yaml
    load = yaml.load(text)
    assert entry.path.name == load.path.name
    assert entry.__class__ == load.__class__


def test_project_yaml_dumper_entry(entry):
    """Test the Yaml dumper for entries"""
    path = entry.path

    # Generate yaml
    text = yaml.dump(entry)

    # Check the yaml format
    if entry.__class__ == Project:
        match = """
        !Project
        meta:
        - - version
          - 0.1.10
        entries:
        - - test.yaml
          - !YamlEntry
            path:
            - test.yaml
        - - test.csv
          - !CsvEntry
            path:
            - test.csv
        - - test.txt
          - !TextEntry
            path:
            - test.txt
        - - test.bin
          - !BinaryEntry
            path:
            - test.bin
        """
        # Strip indentation and leading newline
        match = re.sub(r"^\s{8}", "", match, flags=re.MULTILINE).lstrip()

        assert text == match
    else:
        match = f"""
        !{entry.__class__.__name__}
        path:
        - {path.name}
        """
        # Strip indentation and leading newline
        match = re.sub(r"^\s{8}", "", match, flags=re.MULTILINE).lstrip()

        assert text == match
