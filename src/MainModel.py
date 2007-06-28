from __future__ import division
from datetime import datetime, timedelta
import time, sys, wx, random

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.DynaPlot import DynaPlot, TIMER_ID
from Utils.Output import Output

class TimeStepper(wx.Timer):
    def __init__(self, cb):
        wx.Timer.__init__(self)
        self.cb = cb

    def Notify(self):
        self.cb()

class MainModel(object):
    def __init__(self, filename,log,run_type="HS"):
        self.Log = log
        self.filename = filename
        self.run_type = run_type

    def Initialize(self):
        self.Log("Initializing Model")
        self.Reach = HeatSourceInterface(self.filename,gauge=self.Log).Reach
        self.Log("Initialization Complete, %i stream nodes built"% len(self.Reach))
#        self.timer = TimeStepper(self.TimeStep)
        self.reachlist = sorted(self.Reach.itervalues(),reverse=True)

    def Reset(self):
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=IniParams["dt"])
        start = IniParams["date"]
        stop = start + timedelta(days=IniParams["simperiod"])
        spin = 0 # IniParams["FlushDays # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        ##########################################################
        dt_out = timedelta(minutes=60)
        self.Output = Output(dt_out, self.Reach, start)

    def Run(self):
#        self.Log("Starting")
        self.Reset()
        self.time1 = datetime.today()
        self.time = Chronos.TheTime
        self.stop = Chronos.stop
#        self.timer.Start(100)

#    def TimeStep(self):
        tm = self.time
#        try: #Wrap this in a try/except block to catch errors. Othewise, the model will continue running past them
        while self.time < Chronos.stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(self.time)
            if not tm.minute and not tm.second:  #TODO: Would this work if an hour is not divisable by our timestep?
                self.hydro_time = tm
                self.solar_time = tm
                for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                if self.solar_time < Chronos.start:
                    self.hydro_time = Chronos.start
                    self.solar_time += timedelta(days=Chronos.start.day-self.solar_time.day)
            elif tm.hour != self.solar_time.hour:
                raise NotImplementedError("Not divisible by timestep")

            if self.run_type=="HS":
                [x.CalcHydraulics(tm,self.hydro_time) for x in self.reachlist]
                [x.CalcHeat(tm.hour, tm.minute, tm.second,self.solar_time,JD,JDC,offset) for x in self.reachlist]
                [x.MacCormick2(self.solar_time) for x in self.reachlist]
            elif self.run_type=="SH":
                [x.CalcHeat(tm.hour, tm.minute, tm.second,self.solar_time,JD,JDC,offset) for x in self.reachlist]
            elif self.run_type=="HY":
                [x.CalcHydraulics(tm,self.hydro_time) for x in self.reachlist]
            else: raise Exception("Invalid run_type")

            self.Output.Store(tm)
            self.time = Chronos.Tick()
            print self.time
        return True
#        except:
#            self.Stop()
#            raise

    def Stop(self):
        self.timer.Stop()
