from __future__ import with_statement, division
#from __future__ import with_statement # On separate line to satisfy PyDev bug

from itertools import count
from traceback import print_exc, format_tb
from sys import exc_info
from os.path import join, exists
from os import unlink
from win32com.client import Dispatch
from win32gui import PumpWaitingMessages
from Utils.easygui import msgbox, buttonbox
from time import time as Time

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties import Chronos
from Dieties import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O
from heatsource.HSmodule import HeatSourceError, CalcMacCormick

from __version__ import version_info
from __debug__ import psyco_optimize

try:
    if psyco_optimize:
        from psyco.classes import psyobj
        object = psyobj
except ImportError: pass

class ModelControl(object):
    def __init__(self, worksheet, run_type=0):
        self.ErrLog = Logger
        self.worksheet = join(worksheet)
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.
        if not psyco_optimize: self.Initialize()
        
    def Initialize(self):
        """Set up the model.

        This is not in __init__() because of psyco and to faciliate the
        ability to run concurrent models or store the ModelControl class
        for Monte Carlo runs if we want to do that later."""
        self.HS = HeatSourceInterface(self.worksheet, self.ErrLog, self.run_type)
        self.reachlist = sorted(self.HS.Reach.itervalues(), reverse=True)
        self.cur_hour = None
        if self.run_type == 0: self.run_all = self.run_hs
        elif self.run_type == 1: self.run_all = self.run_sh
        elif self.run_type == 2: self.run_all = self.run_hy
        else: raise Exception("Bad run_type: %i" %`self.run_type`)
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = IniParams["dt"]
        start = IniParams["modelstart"]
        stop = IniParams["modelend"]
        spin = IniParams["flushdays"] # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin, IniParams["offset"])
        self.Output = O(60, self.HS.Reach, start)
        ##########################################################
        self.testfile = open("E:\\solar_new.txt", "w")

    ###############################################################
    def run(self): # Argument allows profiling and testing
        if psyco_optimize: self.Initialize()
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        flush = start-(IniParams["flushdays"]*86400)
        # Number of timesteps is based on the division of the timesteps into the hour. In other words
        # 1 day with a 1 minute dt is 1440 timesteps, while a 3 minute dt is only 480 timesteps. Thus,
        # We define the timesteps by dividing dt (now in seconds) by 3600
        timesteps = (stop-flush)/IniParams["dt"]
        cnt = count()
        out = 0
        time1 = Time()
        while time < stop:
            JD, JDC = Chronos.JD
            year, month, day, hour, minute, second, weekday, jday, offset = Chronos.TimeTuple()
            if not (minute + second): # every hour
                ts = cnt.next() # Number of actual timesteps per tick
                hr = 60/(IniParams["dt"]/60) # Number of timesteps in one hour
                self.HS.PB("%i of %i timesteps"% (ts*hr, timesteps))
                # Update the Excel status bar
                PumpWaitingMessages()
                # Reset the flux daily sum for a new day
                if not hour:
                    for nd in self.reachlist: nd.F_DailySum = [0]*5
                # Check to see if the user pressed the stop button. Pretty crappy kludge here- VB code writing an
                # empty file- but I basically got to lazy to figure out how to interact with the underlying
                # COM API without using a threading interface.
                if exists("c:\\quit_heatsource"):
                    unlink("c:\\quit_heatsource")
                    QuitMessage()
            try:
                self.run_all(time, hour, minute, second, JD, JDC)
            except HeatSourceError, (stderr):
                msg = "At %s and time %s\n"%(self, Chronos.PrettyTime())
                try:
                    msg += stderr+"\nThe model run has been halted. You may ignore any further error messages."
                except TypeError:
                    msg += `stderr`+"\nThe model run has been halted. You may ignore any further error messages."
                msgbox(msg)
                raise SystemExit

            out += self.reachlist[-1].Q
            self.Output.call()
            time = Chronos(True)

        self.Output.close()
        total_time = (Time() - time1) /60
        simperiod = (IniParams["modelend"] - IniParams["modelstart"])/86400
        total_days = total_time/(simperiod+IniParams["flushdays"])
        balances = [x.Q_mass for x in self.reachlist]
        total_inflow = sum(balances)
        mettaseconds = (total_time/timesteps/len(self.reachlist))*1e6
        message = "Finished in %i minutes (%0.3f microseconds each cycle). Water Balance: %0.3f/%0.3f" %\
                    (total_time, mettaseconds, total_inflow, out)
        self.HS.PB(message)
        self.testfile.close()
        print message
    #############################################################
    ## three different versions of the run() routine, depending on the run_type
    def run_hs(self, time, H, M, S, JD, JDC):
        [x.CalcDischarge(time) for x in self.reachlist]
        [x.CalcHeat(time, H, M, S, JD, JDC) for x in self.reachlist]
        [x.MacCormick2(time) for x in self.reachlist]

    def run_hy(self, time, H, M, S, JD, JDC):
        [x.CalcDischarge(time) for x in self.reachlist]

    def run_sh(self, time, H, M, S, JD, JDC):
        [x.CalcHeat(time, H, M, S, JD, JDC) for x in self.reachlist]


def QuitMessage():
        b = buttonbox("Do you really want to quit Heat Source", "Quit Heat Source", ["Cancel", "Quit"])
        if b == "Quit":
            raise Exception("Model stopped user.")
        else: return


def RunHS(sheet):
    try:
        HSP = ModelControl(sheet)
        HSP.run()
        del HSP
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)
def RunSH(sheet):
    try:
        HSP = ModelControl(sheet, 1)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)
def RunHY(sheet):
    try:
        HSP = ModelControl(sheet, 2)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)

