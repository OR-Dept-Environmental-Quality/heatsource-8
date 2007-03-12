from __future__ import division
from SingletonMixin import Singleton
class IniParams(Singleton):
    """A class to hold user-defined data that is static throughout a model run

    This is often the data that is in the 9th column, rows 2-13, of most of the
    original Excel Heat Source pages. However, it is a generalized class that
    is useful for holding other user-defined/static data as well. This class is
    a Singleton class, meaning that there is only one live instance of it at any
    time."""
    def __init__(self,**kwargs):
        self.data = {'Name': None,
                     'Date': None,
                     'dT': None,
                     'dx': None,
                     'Length': None,
                     'LongSample': None,
                     'TransSample': None,
                     'InflowSites': None,
                     'ContSites': None,
                     'FlushDays': None,
                     'TimeZone': None,
                     'SimPeriod': None,
                     # Some things from the original VB code. These things were
                     # hidden in Excel cells with addresses like IV22, which were in
                     # hidden columns that the user couldn't access without significant
                     # knowledge. It seems like these should never change, since most
                     # users probably don't know they exist. I put them in here in case
                     # we want to allow change later.
                     'Muskingum': True, # IS1
                     'EvapLoss': False, # IV1
                     'Emergent': False,# IV5
                     'Penman': False, # IU1 and IT1. Here, True:Penman Combination method, False: Jobson Wind Method
                     'DryChannel': False # Flag in original code to tell us whether we accept dry channels?
                     }
        # If any of these are in the constructor, replace the values with them.
        for key in self.data.keys():
            if key in kwargs.keys():
                self.data[key] = kwargs[key]

    # Make everything accessible via the property() method for convenience
    def SetName(self,val): self.data['Name'] = val
    def SetDate(self,val): self.data['Date'] = val
    def SetDT(self,val): self.data['dT'] = val
    def SetDx(self,val): self.data['dx'] = val
    def SetLength(self,val): self.data['Length'] = val
    def SetLongSample(self,val): self.data['LongSample'] = val
    def SetTranSample(self,val): self.data['TransSample'] = val
    def SetInflowSites(self,val): self.data['InflowSites'] = val
    def SetContSites(self,val): self.data['ContSites'] = val
    def SetFlushDays(self,val): self.data['FlushDays'] = val
    def SetTimeZone(self,val): self.data['TimeZone'] = val
    def SetSimPeriod(self,val): self.data['SimPeriod'] = val

    def GetName(self): return self.data['Name']
    def GetDate(self): return self.data['Date']
    def GetDT(self): return self.data['dT']
    def GetDx(self): return self.data['dx']
    def GetLength(self): return self.data['Length']
    def GetLongSample(self): return self.data['LongSample']
    def GetTranSample(self): return self.data['TranSample']
    def GetInflowSites(self): return self.data['InflowSites']
    def GetContSites(self): return self.data['ContSites']
    def GetFlushDays(self): return self.data['FlushDays']
    def GetTimeZone(self): return self.data['TimeZone']
    def GetSimPeriod(self): return self.data['SimPeriod']

    Name = property(GetName, SetName, doc="Name of the simulation")
    Date = property(GetDate, SetDate, doc="Simulation start date")
    dT = property(GetDT, SetDT, doc="Time step in minutes")
    dx = property(GetDx, SetDx, doc="Distance step in meters")
    Length = property(GetLength, SetLength, doc="Stream Length in kilometers")
    LongSample = property(GetLongSample, SetLongSample, doc="Longitudinal sample rate in meters")
    TranSample = property(GetTranSample, SetTranSample, doc="Transverse sample rate in meters")
    InflowSites = property(GetInflowSites, SetInflowSites, doc="Inflow sites")
    ContSites = property(GetContSites, SetContSites, doc="Continuous data sites")
    FlushDays = property(GetFlushDays, SetFlushDays, doc="Flush initial conditions (days)")
    TimeZone = property(GetTimeZone, SetTimeZone, doc="Timezone (e.g. US/Pacific)")
    SimPeriod = property(GetSimPeriod, SetSimPeriod, doc="Simulation period in days")
