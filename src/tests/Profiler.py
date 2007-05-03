from __future__ import division

import cProfile, sys, time
from datetime import datetime, timedelta

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.TimeZones import Pacific

ErrLog = Logger
ErrLog.SetFile(sys.stdout) # Set the logger to the stdout

#try:
#    import psyco
#    psyco.full()
#except:
#    pass

Reach = HeatSourceInterface("D:\\dan\\heatsource tests\\HS7_NUmpqua3_Toketee_CCC.xls", ErrLog).Reach
ErrLog("Starting")
##########################################################
# Create a Chronos iterator that controls all model time
dt = timedelta(seconds=60)
start = datetime(2007, 4, 27, 00, 00,00, tzinfo=Pacific)
stop = start + timedelta(days=4)
spin = 0 # IniParams.FlushDays # Spin up period
# Other classes hold references to the instance, but only we should Start() it.
Chronos.Start(start-dt, dt, stop, spin)
##########################################################

def hydraulics():
    while Chronos.TheTime < Chronos.stop:
        [x.CalcHydraulics() for x in Reach]
        [x.CalcHeat() for x in Reach]
        [x.MacCormick2() for x in Reach]
        Chronos.Tick()


hydraulics()
#cProfile.run('hydraulics()')
ErrLog("Finished")
