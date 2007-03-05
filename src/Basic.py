from __future__ import division
from Utils.ProgressBar import ProgressBar
import wx
from Excel.HeatSourceInterface import HeatSourceInterface

app = wx.App()
app.MainLoop()

"""Junker test class to make sure things are running and test out options"""

# This is a transliterated version of the subroutine called theModel in the
# original VB code

# TODO: Implement cross-platform path capabilities

# The original code calls a subroutine called BFMorph which calculates the
# Bottomwidth, max depth, etc. We no longer do that separately but calculate
# it when the StreamNode is built because it is StreamNode specific. It is
# Now calculated in HeatSourceInterface.BuildStreamNodes()

# The original version clears a bunch of data in different ways. With a live
# link between internal data and interface, this would be unnecessary...
# Way to go, Micro$oft.
# TODO: Perhaps we should query the user here to see if they want to clear
# all of the data.
# HS.SetupSheets1() # moved to HS's constructor

# The next sub basically counts the number of streamnodes. This is a pretty
# meaningless function, because with the StreamNode class, we build a list
# of them in the HeatSourceInterface, so we should be able to work around this
# and then just call len(HS.StreamNodeList) on the rare occasions when it is
# actually necessary. However, since much of the later un-reworked code needs
# it still, we will do it for now. This comes before BasicInputs here because
# we want to build the StreamNodes before the BasicInputs subroutine
# HS.UpdateQVarCounter() # moved to HS's constructor

# This routine checks for the validity of input. This is a fairly stupid way
# to do this, rather than creating input validators for the spreadsheet itself.
# We should consider just making it impossible to enter a string into a numeric
# cell, rather than allowing it and then checking every single cell to make sure
# that it didn't happen
# HS.CheckMorphologySheet() # moved to HS's constructor

# This was called something like RedimVariables1 in the original code. The
# purpose was to set all the variables to zero and then fill the various arrays
# with data from the spreadsheet. Rather, here we decide to just use the
# spreadsheet to generate StreamNode instances and add them to the main container.
# HS.BuildStreamNodes() # moved to HS's constructor

# The next sub originally set the meridian and the timezone based on what the user
# inputs. Rather than set the timezone as a separate variable, we are using
# a Datetime class for time, which has timezone builtin. I have not yet
# found where meridian is used, when I do, I will implement it if it's needed.

# This subroutine does some more setting up, much of which should just be done
# in the constructor of the HS instance, or within the StreamNode, or in a much
# more elegant place than here. It's kept here for now to reduce uncertainty
# between this and the VB code's differences.
# HS.BasicInputs() # moved to HS's constructor

# the next routine was RedimVariables number 2, and is completely pointless in
# Python, since we have dynamically sized containers and the StreamNode class.

# Next, a bunch of global variables were set. These globals are really bad form
# and should be removed since they are not really 'global' in the python sense
# anyway.
HS = HeatSourceInterface("C:\\eclipse\\HeatSource\\Toketee_CCC.xls")

# If the needles in your eyes weren't enough, now things REALLY start getting painful!
# This loop cycles over the model distance timesteps and calls the two functions
# for each model timestep.
# This has now all been moved to the constructor of HS, since it all has to be loaded
# regardless, there's no reason to keep it global. Now, all of this get's done
# automagically when we build a HS instance.
#while theDistance >= 0:
#    HS.LoadModelVariables(Node, theDistance, Count_Q_Var, Flag_HS)
#    if Flag_HS != 2: HS.CalculateInitialConditions(Node, theDistance,Flag_BC, Flag_HS)
#    HS.SetupSheets2(Node, Count_Q_Var, theDistance)
#    theDistance = theDistance - (HS.IniParams.Dx / 1000)
#    Node = Node + 1
#    PB("Loading model variables")



# This next method has been moved to the StreamNode, and it is not necessary to
# have it in the above loop, especially since you can map a function to the StreamNodeList
