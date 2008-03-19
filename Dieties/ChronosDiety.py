from time import strptime, mktime, asctime, localtime
from pywintypes import Time as pyTime

try:
    from __debug__ import psyco_optimize
    if psyco_optimize:
        from psyco.classes import psyobj
        object = psyobj
except ImportError: pass

class ChronosDiety(object):
    """This class provides a clock to be used in the model timestepping.
    
    The ChronosDiety controls the current time and steps through time
    in an organized fashion based on start/stop/step functionality.
    The time is stored as seconds from the epoch. Changes to this
    class to support more advanced timezone and datetime functionality
    (as an older version had) should be pushed into a subclass."""
    def __init__(self):
        self.second = 1
        self.minute = self.second * 60
        self.hour = self.minute * 60
        self.day = self.hour * 24
        self.week = self.day * 7
        self.__dayone = None # First day, used in julian day calculation
        self.__current = None # Current time
        self.__start = None
        self.__dt = None
        self.__stop = None

    def __call__(self,tick=False):
        """Return current time as seconds since epoch
        
        Returns the current time float if called with no arguments. If tick=True,
        advances the clock one timestep and returns new current time. If we are 
        in a spin-up period, it tests whether the advance would move us to the 
        next day and if so it reverts to the begining of the spin-up day, thus 
        running a single day over and over until the spin-up time is complete."""
        # Quickly return if we're not moving forward in time
        if not tick: return self.__current
        # First we increment the current time by dt
        self.__current += self.__dt
        # Then test whether we're still spinning up
        if self.__current < self.__start: # If we're still in the spin-up period
            if ((self.__spin_current+self.__dt)-self.__spin_start).days: #Make sure we don't advance to next day (i.e. just run the first day over and over)
                self.__spin_current = self.__spin_start # We would have advanced, so we start again on the first day
            else:
                self.__spin_current += self.__dt # We're spinning up and haven't advanced, so use the current spin-up time
            # Set TheTime according to either spin_current or current and then return it
            return self.__spin_current
        else:
            return self.__current

    def __iter__(self):
        """Iterator support to allow 'for tm in Chronos' loops"""
        if not self.__start or not self.__dt:
            raise Exception("Must call %s with the Start() method before using." % self.__class__.__name__)
        while self.__current <= self.__stop:
            yield self.__current
            self(True)
    def __len__(self):
        """Length will report the number of timesteps
        
        Currently, this method will screw things up because it actually
        iterates through the sequence, cycling through time. This is a problem."""
        raise NotImplementedError("This needs some work- do we actually need it?")
        return len([i for i in self])

    def PrettyTime(self): return asctime(localtime(self.__current))
    def Year(self): return localtime(self.__current)[0]
    def Month(self): return localtime(self.__current)[1]
    def Day(self): return localtime(self.__current)[2]
    def TimeTuple(self): return localtime(self.__current)
    def ExcelTime(self): return float(pyTime(self.__current))
    
    def Start(self, start, dt=None, stop=None, spin=0, offset=0):
        """Initialize the clock to some default values and get ready to run.
        
        Initial values are starting and stopping times, timestep in seconds, number
        of days to spin up and the timezone offset in hours."""
        #Make sure the start, stop and dt values are datetime instances
        if (not isinstance(start, float) and not isinstance(start, int)) or \
            (stop and (not isinstance(stop, float) and not isinstance(stop, int))) or \
            (dt and (not isinstance(dt, float) and not isinstance(dt, int))):
            raise Exception("Start, stop times and timestep much be floating point numbers or integers.")
        # Some values used in internal calculations
        self.__offset = offset # The timezone offset, default to GMT
        self.__start = start
        self.__dt = dt or self.minute # There's a default dt of one minute
        self.__stop = stop or self.__start + self.day # There's a default runtime of one day
        self.__spin_start = self.__start- (spin*86400) if spin else self.__start # Start of the spin-up period
        self.__spin_current = self.__start # Current time within the spinup period
        self.__current = self.__spin_current
        self.__dayone = mktime((localtime(self.__start)[0],1,1,0,0,0,-1,-1,-1))
        self.__thisday = self.__current-self.__dt # Placeholder for deciding whether we have to recalculate the julian day
        self.__jd = None # Placeholder for current julian day
        
    def GetJD(self):
        """FracJD([time])-> floating point julian day

        Takes a datetime object in UTC and returns a fractional julian date
        according to the Naval Observatory calculations. The method rounds
        the resulting floating point number to 5 places to conform with the
        Naval Observatory's online system"""
        # Then break out the time into a tuple
        y,m,d,H,M,S,day,wk,tz = localtime(self.__current)
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
        jd = round(julian_day,5) #Python numerics return to about 10 places, Naval Observatory goes to 5
        jdc = round((jd-2451545.0)/36525.0,10) # Eqn. 2-5 in HS Manual
        return jd, jdc

    #####################################################
    # Properties to allow reading but no changes
    start = property(lambda self: self.__start)
    stop = property(lambda self: self.__stop)
    dt = property(lambda self: self.__dt)
    offset = property(lambda self: self.__offset)
    TheTime = property(lambda self: self.__current)
    JD = property(lambda self: self.GetJD())
    UTC = property(lambda self: gmtime(self.__current))