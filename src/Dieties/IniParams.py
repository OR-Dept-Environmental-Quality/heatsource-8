from __future__ import division
from psyco.classes import psyobj

class IniParamsDiety(psyobj):
    """A class to hold user-defined data that is static throughout a model run

    This is often the data that is in the 9th column, rows 2-13, of most of the
    original Excel Heat Source pages. However, it is a generalized class that
    is useful for holding other user-defined/static data as well. This class is
    a Singleton class, meaning that there is only one live instance of it at any
    time."""
    def __init__(self,**kwargs):
        d = {'Name': None,
             'Date': None,
             'dt': None, # This time should be in seconds.
             'dx': None, # This should be in meters
             'Length': None, # kilometers
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
             'Wind_A': 1.505e-9, #Default wind values taken from Umpqua:Toketee basin model
             'Wind_B': 1.6e-9,
             'Penman': False, # IU1 and IT1. Here, True:Penman Combination method, False: Jobson Wind Method
             'DryChannel': False, # Flag in original code to tell us whether we accept dry channels?
             'ChannelWidth': True # Flag meaning we know that our channel widths are over bounding.
             }
        # If any of these are in the constructor, replace the values with them.
        for key in d.keys():
            if key in kwargs.keys():
                d[key] = kwargs[key]
            setattr(self,key,d[key])
IniParams = IniParamsDiety()