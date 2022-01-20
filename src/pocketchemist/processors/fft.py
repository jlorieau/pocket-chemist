"""Processors for FFT"""
import typing as t

from pocketchemist.utils.list import wraplist

from .processor import Processor
from ..modules import Module, TorchModule

__all__ = ('FFTProcessor',)


class FFTProcessor(Processor):
    """A processor with access to FFT functionality."""

    modules = (
        TorchModule('fft', 'torch.fft', 'fft'),
        Module('fft', 'numpy.fft', 'fft'),
        TorchModule('ifft', 'torch.fft', 'ifft'),
        Module('ifft', 'numpy.fft', 'ifft'),
    )

    @classmethod
    def get_fft_func(cls,
                     module_name: t.Optional[str] = None,
                     modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best FFT function

        Parameters
        ----------
        module_name
            If specified, search for the callable with the given module name.
            Otherwise, the first module found will be used.
        modules
            The list of modules (:obj:`Module`) to search for the callable.
            If the list of modules is not specified, the self.modules list
            will be used.

        Returns
        -------
        callable
            The found module callable (function).

        Raises
        ------
        ModuleNotFoundError
            Raised when a suitable module could not be found.
        """
        # Setup the list of modules to search
        modules = wraplist(modules, default=getattr(cls, 'modules', []))
        modules = [module for module in modules if module.category == 'fft']
        return super().get_module_callable(module_name=module_name,
                                           modules=modules)

    @classmethod
    def get_ifft_func(cls,
                      module_name: t.Optional[str] = None,
                      modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best IFFT function

        Parameters
        ----------
        module_name
            If specified, search for the callable with the given module name.
            Otherwise, the first module found will be used.
        modules
            The list of modules (:obj:`Module`) to search for the callable.
            If the list of modules is not specified, the self.modules list
            will be used.

        Returns
        -------
        callable
            The found module callable (function).

        Raises
        ------
        ModuleNotFoundError
            Raised when a suitable module could not be found.
        """
        # Setup the list of modules to search
        modules = wraplist(modules, default=getattr(cls, 'modules', []))
        modules = [module for module in modules if module.category == 'ifft']
        return super().get_module_callable(module_name=module_name,
                                           modules=modules)
