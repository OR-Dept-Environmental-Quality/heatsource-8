from __future__ import division
from datetime import datetime, timedelta
import time

from Time.TimeUtil import TimeUtil
from Excel.HeatSourceInterface import HeatSourceInterface
from Solar.SolarRad import TheSun
from Time.TimeStepper import TimeStepper
from Containers.IniParams import IniParams
from Containers.BoundCond import BoundCond

class MainModel(object):
    def __init__(self, filename,log):
        self.Log = log
        self.filename = filename
    def Initialize(self):
        self.Log("Initializing Model")
        self.HS = HeatSourceInterface(self.filename,gauge=self.Log)
        self.Reach = self.HS.Reach
        self.Log("Initialization Complete, %i stream nodes built"% len(self.Reach))
        self.IniParams = IniParams.getInstance()
        self.Bounds = BoundCond.getInstance()
        self.TheSun = TheSun.getInstance()
        #######################################################
        ## Time class objects
        # Create a time manipulator for making time objects
        self.TimeUtil = TimeUtil()

        ##########################################################
        # Create a TimeStepper iterator
        dt = timedelta(minutes=self.IniParams.dt)
        start = self.TimeUtil.MakeDatetime(self.IniParams.Date)
        stop = start + timedelta(days=self.IniParams.SimPeriod)
        self.Timer = TimeStepper(start, dt, stop)
        ##########################################################
    def Run(self):
        max = len(self.Timer)
        n = 0
        for t in self.Timer:
            try:
#                self.CalcSolarPosition(t)
                map(lambda x:x.ViewToSky(),self.Reach)
                map(lambda x:x.CalcHydraulics(t),self.Reach)
            except:
                raise
                return False
            n+=1
            self.Log("Running...",n,max)
        return True
    def Stop(self):
        pass
