#IniParams is a simple dictionary, since we need nothing more than this. This way,
# it can be more easily read in from a user-defined file.
IniParams = {'Name': None,
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
             'ChannelWidth': True, # Flag meaning we know that our channel widths are over bounding.
             'OutputDirectory':"C:\\Temp\\HeatSource\\"
             }
