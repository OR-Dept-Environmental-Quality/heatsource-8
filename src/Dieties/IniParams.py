from ConfigParser import SafeConfigParser,NoOptionError
from platform import platform
from os import environ, path, makedirs
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
ModelParams = {'name': None,
                'Date': None,
                'dt': None, # This time should be in seconds.
                'dx': None, # This should be in meters
                'length': None, # kilometers
                'longsample': None,
                'transsample': None,
                'inflowsites': None,
                'contsites': None,
                'flushdays': None,
                'timezone': None,
                'simperiod': None}
# Some things from the original VB code. These things were
# hidden in Excel cells with addresses like IV22, which were in
# hidden columns that the user couldn't access without significant
# knowledge. It seems like these should never change, since most
# users probably don't know they exist. I put them in here in case
# we want to allow change later.
defaults = (('muskingum',1), # IS1
             ('evaploss',0), # IV1
             ('emergent',0),# IV5
             ('wind_a',`1.505e-9`), #Default wind values taken from Umpqua:Toketee basin model
             ('wind_b',`1.6e-9`),
             ('penman',0), # IU1 and IT1. Here, True:Penman Combination method, False: Jobson Wind Method
             ('drychannel',0), # Flag in original code to tell us whether we accept dry channels?
             ('channelwidth',1) # Flag meaning we know that our channel widths are over bounding.
             )

class IniParamsDiety(dict):
    """Create an IniParams dictionary"""
    def __init__(self):
        Parser = SafeConfigParser()
        Parser.add_section("User")
        home = path.expanduser("~") # Users HOME
        self.filename = path.join(home,"HSfiles","heatsource.ini")
        Parser.set("User","RootDirectory",path.join(home,"HSfiles"))
        Parser.set("User","TempDirectory",path.join(home,"HSfiles","Temp"))
        Parser.set("User","DataDirectory",path.join(home,"HSfiles","Data"))

        # Check if we have a known inifile in ${HOME}/HSfiles/heatsource.ini
        if not len(Parser.read([self.filename])):
            Parser.read(self.findIniFiles())
        for k,v in defaults:
            if not Parser.has_option("User", k):
                Parser.set("User",k,v)
        dict.__init__(self,dict((k,v) for k,v in Parser.items("User")))
        for k,v in self.iteritems():
            try:
                self[k] = float(v)
            except ValueError: pass
            if k == "date":
                try:
                    self[k] = datetime.strptime(v,"%m/%d/%y %H:%M:%S")
                except ValueError:
                    try:
                        self[k] = datetime.strptime(v,"%Y-%m-%d %H:%M:%S")
                    except:
                        raise
                else:
                    raise
        self.writeFile()
    def __del__(self):
        self.writeFile()
    def writeFile(self):
        try:
            f = open(self.filename,'w')
        except IOError:
            makedirs(path.split(self.filename)[0])
            f = open(self.filename,'w')
        f.write("[User]\n")
        for k,v in self.iteritems():
            try:
                f.write("%s = %s\n" % (k,v))
            except:
                f.write("%s = %s\n" % (k,`v`))
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
        l = ("TMP","COMMONPROGRAMFILES","PROGRAMFILES","SYSTEMROOT","TEMP","ALLUSERSPROFILE","HOME","HOMESHARE","WINDIR","APPDATA","USERPROFILE")
        for d in l:
            try:
                a = environ[d]
                dirs += a,
            except KeyError: pass
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