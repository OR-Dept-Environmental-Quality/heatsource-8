from datetime import datetime, timedelta
import time
from SingletonMixin import Singleton

class TimeStepper(Singleton):
    """This class provides a clock to be used in the model timestepping.

    The basic functionality of this class comes from the __iter__() method,
    which will iterate over a certain timespan, given a certain timestep,
    and will return the current timestep value as a datetime object. This
    allows use of the datetime object in calculations, and for dictionary
    or object keys, for instance as an index in a AttrList.TimeList object.
    """
    def __init__(self):
        # Some timedelta objects with standard time amounts
        self.day = timedelta(days=1)
        self.hour = timedelta(hours=1)
        self.minute = timedelta(minutes=1)
        self.second = timedelta(seconds=1)

        self.__start = None
        self.__dT = self.minute
        self.__stop = None

    def __iter__(self):
        if not self.__start or not self.__dT or not self.__stop:
            raise Exception("The start, stop and dT attributes must be set before using %s" % self.__class__.__name__)
        current = self.__start
        while current <= self.__stop:
            yield current
            current += self.dT


    def GetStart(self): return self.__start
    def SetStart(self, start):
        if isinstance(start, datetime):
            self.__start = start
        else:
            try:
                self.__start = datetime(*time.strptime(start.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S")[:6])
            except AttributeError:
                raise TypeError("Start time must be a PyTime or a datetime object, not %s" % start.__class__.__time__)
    def GetDT(self): return self.__dT
    def SetDT(self, dt):
        """Sets the current timestep in terms of seconds, or sets it to a timedelta object"""
        if isinstance(dt, timedelta):
            self.__dT = dt
        else:
            self.__dT = timedelta(seconds=dt)
    def GetStop(self): return self.__stop
    def SetStop(self, stop):
        if isinstance(stop, datetime):
            self.__stop = stop
        elif isinstance(stop, timedelta):
            self.__stop = self.start + stop
        else:
            try:
                self.__stop = datetime(*time.strptime(stop.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S")[:6])
            except AttributeError:
                raise TypeError("Stop time must be a PyTime, timedelta or a datetime object, not %s" % start.__class__.__time__)
    start = property(GetStart, SetStart)
    dT = property(GetDT, SetDT)
    stop = property(GetStop, SetStop)

