"""General utility fixtures for the repo"""

import re

import pytest


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
