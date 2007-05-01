from __future__ import division

import cProfile, sys
from datetime import datetime, timedelta

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from Utils.Logger import Logger
from Utils.TimeZones import Pacific

ErrLog = Logger.getInstance()
ErrLog.SetFile(sys.stdout) # Set the logger to the stdout

#try:
#    import psyco
#    psyco.log()
#    psyco.profile()
#except:
#    pass

Reach = HeatSourceInterface('C:\\eclipse\\HeatSource\\Toketee_CCC.xls', ErrLog).Reach
##########################################################
# Create a Chronos iterator that controls all model time
dt = timedelta(seconds=60)
start = datetime(2007, 4, 27, 00, 00,00, tzinfo=Pacific)
stop = start + timedelta(days=3)
spin = 0 # IniParams.FlushDays # Spin up period
# Other classes hold references to the instance, but only we should Start() it.
Chronos.Start(start-dt, dt, stop, spin)
##########################################################

def hydraulics():
    while Chronos.TheTime < Chronos.stop:
        [x.CalcHydraulics() for x in Reach]
        [x.CalcHeat() for x in Reach]
        Chronos.Tick()

def heat():
    [x.CalcHeat() for x in Reach]

def finish():
    l = [x.MacCormick1() for x in Reach]
    for i in xrange(len(l)):
        Reach[i].MacCormick2(l[i])


#hydraulics()
#Chronos.Tick()
cProfile.run('hydraulics()')
##cProfile.run('finish')