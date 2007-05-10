from itertools import chain

class Zonator(tuple):
    def __new__(cls, *args, **kwargs):
        """Python's immutable types must be subclassed using __new__(). See
        http://www.python.org/download/releases/2.2.3/descrintro/#__new__
        for details
        """
        return tuple.__new__(cls, *args, **kwargs)
    def __iter__(self):
        return iter(chain(*self))
