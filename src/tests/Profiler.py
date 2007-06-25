from __future__ import division

import cProfile, sys, time
from os.path import join
from datetime import datetime, timedelta

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O

from __version__ import version_info

class Profile(object):
    def __init__(self,sheet):
        self.ErrLog = Logger
        self.ErrLog.SetFile(sys.stdout) # Set the logger to the stdout
        debugfile = join(sheet)
        self.Reach = HeatSourceInterface(debugfile, self.ErrLog).Reach
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=60)
        start = IniParams["date"]
        stop = start + timedelta(days=IniParams["simperiod"])
        spin = IniParams["flushdays"] # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        dt_out = timedelta(minutes=60)
        self.Output = O(dt_out, self.Reach, start)
        ##########################################################

        self.reachlist = sorted(self.Reach.itervalues(),reverse=True)

    def run(self): # Argument allows profiling and testing
        time1 = datetime.today()
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        while time < stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(time)
            if not time.minute or time.second:  #TODO: Would this work if an hour is not divisable by our timestep?
                hydro_time = time
                solar_time = time
                for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                if solar_time < start:
                    hydro_time = start
                    solar_time += timedelta(days=start.day-solar_time.day)
            elif time.hour != solar_time.hour:
                raise NotImplementedError("Not divisible by timestep")


            [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
            [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]

            [x.MacCormick2(solar_time) for x in self.reachlist]
            self.Output.Store(time)
            for x in self.reachlist:
                x.T_prev = x.T
                x.T = None # This just ensures we don't accidentally use it until it's reset
            time = Chronos.Tick()
        self.ErrLog("Finished in %i seconds"% (datetime.today()-time1).seconds)
def Run(sheetname):
    P = Profile(sheetname)
    P.run()
#    cProfile.run('P.run()')

if __name__ == "__main__":
    Run("C:\eclipse\HeatSource\HS8_Example_River.xls")