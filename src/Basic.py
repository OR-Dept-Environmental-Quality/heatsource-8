from __future__ import division
import wx, time
import wxaddons.sized_controls as sc
from Excel.HeatSourceInterface import HeatSourceInterface
from SolarRad import SolarRad
from Utils.TimeStepper import TimeStepper
from Utils.IniParams import IniParams
from Utils.BoundCond import BoundCond

class HSFrame(sc.SizedFrame):
    def __init__(self, parent, id):
        sc.SizedFrame.__init__(self, parent, id, "HeatSource Control Panel",
                               style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        pane = self.GetContentsPane()
        pane.SetSizerType("form")

        # row 1
        t = time.strftime("m/d/y H:M:S" % time.localtime())
        self.ErrLog = wx.TextCtrl(pane, -1, "%s: HeatSource Error Log Started"% time.now())
        self.ErrLog.SetSizerProps(expand=True)

        # row 2
        BottomPane = sc.SizedPanel(pane, -1)
        BottomPane.SetSizerType("horizontal")
        BottomPane.SetSizerProps(expand=True)

        self.PB = wx.Gauge(BottomPane, -1, "Remember: Patience is a Virtue!")
        self.PB.SetSizerProps(expand=True)

        # row 3
        wx.StaticText(BottomPane, -1, "Warnings:")
        self.NumWarnings = wx.StaticText(BottomPane, -1, "0")
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        text.SetFont(font)

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

class StderrFaker:
    def write(self, message):
        if message[-1] == '\n':
            print message[:-1]
        else:
            print message,

import sys
app = wx.App()
app.MainLoop()
sys.stderr = StderrFaker()
#HSFrame(None, -1)
"""Junker test class to make sure things are running and test out options"""
IniParams = IniParams.getInstance()

HS = HeatSourceInterface("c:\\eclipse\\HeatSource\\Toketee_CCC.xls")

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
