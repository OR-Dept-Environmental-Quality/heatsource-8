from ConfigParser import SafeConfigParser,NoOptionError
from platform import platform
from os import environ, path
from datetime import datetime, time
from time import strptime

def opj(path):
    """Convert paths to the platform-specific separator"""
    str = apply(path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        str = '/' + str
    return str

# Some parameters that are modeling specific. Eventually, these will be in
# separate sections by model name, then we can list the current models we
# know about. Path will be added as a parameter and Name will be pushed up
# to the section. But for now we'll just add it at the top level.
ModelParams = {'Name': None,
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
                'SimPeriod': None}
# Some things from the original VB code. These things were
# hidden in Excel cells with addresses like IV22, which were in
# hidden columns that the user couldn't access without significant
# knowledge. It seems like these should never change, since most
# users probably don't know they exist. I put them in here in case
# we want to allow change later.
defaults = (('Muskingum',"True"), # IS1
             ('EvapLoss',"False"), # IV1
             ('Emergent',"False"),# IV5
             ('Wind_A',`1.505e-9`), #Default wind values taken from Umpqua:Toketee basin model
             ('Wind_B',`1.6e-9`),
             ('Penman',"False"), # IU1 and IT1. Here, True:Penman Combination method, False: Jobson Wind Method
             ('DryChannel',"no"), # Flag in original code to tell us whether we accept dry channels?
             ('ChannelWidth',"True") # Flag meaning we know that our channel widths are over bounding.
             )

class IniParamsDiety(object):
    """Create an IniParams dictionary"""
    def __init__(self):
        self.Parser = Parser = SafeConfigParser()
        Parser.add_section("User")
        home = path.expanduser("~") # Users HOME
        self.filename = path.join(home,"HSfiles","heatsource.ini")
        Parser.set("User","RootDirectory",path.join(home,"HSfiles"))
        Parser.set("User","TempDirectory",path.join(home,"HSfiles","Temp"))
        Parser.set("User","DataDirectory",path.join(home,"HSfiles","Data"))
        # Check if we have a known inifile in ${HOME}/HSfiles/heatsource.ini
        if not len(Parser.read([self.filename])):
            print "test"
            Parser.read(self.findIniFiles())
        for k,v in defaults:
            if not Parser.has_option("User", k):
                Parser.set("User",k,v)
        f = open(self.filename,'w')
        self.Parser.write(f)
        f.close()
    def __getitem__(self,key):
        if not self.Parser.has_option: raise KeyError(key)
        # Get the value as a string
        val = self.Parser.get("User",key)
        # Try to coerce it to a boolean, otherwise keep it
        try: val = self.Parser.getboolean("User",key)
        except: pass
        # Try then to coerce it to a float, otherwise keep it
        try: val = self.Parser.getfloat("User",key)
        except: pass
        # Try to coerce to a datetime object, otherwise keep it
        if key == "Date":
            return datetime(*strptime(val,"%m/%d/%y %H:%M:%S")[:6])
        # If we have a path, normalize it
        if "Directory" in key or "Path" in key:
            val = path.normpath(path.join(*path.split(val)))

        return val
    def __setitem__(self, key, value):
        if key == "Date":
            value = value.Format("%m/%d/%y %H:%M:%S")
        else:
            value = `value` if not isinstance(value,str) else value
        self.Parser.set("User",key,value)
    def __delitem__(self, key):
        self.Parser.remove_option("User",key)
    def __del__(self):
        f = open(self.filename)
        self.Parser.write(f)
        f.close()

    def findIniFiles(self):
        """Search a list of possible directories, returning the first instance of the HS inifile

        The HS inifile must be named 'heatsource.ini' and must be a file readable by the
        ConfigParser class. If the file is not found, a default dictionary is created in
        a folder named hs_files in the user's home directory. This is the directory returned
        by os.path.expanduser('~'), which should work on both Windows and *nix."""
        # Make a list of possible search paths by platform
        if "Win" in platform(terse=True) or "win" in platform(terse=True):
            dirs = ("C:\\","C:\\Temp","C:\\Documents and Settings")
        else:
            dirs = ("/")
        dirs += path.expanduser("~"), # Users HOME
        # All possible directories returned by os.environ dictionary
        l = ("TMP","COMMONPROGRAMFILES","PROGRAMFILES","SYSTEMROOT","TEMP","ALLUSERSPROFILE","HOMESHARE","WINDIR","APPDATA","USERPROFILE")
        for d in l:
            a = environ[d]
            dirs += a,
        # One more, incase it's different from what expanduser() returns
        dirs += path.join(environ["HOMEDRIVE"],environ["HOMEPATH"]),
        # Now, remove all duplicates
        import sets
        dirs = tuple(sets.Set(dirs))
        # Add additional paths ending in 'HSfiles'
        dirs += tuple(path.join(i,"HSfiles") for i in dirs)

        # All realistic capitalization forms of the inifile
        names = ["HeatSource"]
        # The following will be needed for *nix filesystems, which are case sensitive
        if "Win" not in platform(terse=True) and "win" not in platform(terse=True):
            names += ["heatsource","Heatsource","heatSource","HEATSOURCE"]
        exts = ["",".ini",".txt"]

        pathlist = []
        for dir in dirs:
            for name in names:
                for ext in exts:
                    pathlist.append(path.join(dir,name+ext))
        # We walked the tree and found all the inifiles, now we parse the first good one
        return pathlist

IniParams = IniParamsDiety()