"""
Test the FFTProcessor
"""
import pickle
from multiprocessing import Pool

import pytest
import numpy as np

from pocketchemist.processors.fft import FFTProcessor, FFTWrapperFunc

# Create a list of modules to test
module_names = ('numpy.fft', 'torch.fft', None)  # None is the default


@pytest.fixture
def data2d(v1: float = 10., v2: float = -20., lb: float = 5.0,
           tmax: float = 1.0, npts: int = 128) -> np.ndarray:
    """Return a 2D dataset

    Parameters
    ----------
    v1
        The frequency (in Hz) of the first dimension (F1)
    v2
        The frequency (in Hz) of the second domension (F2)
    lb
        The Lorentzian line-broadening of the peak (in Hz).
    tmax
        The maximum acquisition time in seconds
    npts
        The number of points per time domain signal (FID)

    Returns
    -------
    data2d
        The constructed time-domain dataset in 2-dimensions
    """
    t = np.linspace(0.0, tmax, npts)

    # Setup the 1-dimension FIDs (time decay functions)
    fid1 = np.exp((1j * v1 * 2. * np.pi - lb) * t)
    fid2 = np.exp((1j * v2 * 2. * np.pi - lb) * t)

    # Calculate spectral parameters
    dt = t[1] - t[0]  # dwell time, delta t, in sec
    df = t[-1]**-1  # spectral resolution, delta f, in Hz
    sw = dt**-1  # spectral width, in Hz

    # Return the 2d array from the product of each dimension
    data2d = np.dot(fid1[:, None], fid2[None, :])
    assert data2d.shape == (npts, npts)
    return data2d


def check_ftdata2d(data2d, dim=2, center=True, fft_type='fft',
                   v1: float = 10., v2: float = -20.,
                   tmax: float = 1.0, npts: int = 128):
    """Check FT data2d"""
    # Check the result's type and shape
    assert isinstance(data2d, np.ndarray)
    assert data2d.shape == (npts, npts)

    # Fix the frequencies in relation to the type of fft
    if fft_type == 'ifft':
        v1 *= -1.0
        v2 *= -1.0

    # Calculate the spectral parameters
    dt = tmax / npts
    sw = dt**-1
    df = tmax ** -1

    if dim == 2:
        data1d = data2d[0, :]
        assert data1d.shape == (npts,)

        # Verify the position of the peak
        maxindex = np.argmax(data1d)  # Find the maximum pt position

        if center:
            correct_index = int((sw/(2. * df)) + (v2 / df))
        else:
            correct_index = max(npts + int(v2 / df), int(v2 / df))
        assert maxindex == correct_index


@pytest.mark.parametrize("module_name", module_names)
def test_fftprocessor_setup(module_name):
    """Test the setup of the FFTProcessor class"""
    fft_processor = FFTProcessor()

    callable_obj = fft_processor.get_module_callable(name=module_name)

    # The callable object should be an instance of the FFTWrapperFunc cls
    assert isinstance(callable_obj, FFTWrapperFunc)
    assert callable(callable_obj)

    if module_name is not None:
        # Check the specific module matches the module_name requested
        assert callable_obj.module.name == module_name
    else:
        # Default module
        assert callable_obj.module.name is not None


@pytest.mark.parametrize("module_name", module_names)
def test_fftprocessor_pickle(module_name):
    """Test the pickling of FFTProcessor objects"""
    fft_processor = pickle.loads(pickle.dumps(FFTProcessor()))
    callable_obj = fft_processor.get_module_callable(name=module_name)

    # The callable object should be an instance of the FFTWrapperFunc cls
    assert isinstance(callable_obj, FFTWrapperFunc)
    assert callable(callable_obj)

    if module_name is not None:
        # Check the specific module matches the module_name requested
        assert callable_obj.module.name == module_name
    else:
        # Default module
        assert callable_obj.module.name is not None


@pytest.mark.parametrize("module_name", module_names)
def test_fftprocessor_fftwrapperfunc(module_name, data2d):
    """Test the behavior of different FFTWrapperFunc functions."""
    # Setup the processor and retrieve the FFTWrapperFunc
    fft_processor = FFTProcessor()
    fft_func = fft_processor.get_module_callable(name=module_name)

    # Check that it's an subclass instance of FFTWrapperFunc
    assert isinstance(fft_func, FFTWrapperFunc)
    assert type(fft_func) in FFTWrapperFunc.__subclasses__()

    # 1. Try an fft with centering (default)
    ftdata2d = fft_func(data2d)
    check_ftdata2d(ftdata2d)

    # 2. Try an fft without centering
    ftdata2d = fft_func(data2d, center=None)
    check_ftdata2d(ftdata2d, center=False)

    # 3. Try an ifft with centering
    ftdata2d = fft_func(data2d, fft_type='ifft')
    check_ftdata2d(ftdata2d, fft_type='ifft')


@pytest.mark.parametrize("module_name", module_names)
def test_fftprocessor_multiprocessing_pool(module_name, data2d):
    """Test the execution of FFTProcessor callables using a multiprocessor
    pool"""
    # Setup the processor
    fft_processor = FFTProcessor()

    # 1. Test with a 2D dataset
    with Pool() as pool:
        # Conduct the Fourier Transformation. This will only Fourier
        # transform the direct dimension

        fft_func = fft_processor.get_module_callable(name=module_name)
        results = [pool.apply_async(fft_func, (data2d,))
                   for i in range(4)]

        # Check that the data was properly transformed by finding the
        # maximum
        for result in results:
            # Check the result's type and shape
            check_ftdata2d(data2d=result.get())
