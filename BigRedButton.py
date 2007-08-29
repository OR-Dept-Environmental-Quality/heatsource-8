from __future__ import division

import cProfile, sys, time, traceback, itertools
from os.path import join, exists
from datetime import datetime, timedelta
from win32com.client import Dispatch
from win32gui import PumpWaitingMessages

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties import Chronos
from Dieties import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O

from __version__ import version_info

class HSProfile(object):
    def __init__(self,worksheet,run_type=0):
        self.ErrLog = Logger
        self.ErrLog.SetFile(sys.stdout) # Set the logger to the stdout
        self.HS = HeatSourceInterface(join(worksheet), self.ErrLog, run_type)
        self.Reach = self.HS.Reach
        self.cur_hour = None
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=IniParams["dt"])
        start = IniParams["date"]
        if self.run_type==1:
            stop = start + timedelta(days=1)
        else:
            stop = start + timedelta(days=IniParams["simperiod"])
        spin = IniParams["flushdays"] # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        Chronos.dst = timedelta(hours=IniParams["daylightsavings"]) # adjust for daylight savings time
        dt_out = timedelta(minutes=60)
        self.Output = O(dt_out, self.Reach, start)
        ##########################################################

        self.reachlist = sorted(self.Reach.itervalues(),reverse=True)

    def trip(self, time):
        """Set tripline if we are at, or the first timestep after, the top of the hour"""
        if time.minute: # We are not the top of the hour
            if time.hour == self.cur_hour: # Same hour as last timestep
                return time
            else: # We've advanced an hour, reset
                self.cur_hour = time.hour
                return time
        else: # we've landed at the top of the hour, return
            return time
    def run(self): # Argument allows profiling and testing
        time1 = datetime.today()
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        flush = start-timedelta(days=IniParams["flushdays"])
        if (stop-start).seconds:
            timesteps = (stop-flush).seconds/Chronos.dt.seconds
        else:
            timesteps = ((stop-flush).days*86400)/Chronos.dt.seconds
        count = itertools.count()
        while time < stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(time)
            n = count.next()
            if not n%60: # every hour
                self.HS.PB("%i of %i timesteps"% (n,int(timesteps)))
                PumpWaitingMessages()
                if exists("c:\\quitHS"):
                    self.HS.PB("Simulation stopped by user")
                    return
                hydro_time = solar_time = self.trip(time)
                if not n%1440:
                    for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                if solar_time < start:
                    solar_time += timedelta(days=start.day-solar_time.day)
            print time

            if self.run_type==0:
                [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
                [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]
                [x.MacCormick2(solar_time) for x in self.reachlist]
            elif self.run_type==1:
                [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]
            elif self.run_type==2:
                [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
            else: raise Exception("Invalid run_type")

            self.Output(time)
            time = Chronos.Tick()
        total_time = (datetime.today()-time1).seconds
        total_days = total_time/(IniParams["simperiod"]+IniParams["flushdays"])
        message = "Finished in %i seconds (%0.3f seconds per timestep, %0.1f seconds per day)" %\
                    (total_time, total_time/timesteps, total_days)
        self.HS.PB(message)
        print message

class MyError(SystemExit):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "'%s'\nSee c:\HSError.txt for full error message." % self.value

def RunHS(sheet):
    try:
        HSP = HSProfile(sheet).run()
    except Exception:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        raise Exception("See error log: c:\\HSError.txt")
def RunSH(sheet):
    try:
        HSP = HSProfile(sheet,1).run()
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        sys.tracebacklimit = 1
        raise
def RunHY(sheet):
    try:
        HSP = HSProfile(sheet,2).run()
    except Exception:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        raise Exception("See error log: c:\\HSError.txt")

if __name__ == "__main__":
    #Profile()

    try:
        #HSP = HSProfile("C:\\Rogue\\Evans.xls",1)
        HSP = HSProfile("C:\\Python25\\HS8_Example_River.xls","HS")
        HSP.run()
        #cProfile.runctx('HSP.run()',globals(), locals())
    except Exception:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        sys.tracebacklimit = 1
        print sys.tracebacklimit
        raise
