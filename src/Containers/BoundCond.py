from Utils.SingletonMixin import Singleton
from Containers.AttrList import TimeList


class BoundCond(Singleton):
    """Class to hold the boundary conditions for a specific StreamReach

    This class is a singleton so currently only allows one instance per run. In
    the event that we want to have more than one StreamReach per run (i.e. model
    a watershed instead of a single stream) then this will have to be changed
    to a regular class, which should be easy
    """
    def __init__(self):
        self.Q = TimeList() # Discharge conditions
        self.T = TimeList() # Temperature conditions
        self.C = TimeList() # Cloudiness conditions
    def __iter__(self):
        for lst in [self.Q, self.T, self.C]:
            yield lst
