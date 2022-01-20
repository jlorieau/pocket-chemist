"""
Test the FFTProcessor
"""
import pytest

from pocketchemist.processors.fft import FFTProcessor


@pytest.mark.parametrize('module_name',
                         ('numpy.fft', 'torch.fft', None))
def test_fftprocessor_get_fft_func(module_name):
    """Test the FFTProcessor get_fft_func method"""
    # This method will raise a ModuleNotFoundError if the module could not
    # be found
    fft_func = FFTProcessor.get_fft_func(module_name=module_name)


@pytest.mark.parametrize('module_name',
                         ('numpy.fft', 'torch.fft', None))
def test_fftprocessor_get_ifft_func(module_name):
    """Test the FFTProcessor get_ifft_func method"""
    # This method will raise a ModuleNotFoundError if the module could not
    # be found
    ifft_func = FFTProcessor.get_ifft_func(module_name=module_name)
