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
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(minutes=IniParams.dt)
        start = Chronos.MakeDatetime(IniParams.Date)
        stop = start + timedelta(days=IniParams.SimPeriod)
        spin = 0 # IniParams.FlushDays # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        ##########################################################
    def Run(self):
        max = len(Chronos)
        n = 0
        for t in Chronos:
            self.Log("Running...",n,max)
            try:
                for node in self.Reach:
                    node.CalcHydraulics()
                    node.CalcSolarFlux()
            except:
                raise
                return False
            n+=1
        return True
    def Stop(self):
        pass
