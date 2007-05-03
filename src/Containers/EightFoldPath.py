#from psyco.classes import psyobj
"""
EightFoldPath is a mixin class that allows simple tracking of
attributes in a cardinal direction manner. Using this, one can
create an object such that object.N is an attribute that we can think
of as 'north'
"""

class EightFoldPath(object):
    """Base class that is aware of the cardinal directions"""
    def __init__(self, dirs=None, north=True):
        # In the Northern Hemisphere, North is not a valid sun angle
        # If this is used in the Southern Hemisphere, it then South would be invalid.
        self.inNorth = north
        # All of our 7 directions in a tuple, maybe later we can refine the resolution.
        if north: self.dirs = ("NE","E","SE","S","SW","W","NW")
        else: self.dirs = ("SW","W","NW","N","NE","E","SE")
        # Dictionary to hold, for each direction, whatever we want.
        # We set it to None initially so that iteration works with an empty object
        self.paths = dict(list((k,None) for k in self.dirs))
        # If given a dirs arg (list or tuple) where len(dirs)==8, then set each direction
        # to the value of the appropriate index
        if dirs:
            for i in xrange(len(dirs)): self.paths[self.dirs[i]] = dirs[i]
    def __iter__(self):
        return iter(self.paths)
    def __len__(self):
        return len(self.items())
    def __getitem__(self,index):
        try: return self.paths[self.dirs[index]]
        except TypeError: return self.paths[index]
#        if isinstance(index,int): return self.paths[self.dirs[index]]
#        elif isinstance(index,str): return self.paths[index]
    def items(self): return self.paths.items()
    def iteritems(self):
        for k,v in self.paths.iteritems(): yield k,v
    def iterkeys(self):
        for k in self.paths.iterkeys(): yield k
    def itervalues(self):
        for v in self.paths.itervalues(): yield v

    def GetN(self):
        if self.inNorth: raise Warning("North is not a valid direction for hemisphere")
        return self.paths["N"]
    def SetN(self, arg):
        if self.inNorth: raise Warning("North is not a valid direction for hemisphere")
        else: self.paths["N"] = arg
    def GetS(self):
        if not self.inNorth: raise Warning("South is not a valid direction for hemisphere")
        return self.paths["S"]
    def SetS(self, arg):
        if not self.inNorth: raise Warning("South is not a valid direction for hemisphere")
        else: self.paths["S"] = arg

    def GetNE(self): return self.paths["NE"]
    def SetNE(self,arg): self.paths["NE"] = arg
    def GetE(self): return self.paths["E"]
    def SetE(self,arg): self.paths["E"] = arg
    def GetSE(self): return self.paths["SE"]
    def SetSE(self,arg): self.paths["SE"] = arg
    def GetSW(self): return self.paths["SW"]
    def SetSW(self,arg): self.paths["SW"] = arg
    def GetW(self): return self.paths["W"]
    def SetW(self,arg): self.paths["W"] = arg
    def GetNW(self): return self.paths["NW"]
    def SetNW(self,arg): self.paths["NW"] = arg

    # Properties allow access as instance.N = whatever.
    N = property(GetN, SetN)
    NE = property(GetNE, SetNE)
    E = property(GetE, SetE)
    SE = property(GetSE, SetSE)
    S = property(GetS, SetS)
    SW = property(GetSW, SetSW)
    W = property(GetW, SetW)
    NW = property(GetNW, SetNW)
