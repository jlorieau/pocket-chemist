"""
Icons for GUI actions
"""

import re
from types import SimpleNamespace
from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap

__all__ = ("Icons",)

_icons_basedir = Path(__file__).parent


_re_underscore = re.compile(r"-")
_re_strip_suffix = re.compile(r"\..*")


class Icons(SimpleNamespace):
    """Generate the icons namespace with QIcon entries"""

    #: Color schemes for icons
    light: SimpleNamespace
    dark: SimpleNamespace

    #: The currently selected color scheme
    current: SimpleNamespace

    def __init__(self):
        self.light = SimpleNamespace()
        self.dark = SimpleNamespace()
        self.current = self.dark

        # Reconstruct the directory structure as nested namespaces
        for abs_filepath in _icons_basedir.glob("**/*.svg"):
            rel_filepath = abs_filepath.relative_to(_icons_basedir)

            # ex: ["dark", "actions", "document-open.svg"]
            parts = rel_filepath.parts

            # Select the namescape
            ns = self
            for part in parts[:-1]:
                if not hasattr(ns, part):
                    setattr(ns, part, SimpleNamespace())
                ns = getattr(ns, part)

            # Get the icon image filename and icon name, based on the filename
            filename = parts[-1]
            name = _re_underscore.sub("_", filename)  # convert "-" to "_"
            name = _re_strip_suffix.sub("", name)  # remove extensions

            # Create the icon
            icon = QIcon(QPixmap(str(abs_filepath)))
            setattr(ns, name, icon)
