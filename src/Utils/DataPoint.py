
class DataPoint(float):
    """General class defining a floating point number with optional location and time attributes

    This class is, for all intents and purposes, a normal python floating point number. It is
    roughly the same size, depending on the value of time and place, which can be objects, and it
    should be just as fast. It can be manipulated just as any other floating point number, because
    it is a direct subclass of float. Time should likely be either a string or a python Time or
    Datetime object. However, there are no restrictions at this baseclass level on the type of
    the time attribute, so it could be anything. next_x and prev_x are references to the next
    and previous DataPoints by location, likewise, next_t and prev_t are references to the next
    and previous DataPoints by time.
    """
    __slots__ = ['x','t','prev_x','next_x','prev_t','next_t']
    def __new__(cls, value=0.0, time=None, place=None):
        """Python's immutable types must be subclassed using __new__(). See
        http://www.python.org/download/releases/2.2.3/descrintro/#__new__
        for details
        """
        return float.__new__(cls, value)
    def __init__(self, value=0.0, time=None, place=None):
        self.t = time
        self.x = place
        self.prev_x = None
        self.next_x = None
        self.prev_t = None
        self.next_t = None
    # Functions that are used for comparison
    def X(self): return self.x
    def T(self): return self.t
