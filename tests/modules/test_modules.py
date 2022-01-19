"""
Tests for module classes
"""
from pocketchemist.modules import Module


def test_module_setup():
    """Test the Module setup"""
    import math

    module = Module('calcs', 'math', 'sqrt')
    assert module.get_module() == math
    assert module.get_callable() == math.sqrt
