from __future__ import division
from time import mktime
from collections import defaultdict
from bisect import bisect

class Interpolator(defaultdict):
    def __init__(self, *args, **kwargs):
        """Linearly interpolated dictionary class

        This class assumes a numeric key/value pair and will
        allow a linear interpolation between the
        all values, filling the dictionary with the results."""
        defaultdict.__init__(self)
        self.step = kwargs["dt"]
        self.sortedkeys = None

    def __missing__(self,key):
        """Interpolate between dictionary values and stock dictionary with results"""
        if not self.sortedkeys:
            self.sortedkeys = sorted(self.keys())
        ind = bisect(self.sortedkeys, key)-1
        x0 = int(self.sortedkeys[ind])
        x1 = int(self.sortedkeys[ind+1])

        y0 = self[x0]
        y1 = self[x1]
        val = None
        if isinstance(y0, tuple):
            for i in xrange(len(y0)):
                try: val += y0 + ((y1-y0)*(key-x0))/(x1-x0), # add value to the tuple
                except TypeError: val = y0 + ((y1-y0)*(key-x0))/(x1-x0),
            return val
        else: return y0 + ((y1-y0)*(key-x0))/(x1-x0)

try:
    from psyco import bind
    bind(Interpolator.__missing__)
except ImportError: pass