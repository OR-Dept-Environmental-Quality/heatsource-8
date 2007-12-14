from datetime import datetime, timedelta
import time, math
from ..Utils.TimeZones import TZ

class ChronosDiety(object):
    """This class provides a clock to be used in the model timestepping.

    This is a class that is the God of Time, and thus seen from The Model as
    the end-all-be-all of time. Like Helios, there is only one Chronos, telling
    us when we are in time.
    The basic functionality of this class comes from the __iter__() method,
    which will iterate over a certain timespan, given a certain timestep,
    and will return the current timestep value as a datetime object. This
    allows use of the datetime object in calculations, and for dictionary
    or object keys, for instance as an index in a AttrList.TimeList object.
    The class also stores the current time in a TheTime attribute, which can
    be accessed by anyone
    """
    def __init__(self):
        # Some timedelta objects with standard time amounts
        self.day = timedelta(days=1)
        self.hour = timedelta(hours=1)
        self.minute = timedelta(minutes=1)
        self.second = timedelta(seconds=1)
        self.year = timedelta(weeks=52)
        self.tz = "US/Pacific"
        self.__dayone = None # First day, used in julian day calculation
        self.__current = None # Current time

    def Start(self, start, dt=None, stop=None, spin=0, tz="US/Pacific"):
        """Initialize the clock to some default values and get ready to run"""
        #Make sure the start, stop and dt values are datetime instances
        if (not isinstance(start, datetime)) or (stop and not isinstance(stop, datetime)):
            raise Exception("Start and stop times much be Python datetime.datetime instances.")
        if dt and not isinstance(dt,timedelta):
            raise Exception("dt must be a Python datetime.timedelta instance.")
        # Some values used in internal calculations
        self.tz = tz # The timezone definition
        self.__start = self.MakeDatetime(start, tz) # Ensures that the timezone is correct
        self.__dt = dt or self.minute # There's a default dt of one minute
        self.dst = timedelta(hours=0) # whether we're in daylight savings time or not
        self.__stop = stop or self.__start + self.day # There's a default runtime of one day
        self.__current = self.__start - timedelta(days=spin) if spin else self.__start
        self.__spin_start = self.__start # Start of the spin-up period
        self.__spin_current = self.__start # Current time within the spinup period
        self.__dayone = datetime(self.__start.year,1,1,tzinfo=TZ[tz])
        self.__thisday = self.__current-self.__dt # Placeholder for deciding whether we have to recalculate the julian day
        self.__jd = None # Placeholder for current julian day
        self.TheTime = self.__spin_current #TheTime should always return the current clock time, even in spin-up

    def Tick(self):
        """Tick() -> datetime

        Advance the clock one timestep and return new current time. This method
        advances the clock one timestep. If we are in a spin-up period,
        it tests whether the advance would move us to the next day and if so it
        reverts to the begining of the spin-up day, thus running a single day over
        and over until the spin-up time is complete."""
        # First we increment the current time by dt
        self.__current += self.__dt
        # Then test whether we're still spinning up
        if self.__current < self.__start: # If we're still in the spin-up period
            if ((self.__spin_current+self.__dt)-self.__spin_start).days: #Make sure we don't advance to next day (i.e. just run the first day over and over)
                self.__spin_current = self.__spin_start # We would have advanced, so we start again on the first day
            else:
                self.__spin_current += self.__dt # We're spinning up and haven't advanced, so use the current spin-up time
            # Set TheTime according to either spin_current or current and then return it
            self.TheTime = self.__spin_current
        else:
            self.TheTime = self.__current
        return self.TheTime
    def __iter__(self):
        if not self.__start or not self.__dt:
            raise Exception("Must call %s with the Start() method before using." % self.__class__.__name__)
        while self.__current <= self.__stop:
            yield self.__current
            self.Tick()
    def __len__(self): return len([i for i in self])
    ###########################################################
    ## Property methods
    #
    # Each property should have a GetProperty() and a SetProperty() method. The SetProperty()
    # Should make sure that the property is a datetime (or whatever), try to convert it if it
    # is not, and raise a TypeError if conversion fails. This insures that we don't send the
    # wrong class when we try to set our property equal to something.
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
    # The following properties raise AttributeErrors in the Set method to protect them from being overwritten from the outside
    def SetJD(self, value): raise AttributeError("You can't tell Chronos the time, he only tells you!")
    def GetJD(self):
        # Returns the celestial julian day
        # We store thisday so that we only calculate the julian day if it's necessary to save time.
        if self.__thisday == self.__current:
            return self.__jd
        else:
            self.__thisday = self.__current
            self.__jd = self.FracJD()
            return self.__jd
    def SetJDC(self, value): raise AttributeError("You can't tell Chronos the time, he only tells you!")
    def GetJDC(self):
        # Returns the celestial julian century
        return self.FracJDC()
    def SetJDay(self, value): raise AttributeError("You can't tell Chronos the time, he only tells you!")
    def GetJDay(self):
        # Returns the number of days from Jan 1 of the current year.
        if self.__dayone.year != self.__current.year:
            self.__dayone = datetime(self.__current.year,1,1,tzinfo=self.tz)
        return (self.__current - self.__dayone).days
    def SetCurrent(self, value): raise AttributeError("You can't tell Chronos the time, he only tells you!")
    def GetCurrent(self): return self.__current

    start = property(GetStart, SetStart)
    dt = property(GetDT, SetDT)
    stop = property(GetStop, SetStop)
    JD = property(GetJD, SetJD)
    JDC = property(GetJDC, SetJDC)
    JDay = property(GetJDay, SetJDay)
    CurrentTime = property(GetCurrent, SetCurrent)

    def FracJD(self, t=None):
        """FracJD([time])-> floating point julian day

        Takes a datetime object in UTC and returns a fractional julian date
        according to the Naval Observatory calculations. The method rounds
        the resulting floating point number to 5 places to conform with the
        Naval Observatory's online system"""
        # Default to the current time
        t = t or self.__current
        # Calculate the UTC time if we are not already in UTC
        if not t.tzinfo == TZ["UTC"]:
            t = self.GetUTC(t)
        # Then break out the time into a tuple
        y,m,d,H,M,S,tz = self.makeTuple(t)
        #H -= t.tzinfo.dst(t).seconds == 3600 # Correct the time for DST
        dec_day = d + (H + (M + S/60)/60)/24

        if m < 3:
            m += 12;
            y -= 1;
        # TODO: Figure out which of these options are correct.
        # The first one, using dec_day, is taken from literature I found:
        # julian_day = math.floor(365.25*(y+4716.0)) + math.floor(30.6001*(m+1)) + dec_day - 1524.5;
        # The second is taken from the VB code
        julian_day = int(365.25*(y+4716.0)) + int(30.6001*(m+1)) + d - 1524.5;
        #(I've stayed with the VB version for consistency)

        # This value should only be added if we fall after a certain date
        if julian_day > 2299160.0:
            a = int(y/100)
            b = (2 - a + int(a/4))
            julian_day += b

        return round(julian_day,5) #Python numerics return to about 10 places, Naval Observatory goes to 5

    def FracJDC(self, t=None):
        """FracJDC([time])-> floating point julian century

        Takes a datetime object in UTC and returns the calculated julian century"""
        t = t or self.__current # default to
        return round((self.JD-2451545.0)/36525.0,10) # Eqn. 2-5 in HS Manual

    def GetJD(self, t=None):
        """GetJD([time])-> (JD, JDC)

        Returns a tuple of julian date and julian century"""
        t = t or self.__current
        jdc = self.FracJDC(t) # Calcs both JD and JDC, but only returns JDC
        return self.JD,self.JDC

    def TZOffset(self, t=None):
        """TZOffset([time])-> integer

        Takes a datetime object and returns the signed integer offset from UTC"""
        t = t or self.__current
        return 24 - (t.utcoffset().seconds/3600)
    def GetUTC(self, t=None):
        """GetUTC([time])-> datetime

        Return UTC version of a datetime object"""
        t = t or self.__current
        s = t.replace(tzinfo=TZ["UTC"]) # Replace our timezone info
        s -= t.tzinfo.utcoffset(t) - self.dst #then subtract the offset and daylight adjustment and return the object
        return s
    def MakeDatetime(self, t=None, tz=None):
        """MakeDatetime([time],[timezone])-> datetime

        Returns a new datetime instance, with a given timezone, by calling makeTuple()"""
        if not t:
            return self.__current
        tz = tz or self.tz
        y,m,d,H,M,S,dst = self.makeTuple(t)
        return datetime(y,m,d,H,M,S,tzinfo=dst)
    def makeTuple(self, t=None, tz=None):
        """makeTuple([time],[timezone])-> (y,m,d,H,M,S,TZ)

        Make a tuple from a datetime, time or other tuple"""
        t = t or self.__current
        # Set the timezone to the argument, or self.tz
        try:
            zone = TZ[tz] or t.tzinfo or TZ[self.tz] # If given a Datetime object, us that in order of precidence (sp?)
        except (AttributeError,KeyError): # We failed on t.tzinfo, catch the exception
            zone = TZ[tz] if tz else TZ[self.tz]
#        except KeyError:
#            print TZ[self.
#            raise
        try:
            if isinstance(t,tuple):
                y,m,d,H,M,S = t
            else:
                y,m,d,H,M,S = time.strptime(t.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S")[:6] # Strip out the time info
        except AttributeError, detail:
            if detail.__str__() == "'datetime.datetime' object has no attribute 'Format'":
                y, m, d, H, M, S = t.timetuple()[:6]
            else:
                print t
                raise AttributeError(detail)
        return y,m,d,H,M,S,zone

