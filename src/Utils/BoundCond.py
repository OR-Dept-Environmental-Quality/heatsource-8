from SingletonMixin import Singleton
    
class BoundCond(Singleton):
    """Class to hold the boundary conditions for a specific StreamReach

    This class is a singleton so currently only allows one instance per run. In
    the event that we want to have more than one StreamReach per run (i.e. model
    a watershed instead of a single stream) then this will have to be changed
    to a regular class, which should be easy
    """
    def __init__(self):
        self.__Q = []
        self.__T = []
        self.__C = []
