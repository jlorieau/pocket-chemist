"""Processors for FFT"""
import typing as t
from dataclasses import dataclass

from .processor import Processor
from ..modules import Module, TorchModule

__all__ = ('FFTProcessor',)


@dataclass
class FFTWrapperFunc:
    """The fft wrapper callable object"""

    module: Module

    def __call__(self, data, n=None, axis=-1, norm=None, fft_type='fft',
                 center='fftshift'):
        """The fft wrapper function.

        Parameters
        ----------
        data
            The input data to Fourier transform
        n
            Length of the transformed axis of the output
        axis
            Axis over which to compute the FFT. (Last dimension used if not
            specified)
        norm
            Normalization mode. e.g. “backward”, “ortho”, “forward”
        fft_type
            The type of fft function to use. Options include:

            - 'fft': A complex Fourier transform
            - 'ifft': A complex inverse Fourier transform
        center
            (Optional) centering of frequencies. Options include:

            - None. No centering is applied
            - 'fftshift'. Use the fftshift function
            - 'ifftshift'. Use the ifftshift function

        Returns
        -------
        out
            The Fourier transormed and possibly frequeny
        """
        raise NotImplementedError


class NumpyFFTFunc(FFTWrapperFunc):
    """The numpy implementation of the FFT func"""

    def __call__(self, data, n=None, axis=-1, norm=None, fft_type='fft',
                 center='fftshift'):
        # Retrieve the 'fft' or 'ifft' function
        fft_func = self.module.get_callable(fft_type)

        # Perform the fft
        result = fft_func(a=data, n=n, axis=axis, norm=norm)
        result = result.astype(data.dtype)

        # Center the spectrum if needed
        if isinstance(center, str):
            fftshift_func = self.module.get_callable(center)
        else:
            fftshift_func = None

        return fftshift_func(result) if fftshift_func is not None else None


class TorchFFTFunc(FFTWrapperFunc):
    """The Torch implementation of the FFT func"""

    from_numpy_module: Module

    def __call__(self, data, n=None, axis=-1, norm=None, fft_type='fft',
                 center='fftshift'):
        # Retrieve from_numpy from the root torch module
        from_numpy = self.from_numpy_module.get_callable()

        # Determine the FFT function
        if fft_type == 'fft':
            fft_func = self.fft_module.get_callable()
        elif fft_type == 'ifft':
            fft_func = self.ifft_module.get_callable()
        else:
            raise NotImplementedError

        # Convert the data to a tensor and conduct the FFT
        tensor = from_numpy(data)
        result = fft_func(input=data, n=n, dim=axis, norm=norm)

        # Center the spectrum if needed
        if center == 'fftshift':
            fftshift_func = self.fftshift_module.get_callable()
        elif center == 'ifftshift':
            fftshift_func = self.ifftshift_module.get_callable()
        else:
            fftshift_func = None

        result = fftshift_func(result) if fftshift_func is not None else result
        return result.cpu().detach().numpy()


class FFTProcessor(Processor):
    """A processor with access to FFT functionality."""

    modules = (
        # TorchModule('fft', 'torch.fft', 'fft'),
        Module('fft', 'numpy.fft', NumpyFFTFunc),
    )
