from __future__ import division

import cProfile, sys, time
from datetime import datetime, timedelta

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.TimeZones import Pacific
from Utils.Output import Output as O

sys.setcheckinterval(1000)
ErrLog = Logger
ErrLog.SetFile(sys.stdout) # Set the logger to the stdout

Reach = HeatSourceInterface("D:\\dan\\heatsource tests\\HS7_NUmpqua3_Toketee_CCC_test1.xls", ErrLog).Reach
ErrLog("Starting")
##########################################################
# Create a Chronos iterator that controls all model time
dt = timedelta(seconds=60)
start = datetime(2001, 7, 8, 00, 00,00, tzinfo=Pacific)
stop = start + timedelta(days=4)
spin = 0 # IniParams["FlushDays"] # Spin up period
# Other classes hold references to the instance, but only we should Start() it.
Chronos.Start(start, dt, stop, spin)
dt_out = timedelta(minutes=60)
Output = O(dt_out, Reach, start)
##########################################################

def hydraulics():
    time = Chronos.TheTime
    stop = Chronos.stop
    offset = Chronos.TZOffset(time)
    while time < stop:
        JD = Chronos.JDay
        JDC = Chronos.JDC
        if not time.minute or time.second:  #TODO: Would this work if an hour is not divisable by our timestep?
            hour = time
        reachlist = sorted(Reach.itervalues(),reverse=True)
        [x.CalcHydraulics(time, hour) for x in reachlist]
        [x.CalcHeat(time, hour,JD,JDC,offset) for x in reachlist]
        [x.MacCormick2(hour) for x in reachlist]
        Output.Store(time)
        for x in reachlist:
            self.T_prev = self.T
            self.T = None # This just ensures we don't accidentally use it until it's reset
        time = Chronos.Tick()


#hydraulics()
cProfile.run('hydraulics()')
ErrLog("Finished")
