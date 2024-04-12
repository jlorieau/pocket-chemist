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
    [<class 'disseminate.utils.classes.B'>, \
<class 'disseminate.utils.classes.C'>]
    """
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)
    ]
