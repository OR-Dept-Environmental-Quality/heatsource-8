"""Test module to spit out and check HeatSource information"""
import os
path = os.path
from warnings import simplefilter

def GetRelative(name, levels):
    """Return a path to a file 'name' that is 'levels' directory 
    levels above the current directory in the tree"""
    dir = path.split(os.getcwd())
    for i in xrange(levels):
        dir = path.split(dir[0])
    return path.join(dir[0], name)

#######################################
# Turn of Metta's warnings and programming comments
simplefilter('ignore', UserWarning)

###########################################
# Import the HeatSourceInterface class and create an instance with
# the Umpqua Toketee file
from Excel.HeatSourceInterface import HeatSourceInterface
# This assumes this file exists.
# This will run the entire setup. What you have left- assuming I don't
# make it fail, will be a fully live instance
HS = HeatSourceInterface(GetRelative('Toketee_CCC.xls',1))
###########################################

############################################
# Open a file in the windows temp directory

# Filenames are easier to change as a variable, remember to escape the
# backslashes
filename = "d:\\Temp\\data.out"
f = open(filename, 'w') # Open the file writable
# Note that the open() function returns a class instance that is actually a file object.
# This is another example of the power of classes and Object-Orientation. If we did this
# the old way, we would have to operate on a single file at a time, at a very low level.
# With classes, we can open as many as we want, and use f.write(), f.close(), etc.

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
##################
# Print out some boundary condition information from the Discharge conditions
BC = HS.BC # Get the boundary conditions class
print BC.Q[0:5] # print first 5 elements of the boundary conditions

# temporary function that prints the attribute of a value, use as attr(object)-> object.t
attr = lambda x: x.t

# maps a function to a list, so that the given function is called for each object in
# a list, with that object as the argument. Returns a list.
l = map(attr,BC.Q)
print l[0:5] # print the time attribute of the first 5 elements of the boundary conditions

# That command print the time key, which is a Python datetime object, let's print it in
# a more readable fashion. The datetime object has a method called isoformat, which prints
# the time in a human readable format. Since the lambda construct above returns x.t, and t
# is the datetime object, we can use x.t.isoformat() in the lambda construct. Lets put it all
# on one line, which is a bit less readable for the beginner, but more appropriately Pythonic,
# and how much code is written:
print map(lambda x: x.t.isoformat(),BC.Q)[0:5]


line = "" # Create a string
for val in BC.Q: # Cycle through the values in the discharge boundary conditions
    line += "%s," % `val` # Add each to the string, with a comma after it. The quotes make it taste better!
# write the values to a file, comma separated. We strip the last character from the line, because
# it prints an extra comma, and we're too lazy to take care of that in such a simple loop, above.
f.write(line[:-1]+"\n")

# We can actually do the above in a single loop, because the BoundCond class has an __iter__() method
# which will allow us to iterate over the entire class in a single call. Let's print a line to the
# file to separate the last command from this one:
f.write("#"*50 + "\n") # Write 50 pound signs and a newline

# Now let's iterate over the entire boundary condition class. The class's iterator returns an iterator
# over each internal list (Discharge, temperature, cloudiness) in turn.
line = "" # Clear the line
for cond in BC:
    for val in cond:
        if len(line): line += "," # Add a comma at the beginning of each conditions iteration if we're not at the beginning
        line += "%s" % `val` # add the value as a string, ignoring the comma.
    f.write(line+"\n") # write it to the file
    line = "" # Then reset the line for the next conditions list

# So, here we have an issue. If we look at the resulting file in the temp directory, we see that two lines
# of data were printed, but the BoundCond class holds boundary conditions for discharge, temp AND cloudiness.
# Thus, there's a problem because only two out of three lists printed. The problem is either in the BoundCond
# iterator, or in the way the lists are filled with data. At this point, the Eclipse debugger comes in handy.
# If you right (left) click over the left edge of the source code window, you can set a breakpoint. Then
# instead of RUNNING the program, you can DEBUG the program (Just like you set up the run, but choose
# "debug as.."). Set a breakpoint at the last for loop and look at the variables. You'll see that
# the BC variable has 4, not 3 attributes. They are Q, T, C and Cloudiness. Meaning that I fucked up the way
# the list is built and added the list to the BoundCond class. This is exactly the type of error that it
# would REALLY help to find now. I've left it as an illustration.

f.close() # CLOSE THE FILE!!