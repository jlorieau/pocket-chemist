"""
Icons for GUI actions
"""

import re
from types import SimpleNamespace
from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap

icons_basedir = Path(__file__).parent

# Create the icons namespaces
icons = None

re_underscore = re.compile(r"-")
re_strip_suffix = re.compile(r"\..*")


def get_icons():
    """Generate the icons namespace with QIcon entries"""
    # Return the loaded icons, if available
    global icons
    if icons is not None:
        return icons

    icons = SimpleNamespace()
    icons.light = SimpleNamespace()
    icons.dark = SimpleNamespace()
    icons.current = icons.dark

    # Reconstruct the directory structure as nested namespaces
    for abs_filepath in icons_basedir.glob("**/*.svg"):
        rel_filepath = abs_filepath.relative_to(icons_basedir)

        # ex: ["dark", "actions", "document-open.svg"]
        parts = rel_filepath.parts

        # Select the namescape
        ns = icons
        for part in parts[:-1]:
            if not hasattr(ns, part):
                setattr(ns, part, SimpleNamespace())
            ns = getattr(ns, part)

        # Get the icon image filename and icon name, based on the filename
        filename = parts[-1]
        name = re_underscore.sub("_", filename)  # convert "-" to "_"
        name = re_strip_suffix.sub("", name)  # remove extensions

        # Create the icon
        icon = QIcon(QPixmap(str(abs_filepath)))
        setattr(ns, name, icon)

    return icons
