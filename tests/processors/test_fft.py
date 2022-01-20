"""
Test the FFTProcessor
"""
import pytest

from pocketchemist.processors.fft import FFTProcessor


@pytest.mark.parametrize('meth_name,name', (
                         # fft functions]
                         ('get_fft_func', 'numpy.fft'),
                         ('get_fft_func', 'torch.fft'),
                         ('get_fft_func', None),
                         # ifft functions
                         ('get_ifft_func', 'numpy.fft'),
                         ('get_ifft_func', 'torch.fft'),
                         ('get_ifft_func', None),
                         # fftshift functions
                         ('get_fftshift_func', 'numpy.fft'),
                         ('get_fftshift_func', 'torch.fft'),
                         ('get_fftshift_func', None),
                         # ifftshift functions
                         ('get_ifftshift_func', 'numpy.fft'),
                         ('get_ifftshift_func', 'torch.fft'),
                         ('get_ifftshift_func', None),
                         ))
def test_fftprocessor_get_x_func(meth_name, name):
    """Test the FFTProcessor get_x_func methods"""
    # Get the method
    meth = getattr(FFTProcessor, meth_name)

    # This method will raise a ModuleNotFoundError if the module could not
    # be found
    meth(name=name)
