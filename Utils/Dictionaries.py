from __future__ import division
from time import mktime
from collections import defaultdict
from bisect import bisect_right, bisect_left

class Interpolator(defaultdict):
    def __init__(self, *args, **kwargs):
        """Linearly interpolated dictionary class

        This class assumes a numeric key/value pair and will
        allow a linear interpolation between the
        all values, filling the dictionary with the results."""
        defaultdict.__init__(self)
        self.sortedkeys = None

    def __missing__(self,key):
        """Interpolate between dictionary values and stock dictionary with results"""
        if not self.sortedkeys:
            # ASSUMPTION: This dictionary is not changed once created.
            self.sortedkeys = sorted(self.keys())
        ind = bisect_right(self.sortedkeys, key)-1
        x0 = int(self.sortedkeys[ind])
        x1 = int(self.sortedkeys[ind+1])

        y0 = self[x0]
        y1 = self[x1]
        val = None
        if isinstance(y0, tuple):
            if not len(y0): return () # We have nothing in the tuple, so return a blank tuple (not 'val', which is None)
            for i in xrange(len(y0)):
                try: val += y0[i] + ((y1[i]-y0[i])*(key-x0))/(x1-x0), # add value to the tuple
                except TypeError: val = y0[i] + ((y1[i]-y0[i])*(key-x0))/(x1-x0),
        else: val = y0 + ((y1-y0)*(key-x0))/(x1-x0)
        self[key] = val
        return val

    def View(self, minkey, maxkey, fore=None, aft=None):
        """Return dictionary subset

        Return a subset of the current dictionary containing items
        with keys between minkey and maxkey. If either or both of
        fore and/or aft are anything but None, then the returned
        dictionary will also contain the next element before or
        after minkey and maxkey, respectively."""
        keys = sorted(self.keys())
        # Get the minimum and maximum indices, including the one
        # before and one after if fore or aft are anything but None
        min = bisect_left(keys, minkey) - (fore is not None)
        max = bisect_right(keys, maxkey) + (aft is not None)

        d = Interpolator()
        for k in keys[min:max]:
            d[k] = self[k]
        return d

############################################
## Psyco optimization
try:
    from psyco import bind
    bind(Interpolator.__missing__)
except ImportError: pass