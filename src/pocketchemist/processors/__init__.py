"""Classes and functions to conduct one or more processes"""
from .processor import Processor, GroupProcessor
from .modules import Module
from .fft import FFTProcessor

__all__ = ('Module', 'Processor', 'GroupProcessor', 'FFTProcessor')
