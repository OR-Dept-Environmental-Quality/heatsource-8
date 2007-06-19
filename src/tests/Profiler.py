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

ErrLog = Logger
ErrLog.SetFile(sys.stdout) # Set the logger to the stdout
debugfile = join("C:\eclipse\HeatSource\HS8_Example_River.xls")
Reach = HeatSourceInterface(debugfile, ErrLog).Reach
time1 = datetime.today()
##########################################################
# Create a Chronos iterator that controls all model time
dt = timedelta(seconds=60)
start = IniParams["date"]
stop = start + timedelta(days=4)
spin = 0 #IniParams["flushdays"] # Spin up period
# Other classes hold references to the instance, but only we should Start() it.
Chronos.Start(start, dt, stop, spin)
dt_out = timedelta(minutes=60)
#Output = O(dt_out, Reach, start)
##########################################################

reachlist = sorted(Reach.itervalues(),reverse=True)
def hydro(t,h): [x.CalcHydraulics(t,h) for x in reachlist]
def solar(h,m,s,sh,j,c,o): [x.CalcHeat(h,m,s,sh,j,c,o) for x in reachlist]

def run(): # Argument allows profiling and testing
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
            if solar_time < start:
                hydro_time = start
                solar_time += timedelta(days=start.day-solar_time.day)
        elif time.hour != solar_time.hour:
            raise NotImplementedError("Not divisible by timestep")

        hydro(time,hydro_time)
        solar(time.hour, time.minute, time.second,solar_time,JD,JDC,offset)
#        [x.MacCormick2(solar_hour) for x in reachlist]
#        Output.Store(time)
        for x in reachlist:
            x.T_prev = x.T
            x.T = None # This just ensures we don't accidentally use it until it's reset
        time = Chronos.Tick()
#run()
cProfile.run('run()')
ErrLog("Finished in %i seconds"% (datetime.today()-time1).seconds)
