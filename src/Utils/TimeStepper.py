from datetime import datetime, timedelta
import time

class TimeStepper(object):
    """This class provides a clock to be used in the model timestepping.

    The basic functionality of this class comes from the __iter__() method,
    which will iterate over a certain timespan, given a certain timestep,
    and will return the current timestep value as a datetime object. This
    allows use of the datetime object in calculations, and for dictionary
    or object keys, for instance as an index in a AttrList.TimeList object.
    """
    def __init__(self, start, dt=None, stop=None):
        if (not isinstance(start, datetime)) or (stop and not isinstance(stop, datetime)):
            raise Exception("Start and stop times much be Python datetime.datetime instances.")
        if dt and not isinstance(dt,timedelta):
            raise Exception("dt must be a Python datetime.timedelta instance.")

        # Some timedelta objects with standard time amounts
        self.day = timedelta(days=1)
        self.hour = timedelta(hours=1)
        self.minute = timedelta(minutes=1)
        self.second = timedelta(seconds=1)
        self.year = timedelta(weeks=52)

        self.__start = start
        self.__dt = dt or self.minute
        self.__stop = stop or self.year

    def __iter__(self):
        if not self.__start or not self.__dt:
            raise Exception("The start, stop and dt attributes must be set before using %s" % self.__class__.__name__)
        current = self.__start
        while current <= self.__stop:
            yield current
            current += self.dt

    def itercount(self):
        """Iterator, just as __iter__() with count parameter

        Functions exactly as __iter__(), but returns a tuple (time,n)
        where n = number of iterations, starting at zero. It is
        useful only as a convenience function where we need to track n
        """
        n = 0
        for time in self:
            yield time, n
            n += 1

    def GetStart(self): return self.__start
    def SetStart(self, start):
        if isinstance(start, datetime):
            self.__start = start
        else:
            try:
                self.__start = datetime(*time.strptime(start.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S")[:6])
            except AttributeError:
                raise TypeError("Start time must be a PyTime or a datetime object, not %s" % start.__class__.__time__)
    def GetDT(self): return self.__dt
    def SetDT(self, dt):
        """Sets the current timestep in terms of seconds, or sets it to a timedelta object"""
        if isinstance(dt, timedelta):
            self.__dt = dt
        else:
            self.__dt = timedelta(seconds=dt)
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
    dt = property(GetDT, SetDT)
    stop = property(GetStop, SetStop)

