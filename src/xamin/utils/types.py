"""
Type definitions
"""

import typing as t
from pathlib import Path

__all__ = ("FilePaths",)

#: A listing of filepaths
FilePaths = t.Iterable[str | Path]
