from __future__ import division
from datetime import datetime, timedelta
import time

from Utils.TimeUtil import TimeUtil
from Excel.HeatSourceInterface import HeatSourceInterface
from SolarRad import SolarRad
from Utils.TimeStepper import TimeStepper
from Utils.IniParams import IniParams
from Utils.BoundCond import BoundCond

class MainModel(object):
    def __init__(self, filename,log):
        self.Log = log
        self.filename = filename
    def Initialize(self):
        self.HS = HeatSourceInterface(self.filename,gauge=self.Log)
        self.Reach = self.HS.Reach
        self.Log("Initialization Complete, %i stream nodes built"% len(self.Reach))
        self.IniParams = IniParams.getInstance()
        self.Bounds = BoundCond.getInstance()
        self.SolarRad = SolarRad.getInstance()
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
        for t in self.Timer:
            self.Log(t)
            time.sleep(30)
        return True
    def Stop(self):
        pass