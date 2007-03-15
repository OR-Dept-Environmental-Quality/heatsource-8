"""Test module to spit out and check HeatSource information"""

########################################
# Import the graphical user interface library, and start it up so that
# we can spit out a progress bar
import wx
app = wx.App()
app.MainLoop()
#######################################

###########################################
# Import the HeatSourceInterface class and create an instance with
# the Umpqua Toketee file
from Excel.HeatSourceInterface import HeatSourceInterface
# This assumes this file exists.
# This will run the entire setup. What you have left- assuming I don't
# make it fail, will be a fully live instance
HS = HeatSourceInterface("c:\\eclipse\\HeatSource\\Toketee_CCC.xls")
###########################################

############################################
# Open a file in the windows temp directory

filename = "first.out" # Easier to change as a variable
f = open(filename, 'w') # Open the file writable
def write(line):
    """Write a given line to the file, with a newline at the end"""
    line += "\n"
    f.write(line)

############################
# Do stuff
# At this point, it might be useful for you to comment things out of your local version of
# HeatSourceInterface()
# Go to the __initialize() method, which is called from __init__(), and start at the bottom.
# (Leave "del self.PB" alone, it just deletes the progress bar.
# I would comment out the following to start:
#
#        self.ScanMorphology()
#        self.BuildStreamNodes()
#        self.GetInflowData()
#        self.GetContinuousData()
#        map(lambda x:x.ViewToSky(),self.Reach)
#        map(lambda x:x.CalcStreamGeom(),self.Reach)
#
# Which will mean that the HS = ... line above will just run the GetBoundaryConditions()
# method. This way, you can do the following

BC = HS.BC # Get the boundary conditions class
print BC.Q[0:5] # print first 5 elements

line = "" # Create a string
for val in BC.Q: # Cycle through the values in the discharge boundary conditions
    line += "%s," % val # Add each to the string, with a comma after it
line = line[:-1] # remove the last character, which is a final comma because I'm lazy
write(line) # write the values to a file, comma separated

f.close() # CLOSE THE FILE!!