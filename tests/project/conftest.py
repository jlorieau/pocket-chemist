"""Project fixtures"""

import os
import csv
import yaml

import pytest

from xamin.project import Entry, TextEntry, BinaryEntry, CsvEntry, YamlEntry, Project


@pytest.fixture
def text_entry(tmp_path) -> TextEntry:
    """An temporary instance of a TextEntry"""
    data = "This is my\ntest text file."
    test_file = tmp_path / "test.txt"
    test_file.write_text(data)
    return TextEntry(test_file)


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


# @pytest.fixture
# def project_entry(tmp_path, yaml_entry, csv_entry, text_entry, binary_entry) -> Project:
#     """A temporary instance of a Project"""
#     test_file = tmp_path / "test.proj"
#     project = Project(
#         test_file, entries=(yaml_entry, csv_entry, text_entry, binary_entry)
#     )
#     project.save()
#     return project


@pytest.fixture
def extra_data():
    """Retrieve extra data for different entry types"""

    def _extra(entry):
        entry_type = type(entry)

        if entry_type == TextEntry:
            return "some extra stuff"
        elif entry_type == BinaryEntry:
            return b"some extra stuff"
        elif entry_type == CsvEntry:
            return [[10, 11, 12, 13, 14, 15]]
        elif entry_type == YamlEntry:
            return {"e": 6, "f": 6}
        elif entry_type == Project:
            return {"meta": {"new": "value"}}
        else:
            raise NotImplementedError(
                f"Extra data for class "
                f"'{entry.__class__.__name__}' is not yet implement"
            )

    _extra.__doc__ = extra_data.__doc__
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
