"""
Classes for managing module imports and availability information.
"""
import abc
from dataclasses import dataclass
from importlib import import_module, metadata  # metadata in python >= 3.8
from types import ModuleType
import typing as t

import click

__all__ = ('Module', 'GPUModule', 'TorchModule')

# The number of spaces to add for printing sub-levels of processors
space_level = 2


@dataclass
class Module:

    #: The category name of the module
    category: str

    #: The name of the module
    name: str

    #: The name of the imported function
    callable_name: str

    #: Options for printing the module to the terminal
    print_cls_fg_color = 'cyan'

    _modules = dict()

    def get_module(self) -> t.Union[ModuleType, None]:
        """Retrieve the module associated with this object

        Returns
        -------
        module
            The loaded module, if available
            None if the module could not be found
        """
        key = self.name

        if key in Module._modules:
            return Module._modules[key]

        # Try loading the module
        try:
            module = import_module(key)
            Module._modules[key] = module
        except ImportError:
            Module._modules[key] = None

        return Module._modules[key]

    def get_root_module(self) -> t.Union[ModuleType, None]:
        """Retrieve the root module of package

        Returns
        -------
        module
            The loaded module, if available
            None if the module could not be found
        """
        # Try to get the root module's name
        root_module_name = self.name.split('.')[0]

        # Try loading the module
        try:
            return import_module(root_module_name)
        except ImportError:
            return None

    def get_callable(self) -> t.Union[t.Callable, None]:
        """Retrieve the module function.

        Returns
        -------
        callable
            The module's function or callable class, if available.
            None if the function could not be found.
        """
        # See if the module is available, and retrieve the function if it is
        module = self.get_module()
        return getattr(module, self.callable_name, None)

    @classmethod
    def list_instances(cls):
        """List modules managed by this class"""
        import gc
        return [obj for obj in gc.get_objects() if isinstance(obj, cls)]

    def print(self,
              space_level: int = space_level,
              item_number: t.Optional[str] = "",
              subitems: t.Optional[t.List[str]] = None) -> None:
        """Print information on the module to the terminal.

        Parameters
        ----------
        space_level
            The number of spaces to separate a level
        item_number
            An optional character to prepend the printed processing string.
        subitems
            Additional items to print about the module as subitems.
        """
        cls_name = self.__class__.__name__
        item_number = str(item_number) + '. ' if item_number else ""
        subitems = list(subitems) if subitems is not None else []

        # Setup subitems to print
        module = self.get_module()
        module_available = module is not None
        callable_available = self.get_callable() is not None
        subitems[:0] += [click.style("module: ") +
                     (click.style("AVAILABLE", fg='green') if module_available
                      else click.style("NOT FOUND", fg='red')) + " " +
                     click.style("callable: ") +
                     (click.style("AVAILABLE", fg='green') if callable_available
                      else click.style("NOT FOUND", fg='red'))]

        # Add version information
        if module_available:
            # Find the root module
            root_module = self.get_root_module()
            if hasattr(root_module, '__version__'):
                subitems += [click.style("version: ") +
                             click.style(root_module.__version__)]

        # Format the string to print
        click.echo(" " * space_level +
                   item_number +
                   click.style(cls_name, fg=self.print_cls_fg_color) +
                   f"({self.name})")
        for subitem in subitems:
            click.echo(" " * space_level * 2 + subitem)


class GPUModule(Module):

    @abc.abstractmethod
    def get_available(self):
        """Determine if the GPU libraries are available"""
        raise NotImplementedError


class TorchModule(GPUModule):
    """A module for PyTorch"""

    def gpu_available(self):
        root_module = self.get_root_module()
        try:
            return root_module.cuda.is_available()
        except AttributeError:
            return False

    def print(self,
              space_level: int = space_level,
              item_number: t.Optional[str] = "",
              subitems: t.Optional[t.List[str]] = None) -> None:
        # Setup arguments
        subitems = subitems if subitems is not None else []

        gpu_available = self.gpu_available()
        subitems += [click.style("GPU (CUDA) Available: ") + str(gpu_available)]

        super().print(space_level=space_level, item_number=item_number,
                      subitems=subitems)
