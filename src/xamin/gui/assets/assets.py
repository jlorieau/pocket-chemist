"""
A base class namespace for asset singletons
"""

from __future__ import annotations

import typing as t
import re
from types import SimpleNamespace
from pathlib import Path

from PyQt6.QtGui import QIcon
from loguru import logger

__all__ = ("Icons",)


class Assets:
    """An ABC asset singleton factory to provide isolated namespaces for GUI assets"""

    #: The relative path of assets
    relpath: Path

    #: The sub-directories below relpath containing the assets
    subdirs: tuple[str | Path, ...]

    #: The extensions of asset files
    extensions: tuple[str, ...]

    #: The assets namespace
    assets: SimpleNamespace

    #: Instances indexed by the path relative to 'relpath'
    _instances: t.Dict[Path, "Assets"] = dict()

    #: Whether to the instance is initialized.
    #: This sets the set __getattribute__ and __setattribute__
    _initialized = False

    #: Regexes for converting filenames to asset namespace attribute names
    _re_underscore = re.compile(r"-")
    _re_strip_suffix = re.compile(r"\..*")

    def __new__(cls, *subdirs: str | Path) -> Assets:
        """Create or retrieve a single assets instance

        Parameters
        ----------
        subdirs
            The sub-directories to find assets
        """
        path = cls.relpath.joinpath(*subdirs)

        if path not in cls._instances:
            # Create the assets instance
            instance = super().__new__(cls)
            cls._instances[path] = instance

        return cls._instances[path]

    def __init_subclass__(cls, relpath: Path, extensions: t.Tuple[str, ...]) -> None:
        """Assign attributes required by subclasses"""
        abs_path = Path(__file__).parent
        cls.relpath = abs_path / relpath
        cls.extensions = extensions

    def __init__(self, *subdirs: str | Path):
        """Initialize the Assets class and assets namespace"""
        # See if this is a single that has already been initialized. If so, bypass.
        if super().__getattribute__("_initialized"):
            return None

        # Setup attributes
        self.subdirs = subdirs
        self.assets = SimpleNamespace()

        # Setup the path to search
        path = self.relpath.joinpath(*subdirs)

        # Reconstruct the directory structure in the assets nested namespaces
        number_assets = 0
        for ext in self.extensions:
            for abs_filepath in path.glob(f"**/*.{ext.lstrip('.*')}"):
                # Get the asset's path relative to the "path"
                rel_path = abs_filepath.relative_to(path)

                # Break the rel_path into parts to populate in the namespace
                parts = rel_path.parts

                # Select of create the namespace to add the asset
                namespace = self.assets

                # iterate over all parts expect last item (filename)
                for part in parts[:-1]:
                    if not hasattr(namespace, part):
                        # Create the sub namespace
                        setattr(namespace, part, SimpleNamespace())

                    # Retrieve the sub namespace
                    namespace = getattr(namespace, part)

                # Convert the asset filename into a namespace attribute name
                # e.g. "document-open.svg" -> "document_open"
                filename: str = parts[-1]
                name = self._re_underscore.sub("_", filename)  # convert "-" to "_"
                name = self._re_strip_suffix.sub("", name)  # remove extensions

                # Convert the filepath to an asset object
                obj = self.convert(abs_filepath)

                # Set the object in the namespace and increment the count
                setattr(namespace, name, obj)
                number_assets += 1

        logger.info(f"{self.__class__.__name__} loaded {number_assets} assets")

        # Make the __getattribute__ and __setattribute__ lookup from the assets
        # attribute instead of self
        self._initialized = True

    def __setattr__(self, name: str, value: t.Any) -> None:
        if super().__getattribute__("_initialized"):
            assets = super().__getattribute__("assets")
            setattr(assets, name, value)
        else:
            super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> t.Any:
        if super().__getattribute__("_initialized"):
            assets = super().__getattribute__("assets")
            return getattr(assets, name)
        else:
            return super().__getattribute__(name)

    def convert(self, filepath: Path) -> QIcon:
        """Convert the given filepath to an asset object"""
        raise NotImplementedError("Convert method must be implemented by subclasses")


class Icons(Assets, relpath=Path("icons"), extensions=("*.svg",)):
    """Icon assets"""

    def convert(self, filepath: Path) -> QIcon:
        """Convert filepath to a QIcon object"""
        return QIcon(str(filepath))
