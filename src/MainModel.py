from __future__ import division
from datetime import datetime, timedelta
import time, sys

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Helios import Helios
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams

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
        self.Helios = Helios.getInstance()
        self.Chronos = Chronos.getInstance()
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(minutes=self.IniParams.dt)
        start = self.Chronos.MakeDatetime(self.IniParams.Date)
        stop = start + timedelta(days=self.IniParams.SimPeriod)
        self.Chronos = Chronos.getInstance()
        # Other classes hold references to the instance, but only we should Start() it.
        self.Chronos.Start(start, dt, stop)
        ##########################################################
    def Run(self):
        max = len(self.Chronos)
        n = 0
        for t in self.Chronos:
            try:
                for node in self.Reach:
                    node.CalcHydraulics()
                    node.CalcSolarPosition()
                    sys.exit()
            except:
                raise
                return False
            n+=1
            self.Log("Running...",n,max)
        return True
    def Stop(self):
        pass
