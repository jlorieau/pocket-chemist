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

        TorchModule('fftshift', 'torch.fft', 'fftshift'),
        Module('fftshift', 'numpy.fft', 'fftshift'),

        TorchModule('ifftshift', 'torch.fft', 'ifftshift'),
        Module('ifftshift', 'numpy.fft', 'ifftshift'),
    )

    @classmethod
    def get_fft_func(cls,
                     name: t.Optional[str] = None,
                     modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best available fft function (Computes the one dimensional
        discrete Fourier transform)

        See :meth:`.Processor.get_module_callable`.
        """
        return cls.get_module_callable(category='fft', name=name,
                                       modules=modules)

    @classmethod
    def get_ifft_func(cls,
                      name: t.Optional[str] = None,
                      modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best available ifft function (Computes the one dimensional
        discrete inverse Fourier transform)

        See :meth:`.Processor.get_module_callable`.
        """
        return cls.get_module_callable(category='ifft', name=name,
                                       modules=modules)

    @classmethod
    def get_fftshift_func(cls,
                     name: t.Optional[str] = None,
                     modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best available fftshift function (Reorders n-dimensional
        FFT data to have negative frequency terms first)

        See :meth:`.Processor.get_module_callable`.
        """
        return cls.get_module_callable(category='fftshift', name=name,
                                       modules=modules)

    @classmethod
    def get_ifftshift_func(cls,
                          name: t.Optional[str] = None,
                          modules: t.Optional[t.Iterable[Module]] = None) \
            -> t.Callable:
        """Return the best available ifftshift function (Inverse of fftshift)

        See :meth:`.Processor.get_module_callable`.
        """
        return cls.get_module_callable(category='ifftshift', name=name,
                                       modules=modules)
