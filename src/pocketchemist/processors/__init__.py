"""Classes and functions to conduct one or more processes"""
from .processor import Processor, GroupProcessor
from .fft import FFTProcessor

__all__ = ('Processor', 'GroupProcessor', 'FFTProcessor')
