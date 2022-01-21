"""
Tests for module classes
"""
import pickle
from multiprocessing import Pool
from dataclasses import dataclass

from pocketchemist.modules import Module


def dummy_func():
    return "dummy function"


@dataclass
class DummyWrapper:

    module: Module

    def __call__(self):
        return "dummy_wrapper"


def test_module_setup():
    """Test the Module setup"""

    # 1. Test with callable string
    module = Module('calcs', 'pickle', 'loads')
    assert module.get_module() == pickle
    assert module.get_callable() == pickle.loads

    # 2. Test with callable object
    module = Module('calcs', 'pickle', dummy_func)
    assert module.get_module() == pickle
    assert module.get_callable() == dummy_func

    # 3. Test with callable class
    module = Module('calcs', 'pickle', DummyWrapper)
    assert module.get_module() == pickle

    # The class was instantiated
    callable_obj = module.get_callable()
    assert isinstance(callable_obj, DummyWrapper)
    assert callable_obj.module == module  # it has a reference to the module
    assert hasattr(callable_obj, '__call__')  # it's callable


def test_module_pickle():
    """Test the pickling of Module objects"""

    # 1. Test with callable string
    module = pickle.loads(pickle.dumps(Module('calcs', 'pickle', 'loads')))
    assert module.get_module() == pickle
    assert module.get_callable() == pickle.loads

    # 2. Test with callable object
    module = pickle.loads(pickle.dumps(Module('calcs', 'pickle', dummy_func)))
    assert module.get_module() == pickle
    assert module.get_callable() == dummy_func

    # 3. Test with callable class
    module = Module('calcs', 'pickle', DummyWrapper)
    assert module.get_module() == pickle

    # The class was instantiated
    callable_obj = module.get_callable()
    assert isinstance(callable_obj, DummyWrapper)
    assert callable_obj.module == module  # it has a reference to the module
    assert hasattr(callable_obj, '__call__')  # it's callable


def test_module_multiprocessing_pool():
    """Test the multiprocessing pool behavior of Module objects."""
    import math

    # 1. Test with callable string
    module = Module('calcs', 'pickle', 'loads')
    with Pool() as pool:
        results = [pool.apply_async(module.get_callable, ()) for i in range(4)]
        assert all(result.get() == pickle.loads for result in results)

    # 2. Test with callable object
    module = Module('calcs', 'pickle', dummy_func)
    with Pool() as pool:
        results = [pool.apply_async(module.get_callable, ()) for i in range(4)]
        assert all(result.get() == dummy_func for result in results)

    # 3. Test with callable class
    module = Module('calcs', 'pickle', DummyWrapper)
    with Pool() as pool:
        results = [pool.apply_async(module.get_callable, ()) for i in range(4)]
        results = [result.get() for result in results]

        # Check the results
        assert all(isinstance(callable_obj, DummyWrapper)
                   for callable_obj in results)
        assert all(callable_obj.module == module
                   for callable_obj in results)  # each references module
