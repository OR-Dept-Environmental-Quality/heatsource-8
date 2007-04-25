from __future__ import division
from datetime import datetime, timedelta
import time, sys, wx, random

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Helios import Helios
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.DynaPlot import DynaPlot, TIMER_ID

global app

class TimeStepper(wx.Timer):
    def __init__(self, cb):
        wx.Timer.__init__(self)
        self.cb = cb

    def Notify(self):
        self.cb()

class MainModel(object):
    def __init__(self, filename,log):
        self.Log = log
        self.filename = filename

    def __del__(self):
        DPlot.Destroy()

    def Initialize(self):
        self.Log("Initializing Model")
        self.Reach = HeatSourceInterface(self.filename,gauge=self.Log).Reach
        self.Log("Initialization Complete, %i stream nodes built"% len(self.Reach))
#        self.DPlot = DynaPlot()
#        self.PlotAttr = "Q" # Attribute to plot at the reach level
#        self.X = [n.km for n in self.Reach]
#        self.Y = [0 for i in xrange(len(self.Reach))]
#        self.DPlot.Show()
#        self.DPlot.Initialize(self.X, self.Y)
        self.timer = TimeStepper(self.TimeStep)
    def Reset(self):
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=IniParams.dt)
        start = Chronos.MakeDatetime(IniParams.Date)
        stop = start + timedelta(days=IniParams.SimPeriod)
        spin = 0 # IniParams.FlushDays # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        ##########################################################
    def Run(self):
        self.Reset()
        self.timer.Start(100)

    def TimeStep(self):
        try:
#            del self.Y[:]
            if Chronos.TheTime > Chronos.start + timedelta(minutes=59):
                pass
            # Calculate the hydraulics
            map(lambda x:x.CalcHydraulics(), self.Reach)
#            [self.Y.append(getattr(node,self.PlotAttr)) for node in self.Reach]
            # Calculate the solar flux
#            map(lambda x:x.CalcSolarFlux(), self.Reach)
#            self.DPlot.onTimer(False)
            Chronos.Tick()
            return True
        except:
            self.Stop()
            raise

    def Stop(self):
        self.timer.Stop()
        self.DPlot.Destroy()
