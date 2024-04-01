"""
Type definitions
"""
import typing as t

__all__ = ('FilePaths',)

#: A listing of filepaths
FilePaths = t.Iterable[t.Union[str, 'pathlib.Path']]
