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
from heatsource import HeatSourceError, CalcMacCormick

from __version__ import version_info

try:
    from __debug__ import psyco_optimize
    if psyco_optimize:
        from psyco.classes import psyobj
        object = psyobj
except ImportError: pass

class ModelControl(object):
    def __init__(self, worksheet, run_type=0):
        self.ErrLog = Logger
        self.worksheet = join(worksheet)
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.

    def PrintReach(self):
        with open("c:\\Reach.txt", "w") as f:
            for node in self.HS.Reach.itervalues():
                f.write("%s\n" % node)
                for attr, val in node.GetNodeData().iteritems():
                    if attr in ["C_args", "FLIR_Time", "FLIR_Temp", "Log"]: continue
                    try:
                        f.write("\t%s: %s\n" % (attr, `val`))
                    except TypeError:
                        f.write("\t%s\n" % (attr, [`i` for i in attr]))
        raise Exception("DONE")

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
        Chronos.Start(start, dt, stop, spin, IniParams["offset"], IniParams["daylightsavings"])
        Chronos.dst = IniParams["daylightsavings"] # adjust for daylight savings time
        self.Output = O(60, self.HS.Reach, start)
        ##########################################################
        self.testfile = open("E:\\solar_new.txt", "w")

    ###############################################################
    def run(self): # Argument allows profiling and testing
        self.Initialize()
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
                self.run_all(time, hour, minute, second, JD, JDC, offset)
            except HeatSourceError, (stderr):
                msg = "At %s and time %s\n"%(self, Chronos.PrettyTime())
                try:
                    msg += stderr+"\nThe model run has been halted. You may ignore any further error messages."
                except TypeError:
                    msg += `stderr`+"\nThe model run has been halted. You may ignore any further error messages."
                msgbox(msg)
                raise SystemExit

            out += self.reachlist[-1].Q
            self.Output()
            time = Chronos(True)

        self.Output.flush()
        total_time = (Time() - time1) /60
        total_days = total_time/(IniParams["simperiod"]+IniParams["flushdays"])
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
    def run_hs(self, time, H, M, S, JD, JDC, offset):
        [x.CalcDischarge(time) for x in self.reachlist]
        [x.CalcHeat(time, H, M, S, JD, JDC, offset) for x in self.reachlist]
        [x.MacCormick2(time) for x in self.reachlist]

    def run_hy(self, time, H, M, S, JD, JDC, offset):
        [x.CalcDischarge(time) for x in self.reachlist]

    def run_sh(self, time, H, M, S, JD, JDC, offset):
        [x.CalcHeat(time, H, M, S, JD, JDC, offset) for x in self.reachlist]


def QuitMessage():
        mess =(("Do you really want to quit Heat Source", "Quit Heat Source",
                ["Cancel", "Yes, quit"]),
               ("Heatsource was developed for real men, not wimps.\nReal men don't quit.\n\nDo you seriously want to quit?", "Environmental Modeling Faux Pas",
                ["Naw, you're right", "Seriously, quit"]),
               ("Dude! You realize that I'm going to call you names and fuck with you for the rest of the day if you do this.\n\nI mean seriously, I won't be responsible for the names people will call you in the hallways!\n\nDo you seriously want to go through with this?", "Are you really going to be a quitter!?",
                ["Wow, thanks! Keep going", "Man, shut up and quit already!"]),
               ("Alright, I'm quitting.\n\nLook, man, don't come bitch to me when people snub you at cocktail parties!\n\nYou're the one who flip-flopped on this one!\n\n\n(A Harvard man wouldn't have quit.)", "Confirmed: You are a wimp.",
                ["Wimps, press here."]))

        for i in xrange(len(mess)):
            m = mess[i]
            b = buttonbox(m[0], m[1], m[2])
            if b == m[2][-1]:
                if i < 3: continue
                else: raise Exception("Model stopped by a wimpy, flip-flopping quitter (Probably a Democrat).")
            else: return


def RunHS(sheet):
    try:
        HSP = HSProfile(sheet)
        HSP.run()
        del HSP
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)
def RunSH(sheet):
    try:
        HSP = HSProfile(sheet, 1)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)
def RunHY(sheet):
    try:
        HSP = HSProfile(sheet, 2)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt", "w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr, "HeatSource Error", err=True)

