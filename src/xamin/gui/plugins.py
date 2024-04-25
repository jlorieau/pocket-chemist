"""Pluggy plug-in hook specifications and management"""

import typing as t

import pluggy
from PyQt6.QtWidgets import QWidget

from .views import code_editor
from ..project import Entry

hookspec = pluggy.HookspecMarker("xamin")

#: An type for entry-views dicts that have:
#:   key: Data entry classes (key)
#:   value: A set of corresponding gui view classes compatible with the entry class
EntryViewsType = t.Dict[Entry, t.Set[QWidget]]


@hookspec
def add_entry_views(entry_views: EntryViewsType | None):
    """Add compatible views for data entries"""
    entry_views = entry_views if entry_views is not None else dict()


def get_plugin_manager():
    """Retrieve and configure the plugin manager"""
    pm = pluggy.PluginManager("xamin")

    # add hook implementations
    pm.register(code_editor)

    return pm
