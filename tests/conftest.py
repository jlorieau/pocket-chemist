"""General fixtures for the repo"""

# mypy: ignore-errors

import re
import os
import csv
import yaml

import pytest

from xamin.entry import (
    Entry,
    TextEntry,
    PythonEntry,
    HtmlEntry,
    XmlEntry,
    BinaryEntry,
    CsvEntry,
    YamlEntry,
    Project,
)
from xamin.utils.dict import recursive_update


@pytest.fixture
def dedent():
    """Dedent the start of all lines in the given text by the specified number of
    spaces.

    Parameters
    ----------
    spaces
        The number of spaces to remove from the start of lines
    strip_ends
        If True (default), remove whitespace at the start and end of the text
    """

    def _dedent(text, spaces=4, strip_ends=True):
        print()
        dedented = re.sub(r"^\s{" + str(spaces) + "}", "", text, flags=re.MULTILINE)
        return dedented.strip() if strip_ends else dedented

    _dedent.__doc__ = dedent.__doc__
    return _dedent


@pytest.fixture
def text_entry(tmp_path) -> TextEntry:
    """An temporary instance of a TextEntry"""
    data = "This is my\ntest text file."
    test_file = tmp_path / "test.txt"
    test_file.write_text(data)
    return TextEntry(test_file)


@pytest.fixture
def python_entry(tmp_path) -> PythonEntry:
    """An temporary instance of a PythonEntry"""
    data = "import os\n"
    test_file = tmp_path / "test.py"
    test_file.write_text(data)
    return PythonEntry(test_file)


@pytest.fixture
def html_entry(tmp_path) -> HtmlEntry:
    """An temporary instance of a HtmlEntry"""
    data = "<html></html>"
    test_file = tmp_path / "test.html"
    test_file.write_text(data)
    return HtmlEntry(test_file)


@pytest.fixture
def xml_entry(tmp_path) -> XmlEntry:
    """An temporary instance of a XmlEntry"""
    data = "<xml></xml>"
    test_file = tmp_path / "test.xml"
    test_file.write_text(data)
    return XmlEntry(test_file)


@pytest.fixture
def binary_entry(tmp_path) -> BinaryEntry:
    """A temporary instance of a BinaryEntry"""
    data = os.urandom(16)  # 16-bytes of binary
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(data)
    return BinaryEntry(test_file)


@pytest.fixture
def csv_entry(tmp_path) -> CsvEntry:
    """A temporary instance of a CsvEntry"""
    data = [[str(i) for i in range(6)] for j in range(8)]
    dialect = csv.get_dialect("excel")
    test_file = tmp_path / "test.csv"
    with open(test_file, "w") as f:
        writer = csv.writer(f, dialect=dialect)
        writer.writerows(data)

    return CsvEntry(test_file)


@pytest.fixture
def yaml_entry(tmp_path) -> YamlEntry:
    """A temporary instance of a YamlEntry"""
    d = {"a": 1, "b": {"c": 2, "d": 3}}
    text = yaml.dump(d)
    test_file = tmp_path / "test.yaml"
    with open(test_file, "w") as f:
        test_file.write_text(text)
    return YamlEntry(test_file)


@pytest.fixture
def project_entry(tmp_path, yaml_entry, csv_entry, text_entry, binary_entry) -> Project:
    """A temporary instance of a Project"""
    test_file = tmp_path / "test.proj"
    project = Project(entries=(yaml_entry, csv_entry, text_entry, binary_entry))
    project.path = test_file
    project.save()
    return project


@pytest.fixture
def add_extra():
    """Add extra data to the entry"""

    def _extra(entry):
        entry_type = type(entry)

        if entry_type == TextEntry:
            entry.data += "some extra stuff"
        elif entry_type == BinaryEntry:
            entry.data += b"some extra stuff"
        elif entry_type == CsvEntry:
            entry.data += [[10, 11, 12, 13, 14, 15]]
        elif entry_type == YamlEntry:
            recursive_update(entry.data, {"e": 6, "f": 6})
        elif entry_type == PythonEntry:
            entry.data += "import sys\n"
        elif entry_type == HtmlEntry:
            entry.data += "<html></html>"
        elif entry_type == XmlEntry:
            entry.data += "<xml></xml>"
        elif entry_type == Project:
            recursive_update(entry.data, {"meta": {"new": "value"}})
        else:
            raise NotImplementedError(
                f"Extra data for class "
                f"'{entry.__class__.__name__}' is not yet implement"
            )

    _extra.__doc__ = add_extra.__doc__
    return _extra


@pytest.fixture(params=[name for name in locals().keys() if name.endswith("_entry")])
def entry(request: pytest.FixtureRequest) -> Entry:
    """Generator to retrieve temporary, concrete instances of all entry types"""
    entry = request.getfixturevalue(request.param)

    if not isinstance(entry, Entry):
        pytest.skip()

    return entry


@pytest.fixture(params=[Entry, TextEntry, BinaryEntry, CsvEntry])
def entry_cls(request: pytest.FixtureRequest) -> Entry:
    """A listing of the Entry classes"""
    return request.param
