"""Processors for FFT"""
from .processor import Processor
from .modules import Module, TorchModule

__all__ = ('FFTProcessor',)


class FFTProcessor(Processor):
    """A processor with access to FFT functionality."""

    modules = (
        TorchModule('fft', 'torch', 'fft'),
        Module('fft', 'cupy.fft', 'fft'),
        Module('fft', 'numpy.fft', 'fft'),
        TorchModule('ifft', 'torch', 'ifft'),
        Module('ifft', 'numpy.fft', 'ifft'),
        Module('ifft', 'cupy.fft', 'ifft'),
    )

    @property
    def fft(self):
        """Return the best FFT function"""
        fft_modules = [mod for mod in self.modules if mod.category == 'fft']
        for fft_module in fft_modules:
            call = fft_module.get_callable()
            if call is not None:
                return call
        raise ModuleNotFoundError("A suitable fft module was not found")
