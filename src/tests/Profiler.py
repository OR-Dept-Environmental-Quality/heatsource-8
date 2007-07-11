from __future__ import division

import cProfile, sys, time, traceback
from os.path import join
from datetime import datetime, timedelta
from win32com.client import Dispatch

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O

from __version__ import version_info

class HSProfile(object):
    def __init__(self,worksheet,run_type="HS"):
        self.ErrLog = Logger
        self.ErrLog.SetFile(sys.stdout) # Set the logger to the stdout
        self.HS = HeatSourceInterface(join(worksheet), self.ErrLog)
        self.Reach = self.HS.Reach
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=IniParams["dt"])
        start = IniParams["date"]
        if self.run_type=="SH":
            stop = start + timedelta(days=1)
        else:
            stop = start + timedelta(days=IniParams["simperiod"])
        spin = IniParams["flushdays"] # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        dt_out = timedelta(minutes=60)
        self.Output = O(dt_out, self.Reach, start)
        ##########################################################

        self.reachlist = sorted(self.Reach.itervalues(),reverse=True)

    def run(self): # Argument allows profiling and testing
        self.ErrLog("Starting..")
        time1 = datetime.today()
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        
        while time < stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(time)
            if not time.minute and not time.second:  #TODO: Would this work if an hour is not divisable by our timestep?
                hydro_time = time
                solar_time = time
                for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                if solar_time < start:
                    hydro_time = start
                    solar_time += timedelta(days=start.day-solar_time.day)
            elif time.hour != solar_time.hour:
                raise NotImplementedError("Not divisible by timestep")

            if self.run_type=="HS":
                [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
                [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]
                [x.MacCormick2(solar_time) for x in self.reachlist]
            elif self.run_type=="SH":
                [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]
            elif self.run_type=="HY":
                [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
            else: raise Exception("Invalid run_type")

            self.Output.Store(time)
            time = Chronos.Tick()
            #self.ErrLog.progress()
        self.ErrLog("Finished in %i seconds"% (datetime.today()-time1).seconds)

def RunHS(sheet): HSP = HSProfile(sheet).run()
def RunSH(sheet): HSP = HSProfile(sheet,"SH").run()
def RunHY(sheet): HSP = HSProfile(sheet,"HY").run()
def Profile():
    HSP = HSProfile("C:\eclipse\HeatSource\HS8_Example_River.xls","HS")
    HSP.run()
#    cProfile.run('HSP.run()')

if __name__ == "__main__":
    #Profile()
    HSP = HSProfile("C:\eclipse\HeatSource\HS8_Example_River.xls","HS")
    cProfile.runctx('HSP.run()',globals(), locals())
