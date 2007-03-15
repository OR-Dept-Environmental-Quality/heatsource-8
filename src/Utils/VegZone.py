
class VegZone(object):
    """Container to hold information about vegetation zones

    Attributes include:
    Elevation: Ground surface elevation
    VHeight: Canopy height
    VDensity: Canopy density
    Overhang: Possible canopy overhanging stream

    Possible access methods are (example):

    >>> v = vegzone.VegZone(23,43,VDensity=4)
    >>> v
    [23, 43, 4, None]
    >>> v['Elevation']
    23
    >>> v.Elevation
    23
    >>> v.VDensity
    4
    >>> v.Overhang # Not set when method constructed
    >>> v[0]
    23
    >>> v[0:3]
    [23, 43, 4]
    >>>
    """
    __slots__ = ['Elevation','VHeight','VDensity','Overhang','SlopeHeight']
    def __init__(self, *args, **kwargs):
        default = [[],[],[],[],0] # Default values
        # We only deal with the first 3 attributes on a normal basis.
        max = len(self.__slots__)
        if len(args) > max or len(kwargs) > max or (len(args) + len(kwargs) > max):
            raise Exception("%s cannot have more than %i arguments" % (self.__class__.__name__,max))
        # Set all the args or default to zero
        for i in xrange(len(self.__slots__)):
            try: setattr(self, self.__slots__[i], args[i])
            except IndexError: setattr(self, self.__slots__[i], default[i])
        # Then fill with kwargs, if any
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
    def __repr__(self):
        return "VZ:%s" % repr(tuple(getattr(self,i) for i in self.__slots__))
    def __iter__(self):
        return (getattr(self,i) for i in self.__slots__)
    def __getitem__(self, index):
        if isinstance(index,str): return getattr(self,index)
        elif isinstance(index,slice): return tuple(self)[index.start:index.stop:index.step]
        elif isinstance(index,int): return getattr(self, self.__slots__[index])
    def __setitem__(self, index, value):
        #NOTE: No item in this class can be negative, so we ensure that here.
        value = 0 if value < 0 else value
        if isinstance(index,str):
            setattr(self,index,value)
        elif isinstance(index,int):
            setattr(self,self.__slots__[index],value)
    def __getother(self,other):
        if not hasattr(other,'__iter__'):
            raise Exception("Item does not support comparison with %s: %s" % (self.__class__.__name__, other))
        l2 = [i for i in other]
        # Only compare the length of l2, because if there are values
        # of None at the end, then we needn't compare them, and the
        # list generated from other might be shorter.
        l = [i for i in self][:len(l2)]
        return l,l2

    def __eq__(self, other):
        l, l2 = self.__getother(other)
        return l == l2
    def __ne__(self, other):
        l,l2 = self.__getother(other)
        return l != l2