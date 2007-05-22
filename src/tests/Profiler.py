from __future__ import division

import cProfile, sys, time
from os.path import join
from datetime import datetime, timedelta
import threading as _T

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.TimeZones import Pacific
from Utils.Output import Output as O

ErrLog = Logger
ErrLog.SetFile(sys.stdout) # Set the logger to the stdout
debugfile = join(IniParams["datadirectory"],IniParams["debugfile"])
Reach = HeatSourceInterface(debugfile, ErrLog).Reach
time1 = datetime.today()
##########################################################
# Create a Chronos iterator that controls all model time
dt = timedelta(seconds=60)
start = datetime(2001, 7, 8, 00, 00,00, tzinfo=Pacific)
stop = start + timedelta(days=4)
spin = 0 # IniParams["flushdays"] # Spin up period
# Other classes hold references to the instance, but only we should Start() it.
Chronos.Start(start, dt, stop, spin)
dt_out = timedelta(minutes=60)
Output = O(dt_out, Reach, start)
##########################################################

reachlist = sorted(Reach.itervalues(),reverse=True)
def hydro(t,h): [x.CalcHydraulics(t,h) for x in reachlist]
def solar(t,h,j,c,o): [x.CalcHeat(t,h,j,c,o) for x in reachlist]

def run_threaded_time():
    time = Chronos.TheTime
    stop = Chronos.stop
    dt = Chronos.dt
    for time in Chronos:
        pass

def run_threaded_space(RunThreaded=0): # Argument allows profiling and testing
    time = Chronos.TheTime
    stop = Chronos.stop
    while time < stop:
        JD = Chronos.JDay
        JDC = Chronos.JDC
        offset = Chronos.TZOffset(time)
        if not time.minute or time.second:  #TODO: Would this work if an hour is not divisable by our timestep?
            hour = time
        elif time.hour != hour.hour:
            raise NotImplementedError("Not divisible by timestep")
        if RunThreaded:
            H = _T.Thread(target=hydro, name="hydro %s"%time, args=(time, hour))
            S = _T.Thread(target=solar, name="solar %s"%time, args=(time,hour,JD,JDC,offset))
            H.setDaemon(True)
            S.setDaemon(True)
            H.start()
            S.start()
            H.join()
            S.join()
        else:
            hydro(time,hour)
            solar(time,hour,JD,JDC,offset)
        [x.MacCormick2(hour) for x in reachlist]
#        Output.Store(time)
        for x in reachlist:
            x.T_prev = x.T
            x.T = None # This just ensures we don't accidentally use it until it's reset
        time = Chronos.Tick()

#run_threaded_space(1)
cProfile.run('run_threaded_space()')
ErrLog("Finished in %i seconds"% (datetime.today()-time1).seconds)
