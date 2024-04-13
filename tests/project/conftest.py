"""Project fixtures"""

import os
import csv

import pytest

from xamin.project import Entry, TextEntry, BinaryEntry, CsvEntry


@pytest.fixture(params=["text", "binary", "csvfile"])
def entry(request, tmp_path) -> TextEntry:
    # Create a test text document
    if request.param == "text":
        data = "This is my\ntest text file."
        test_file = tmp_path / "test.txt"
        test_file.write_text(data)
        return TextEntry(test_file)

    elif request.param == "binary":
        data = os.urandom(16)  # 16-bytes of binary
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(data)
        return BinaryEntry(test_file)

    elif request.param == "csvfile" or request.param == "tsvfile":
        data = [[str(i) for i in range(6)] for j in range(8)]
        if "csvfile":
            dialect = csv.get_dialect("excel")
            test_file = tmp_path / "test.csv"
        elif "tsvfile":
            dialect = csv.get_dialect("excel-tab")
            test_file = tmp_path / "test.tsv"
        else:
            raise AssertionError("Unknown dialect")

        with open(test_file, "w") as f:
            writer = csv.writer(f, dialect=dialect)
            writer.writerows(data)
        return CsvEntry(test_file)

    else:
        raise AssertionError("Unknown type")


@pytest.fixture(params=[Entry, TextEntry, BinaryEntry, CsvEntry])
def entry_cls(request) -> Entry:
    """A listing of the Entry classes"""
    return request.param
