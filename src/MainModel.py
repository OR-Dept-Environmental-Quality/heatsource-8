from __future__ import division
from datetime import datetime, timedelta
import time

from Time.TimeUtil import TimeUtil
from Excel.HeatSourceInterface import HeatSourceInterface
from Solar.Helios import Helios
from Time.Chronos import Chronos
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
        self.Helios = Helios.getInstance()
        #######################################################
        ## Time class objects
        # Create a time manipulator for making time objects
        self.TimeUtil = TimeUtil()

        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(minutes=self.IniParams.dt)
        start = self.TimeUtil.MakeDatetime(self.IniParams.Date)
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
#                map(lambda x:x.ViewToSky(),self.Reach)
                for node in self.Reach:
                    for k in node.__slots__:
                        print k,
                        try: print getattr(node,k)
                        except: print "None"
                    for k in node.slots:
                        print k,
                        try: print getattr(node,k)
                        except: print "None"
                    import sys
                    sys.exit()
            except:
                raise
                return False
            n+=1
            self.Log("Running...",n,max)
        return True
    def Stop(self):
        pass
