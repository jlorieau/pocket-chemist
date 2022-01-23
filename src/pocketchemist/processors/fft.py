"""Processors for FFT"""
import typing as t
from dataclasses import dataclass
from enum import Enum

import numpy as np

from .processor import Processor
from ..modules import Module, TorchModule

__all__ = ('FFTProcessor', 'FFTWrapperFunc', 'FFTType', 'FFTShift')


# Enumeration types
class FFTType(Enum):
    """The types of fft functions"""
    FFT = 'fft'  # Fast Fourier Transform (1D). exp(-i 2pi nu)
    IFFT = 'ifft'  # Inverse Fast Fourier Transform (1D). exp(i 2pi nu)
    RFFT = 'rfft'  # Real Fourier Transform (1D). Real component only.
    IRFFT = 'irfft'  # Inverse Real Fourier Transform (1D)
    NONE = None  # No Fourier Transform (null)


class FFTShift(Enum):
    """The type of post-FFT frequency/time shift to apply"""
    FFTSHIFT = 'fftshift'  # Shift zero-frequency to the center of the spectrum
    IFFTSHIFT = 'ifftshift'  # Reverse of FFTSHIFT
    NONE = None  # Do not apply frquency shift


# Wrapper Class Functions
@dataclass
class FFTWrapperFunc:
    """The fft wrapper callable object"""

    module: Module

    # Function parameter defaults that can be modified
    fft_type: FFTType = FFTType.FFT
    fft_shift: FFTShift = FFTShift.FFTSHIFT

    def __call__(self,
                 data: np.ndarray,
                 n: t.Optional[int] = None,
                 axis: int = -1,
                 norm: t.Optional[str] = None,
                 fft_type: t.Optional[FFTType] = None,
                 fft_shift: t.Optional[FFTShift] = None):
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
            The type of fft function to use. See :class:`.FFTType`
        fft_shift
            Center the zero-frequency to the center of the spectrum.
            See :class:`.FFTShift`

        Returns
        -------
        out
            The Fourier transormed and possibly frequeny
        """
        raise NotImplementedError


class NumpyFFTFunc(FFTWrapperFunc):
    """The numpy implementation of the FFT wrapper function"""

    def __call__(self, data, n=None, axis=-1, norm=None, fft_type=None,
                 fft_shift=None):
        # Setup arguments
        fft_type = fft_type if fft_type is not None else self.fft_type
        fft_shift = fft_shift if fft_shift is not None else self.fft_shift

        # Retrieve the 'fft' or 'ifft' function
        fft_func = self.module.get_callable(fft_type.value)

        # Perform the fft
        result = fft_func(a=data, n=n, axis=axis, norm=norm)
        result = result.astype(data.dtype)

        # Center the spectrum if needed
        if fft_shift is FFTShift.NONE:
            fftshift_func = None
        else:
            fftshift_func = self.module.get_callable(fft_shift.value)

        return fftshift_func(result) if fftshift_func is not None else result


class TorchFFTFunc(FFTWrapperFunc):
    """The Torch implementation of the FFT wrapper function"""

    from_numpy_module: Module

    def __call__(self, data, n=None, axis=-1, norm=None, fft_type=None,
                 fft_shift=None):
        # Setup arguments
        fft_type = fft_type if fft_type is not None else self.fft_type
        fft_shift = fft_shift if fft_shift is not None else self.fft_shift

        # Retrieve the conversion function for numpy arrays
        from_numpy = getattr(self.module.get_root_module(), 'from_numpy')

        # Convert the numpy ndarray to a tensor
        tensor = from_numpy(data)

        # Retrieve the 'fft' or 'ifft' function
        fft_func = self.module.get_callable(fft_type.value)

        # Perform the fft
        result = fft_func(input=tensor, n=n, dim=axis, norm=norm)

        # Center the spectrum if needed
        if fft_shift is FFTShift.NONE:
            fftshift_func = None
        else:
            fftshift_func = self.module.get_callable(fft_shift.value)

        return (fftshift_func(result).cpu().detach().numpy()
                if fftshift_func is not None else
                result.cpu().detach().numpy())


class FFTProcessor(Processor):
    """A processor with access to FFT functionality."""

    modules = (
        TorchModule('fft', 'torch.fft', TorchFFTFunc),
        Module('fft', 'numpy.fft', NumpyFFTFunc),
    )
