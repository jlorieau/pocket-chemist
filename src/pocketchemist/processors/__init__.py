"""Classes and functions to conduct one or more processes"""
from .processor import Module, Processor, GroupProcessor
from .fft import FFTProcessor

__all__ = ('Module', 'Processor', 'GroupProcessor', 'FFTProcessor')
