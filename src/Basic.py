from __future__ import division
from Utils.ProgressBar import ProgressBar
import wx, math
from datetime import timedelta, datetime
from Excel.HeatSourceInterface import HeatSourceInterface
from SolarRad import SolarRad
from Utils.TimeStepper import TimeStepper
from Utils.IniParams import IniParams
from Utils.BoundCond import BoundCond

app = wx.App()
app.MainLoop()

"""Junker test class to make sure things are running and test out options"""
IniParams = IniParams.getInstance()
HS = HeatSourceInterface("..\\Toketee_CCC.xls")
# There's a timestepper built in HS, so we'll just use that for now
Timer = HS.Timer
# HS also builds the stream reach, but that should be local to here.
Reach = HS.Reach
# Get the boundary conditions class
Bounds = BoundCond.getInstance()
# SolarRad class, to hold and calculate solar variables
Solar = SolarRad.getInstance()

for time in Timer:
    Solar.ResetSolarVars(time)
    map(lambda x: x.CalcHydraulics(time), Reach)
