"""
Utilities for classes
"""


def all_subclasses(cls):
    """Retrieve all subclasses, sub-subclasses and so on for a class

    Parameters
    ----------
    cls : Type
        The class object to inspect for subclasses.

    Returns
    -------
    subclasses : list
        The list of all subclasses.

    Examples
    --------
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(B): pass
    >>> all_subclasses(A)
    [<class 'xamin.utils.classes.B'>, <class 'xamin.utils.classes.C'>]
    """
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)
    ]


class Singleton(type):
    """A metaclass for making singleton classes

    Examples
    --------
    >>> class Single(metaclass=Singleton):
    ...     pass
    >>> singleton_a = Single()
    >>> singleton_b = Single()
    >>> assert id(singleton_a) == id(singleton_b)  # The same object
    """

    def __init__(cls, *args, **kwargs):
        cls._singleton_instance = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton_instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._singleton_instance = instance
        return cls._singleton_instance
