from __future__ import division

import gc
import cProfile, sys, time, traceback, itertools, weakref
from os.path import join, exists
from datetime import datetime, timedelta
from win32com.client import Dispatch
from win32gui import PumpWaitingMessages
from Utils.easygui import msgbox

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties import Chronos
from Dieties import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O
from heatsource import HeatSourceError, CalcMacCormick

from __version__ import version_info

#force_quit = False

class HSProfile(object):
    def __init__(self,worksheet,run_type=0):
        self.ErrLog = Logger
        self.HS = HeatSourceInterface(join(worksheet), self.ErrLog, run_type)
        gc.enable()
        gc.set_debug(gc.DEBUG_LEAK)
        gc.collect()
        self.Reach = self.HS.Reach
        self.cur_hour = None
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.
        if run_type == 0: self.run_all = self.run_hs
        elif run_type == 1: self.run_all = self.run_sh
        elif run_type == 2: self.run_all = self.run_hy
        else: raise Exception("Bad run_type: %i" %`run_type`)
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
        #self.Output = O(dt_out, self.Reach, start)
        ##########################################################

        self.reachlist = sorted(self.Reach.itervalues(),reverse=True)
    def close(self):
        print "Deleting HSProfile"
        self.HS.close()
        del self.reachlist, self.run_all, self.Reach, self.HS, #self.Output
    def run_hs(self,time,hydro_time, solar_time, JD, JDC, offset):
        for node in self.reachlist:
            node.CalcHydraulics(time,hydro_time)
            node.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset)
        for node in self.reachlist[1:]:
            node.T, junk = CalcMacCormick(node.dt, node.dx, node.U, node.T_sed, node.T_prev, node.Q_hyp,
                            node.Q_tribs[solar_time], node.T_tribs[solar_time], node.prev_km.Q, node.Delta_T, node.Disp,
                            True, node.S1, node.prev_km.T, node.T, node.next_km.T, node.Q_in, node.T_in)
    def run_hy(self,time,hydro_time, solar_time, JD, JDC, offset):
        [x.CalcHydraulics(time,hydro_time) for x in self.reachlist]
    def run_sh(self,time,hydro_time, solar_time, JD, JDC, offset):
        [x.CalcHeat(time.hour, time.minute, time.second,solar_time,JD,JDC,offset) for x in self.reachlist]
    def run(self): # Argument allows profiling and testing
        global force_quit
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        flush = start-timedelta(days=IniParams["flushdays"])
        if (stop-start).seconds:
            timesteps = (stop-flush).seconds/Chronos.dt.seconds
        else:
            timesteps = ((stop-flush).days*86400)/Chronos.dt.seconds
        count = itertools.count()
        out = 0
        time1 = datetime.today()
        while time < stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(time)
            n = count.next()
            if not n%60: # every hour
                self.HS.PB("%i of %i timesteps"% (n,int(timesteps)))
                PumpWaitingMessages()
#                if force_quit:
#                    self.HS.PB("Simulation stopped by user")
#                    break
                if not n%1440:
                    for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                hydro_time = solar_time = time.isoformat(" ")[:-12]+":00:00" # Reformat time to "YYYY-MM-DD HH:00:00"
                if time < start:
                    solar_time = (time + timedelta(days=start.day-solar_time.day)).isoformat(" ")[:-12]+":00:00"
            try:
                self.run_all(time,hydro_time, solar_time, JD, JDC, offset)
            except HeatSourceError, (stderr):
                msg = "At %s and time %s\n"%(self,Chronos.TheTime.isoformat(" ") )
                msg += stderr+"\nThe model run has been halted. You may ignore any further error messages."
                msgbox(msg)
                raise SystemExit

            out += self.reachlist[-1].Q
            #self.Output(time)
            time = Chronos.Tick()

        #self.Output.flush()
        total_time = (datetime.today()-time1).seconds
        total_days = total_time/(IniParams["simperiod"]+IniParams["flushdays"])
        balances = [x.Q_mb for x in self.reachlist]
        total_inflow = sum(balances)
        message = "Finished in %i seconds (%0.3f seconds per timestep, %0.1f seconds per day). Water Balance: %0.3f/%0.3f" %\
                    (total_time, total_time/timesteps, total_days, total_inflow, out)
        self.HS.PB(message)

def RunHS(sheet):
    try:
        HSP = HSProfile(sheet)
        HSP.run()
        del HSP
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        msgbox("".join(traceback.format_tb(sys.exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)
def RunSH(sheet):
    try:
        HSP = HSProfile(sheet,1)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        msgbox("".join(traceback.format_tb(sys.exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)
def RunHY(sheet):
    try:
        HSP = HSProfile(sheet,2)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        traceback.print_exc(file=f)
        f.close()
        msgbox("".join(traceback.format_tb(sys.exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)

def quit(arg):
    global force_quit
    if arg:
        force_quit = True
    else:
        force_quit = False