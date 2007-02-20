from __future__ import division
import datetime, pytz, time, math

class TimeUtil(object):
    """Return a pytz.datetime object built from a time taken from the data"""
    def __init__(self):
        # Make places to hold Julian date for inter-method communication
        self.JD = None
        # And a place to hold time tuple info
        self.y = self.m = self.d = None
        self.H = self.M = self.S = None
    def getTup(self): return self.y,self.m,self.d,self.H,self.M,self.S
    tup = property(getTup)
    def makeTuple(self, t):
        """Populate time tuple info"""
        try:
            self.y,self.m,self.d,self.H,self.M,self.S = time.strptime(t.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S")[:6] # Strip out the time info
        except AttributeError, detail:
            if detail.__str__() == "'datetime.datetime' object has no attribute 'Format'":
                self.y, self.m, self.d, self.H, self.M, self.S = t.timetuple()[:6]
            else: raise AttributeError(detail)
    def MakeDatetime(self, t, tz="US/Pacific"):
        dst = pytz.timezone(tz) # Make a local timezone object
        self.makeTuple(t)
        return datetime.datetime(self.y,self.m,self.d,self.H,self.M,self.S,tzinfo=dst) #Create a datetime object that is set to the local timezone
    def FracJD(self, t):
        """Takes a datetime object in UTC and returns a fractional julian date"""
        if not t.tzinfo == pytz.utc:
            t = self.GetUTC(t)
        self.makeTuple(t)
        dec_day = self.d + (self.H + (self.M + self.S/60)/60)/24
        if self.m < 3:
            self.m += 12;
            self.y -= 1;
        julian_day = math.floor(365.25*(self.y+4716.0)) + math.floor(30.6001*(self.m+1)) + dec_day - 1524.5;

        if julian_day > 2299160.0:
            a = math.floor(self.y/100);
            julian_day += (2 - a + math.floor(a/4));

        self.JD = round(julian_day,5) #Python numerics return to about 10 places, Naval Observatory goes to 5
    def FracJDC(self, t):
        """Takes a datetime object in UTC and returns the calculated julian century"""
        self.FracJD(t) #Set the fractional julian time, even if it's set already (because it might be a leftover from a previous call)
        return round((self.JD-2451545.0)/36525.0,10) # Eqn. 2-5 in HS Manual

    def GetJD(self, t):
        """Returns a tuple of julian date and julian century"""
        jdc = self.FracJDC(t) # Calcs both JD and JDC, but only returns JDC
        return self.JD,jdc

    def TZOffset(self, t):
        """Takes a datetime object and returns the signed integer offset from UTC"""
        return 24 - (t.utcoffset().seconds/3600)
    def GetUTC(self, t):
        """Return UTC version of a datetime object"""
        s = t.replace(tzinfo=pytz.utc) # Replace our timezone info
        return s - t.tzinfo._utcoffset #then subtract the offset and return the object
