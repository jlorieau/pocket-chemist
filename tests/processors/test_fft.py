"""
Test the FFTProcessor
"""
import pickle
from multiprocessing import Pool

import pytest
import numpy as np

from pocketchemist.processors.fft import FFTProcessor, FFTWrapperFunc


@pytest.fixture
def module_names():
    """A listing of module names to test"""
    return 'numpy.fft', None  # None is the default


@pytest.fixture
def data2d():
    """Return a 2D dataset"""
    t = np.linspace(0.0, 1.0, 128)
    lb = 5.0  # Hz

    # Setup the 1-dimension FIDs (time decay functions)
    v1 = 10.  # Hz
    fid1 = np.exp((1j * v1 * 2. * np.pi - lb) * t)

    v2 = -20.  # Hz
    fid2 = np.exp((1j * v2 * 2. * np.pi - lb) * t)

    # Calculate spectral parameters
    dt = t[1] - t[0]  # dwell time, delta t, in sec
    df = t[-1]**-1  # spectral resolution, delta f, in Hz
    sw = dt**-1  # spectral width, in Hz

    # Determine the index position for the FT peak maximum, accounting for
    # centering of the zero-frequencies
    maxF1 = int((v1 + sw/2.)/df)
    maxF2 = int((v2 + sw/2.)/df)

    # Return the 2d array from the product of each dimension
    data2d = np.dot(fid1[:, None], fid2[None, :])
    assert data2d.shape == (128, 128)
    return data2d


def test_fftprocessor_setup(module_names):
    """Test the setup of the FFTProcessor class"""
    fft_processor = FFTProcessor()

    for module_name in module_names:
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


def test_fftprocessor_pickle(module_names):
    """Test the pickling of FFTProcessor objects"""
    for module_name in module_names:
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


def test_fftprocessor_multiprocessing_pool(module_names, data2d):
    """Test the execution of FFTProcessor callables using a multiprocessor
    pool"""
    # Setup the processor
    fft_processor = FFTProcessor()

    # 1. Test with a 2D dataset
    for module_name in module_names:
        with Pool() as pool:
            # Conduct the Fourier Transformation. This will only Fourier
            # transform the direct dimension

            fft_func = fft_processor.get_module_callable(name=module_name)
            results = [pool.apply_async(fft_func, (data2d,))
                       for i in range(4)]
            ftdata2d = [result.get() for result in results]

            # Check that the data was properly transformed by finding the
            # maximum
            for ftdata in ftdata2d:
                # Check the result's type and shape
                assert isinstance(ftdata, np.ndarray)
                assert ftdata.shape == (128, 128)

                # Look at the first 1d slice (F2) and find the maximum peak
                ftdata1d = ftdata[0, :]
                assert ftdata1d.shape == (128,)

                maxindex = np.argmax(ftdata1d)
                assert maxindex == 44
