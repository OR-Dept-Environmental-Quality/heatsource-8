from __future__ import division

from itertools import count
from traceback import print_exc, format_tb
from sys import exc_info
from os.path import join, exists
from os import unlink
from datetime import datetime, timedelta
from win32com.client import Dispatch
from win32gui import PumpWaitingMessages
from Utils.easygui import msgbox, buttonbox
from time import mktime

from Excel.HeatSourceInterface import HeatSourceInterface
from Dieties import Chronos
from Dieties import IniParams
from Utils.Logger import Logger
from Utils.Output import Output as O
from heatsource import HeatSourceError, CalcMacCormick

from __version__ import version_info

try:
    from psyco.classes import psyobj
    object = psyobj
except ImportError: pass

class HSProfile(object):
    def __init__(self,worksheet,run_type=0):
        self.ErrLog = Logger
        self.HS = HeatSourceInterface(join(worksheet), self.ErrLog, run_type)
        self.reachlist = sorted(self.HS.Reach.itervalues(),reverse=True)
        self.cur_hour = None
        self.run_type = run_type # can be "HS", "SH", or "HY" for Heatsource, Shadalator, or Hydraulics, resp.
        if run_type == 0: self.run_all = self.run_hs
        elif run_type == 1: self.run_all = self.run_sh
        elif run_type == 2: self.run_all = self.run_hy
        else: raise Exception("Bad run_type: %i" %`run_type`)
        self.interp = IniParams["interp"]
        ##########################################################
        # Create a Chronos iterator that controls all model time
        dt = timedelta(seconds=IniParams["dt"])
        start = IniParams["modelstart"]
        if self.run_type==1:
            stop = start + timedelta(days=1)
        else:
            stop = start + timedelta(days=IniParams["simperiod"])
        spin = IniParams["flushdays"] # Spin up period
        # Other classes hold references to the instance, but only we should Start() it.
        Chronos.Start(start, dt, stop, spin)
        Chronos.dst = timedelta(hours=IniParams["daylightsavings"]) # adjust for daylight savings time
        dt_out = timedelta(minutes=60)
        self.Output = O(dt_out, self.HS.Reach, start)
        ##########################################################
        self.testfile = open("E:\\solar_new.txt","w")
    def close(self):
        print "Deleting HSProfile"
#        self.HS.close()
#        del self.reachlist, self.run_all, self.Reach, self.HS, #self.Output
    def run_hs(self,time,hydro_time, solar_time, JD, JDC, offset):
        HMS = time.hour, time.minute, time.second
        [x.CalcDischarge(time,hydro_time) for x in self.reachlist]
        [x.CalcHeat(time, HMS, solar_time,JD,JDC,offset) for x in self.reachlist]
        [x.MacCormick2(solar_time) for x in self.reachlist]
    def run_hy(self,time,hydro_time, solar_time, JD, JDC, offset):
        [x.CalcDischarge(time,hydro_time) for x in self.reachlist]
    def run_sh(self,time,hydro_time, solar_time, JD, JDC, offset):
        HMS = time.hour, time.minute, time.second
        [x.CalcHeat(time, HMS, solar_time,JD,JDC,offset) for x in self.reachlist]
    def run(self): # Argument allows profiling and testing
        time = Chronos.TheTime
        stop = Chronos.stop
        start = Chronos.start
        flush = start-timedelta(days=IniParams["flushdays"])
        # Number of timesteps is based on the division of the timesteps into the hour. In other words
        # 1 day with a 1 minute dt is 1440 timesteps, while a 3 minute dt is only 480 timesteps. Thus,
        # We define the timesteps by dividing dt (now in seconds) by 3600
        timesteps = int(((stop-flush).days*24*(3600/IniParams["dt"])))#/Chronos.dt.seconds
        cnt = count()
        out = 0
        time1 = datetime.today()
        while time < stop:
            JD = Chronos.JDay
            JDC = Chronos.JDC
            offset = Chronos.TZOffset(time)
            if not (time.minute + time.second): # every hour
                ts = cnt.next() # Number of actual timesteps per tick
                hr = 60/(IniParams["dt"]/60) # Number of timesteps in one hour
                self.HS.PB("%i of %i timesteps"% (ts*hr,timesteps))
                PumpWaitingMessages()
                if not time.hour:
                    for nd in self.reachlist: nd.F_DailySum = [0]*5 # Reset values for new day
                hydro_time = solar_time = mktime(time.timetuple())
                # If we're not interpolating the values, set the time to the top of the hour
                # This is done by subtracting the remainder of the time when we divide by
                # one hour's worth of seconds
                if self.interp: hydro_time = solar_time = hydro_time-(hydro_time%3600)
                if time < start:
                    solar_time = mktime((time + timedelta(days=start.day-solar_time.day)).timetuple())
                    if self.interp: solar_time = solar_time - (solar_time%3600)
                # Check to see if the user pressed the stop button. Pretty crappy kludge here- VB code writing an
                # empty file- but I basically got to lazy to figure out how to interact with the underlying
                # COM API without using a threading interface.
                if exists("c:\\quit_heatsource"):
                    unlink("c:\\quit_heatsource")
                    QuitMessage()
            try:
                self.run_all(time,hydro_time, solar_time, JD, JDC, offset)
            except HeatSourceError, (stderr):
                msg = "At %s and time %s\n"%(self,Chronos.TheTime.isoformat(" ") )
                try:
                    msg += stderr+"\nThe model run has been halted. You may ignore any further error messages."
                except TypeError:
                    msg += `stderr`+"\nThe model run has been halted. You may ignore any further error messages."
                msgbox(msg)
                raise SystemExit

            out += self.reachlist[-1].Q
            self.Output(time)
            time = Chronos.Tick()

        self.Output.flush()
        total_time = (datetime.today()-time1).seconds/60
        total_days = total_time/(IniParams["simperiod"]+IniParams["flushdays"])
        balances = [x.Q_mass for x in self.reachlist]
        total_inflow = sum(balances)
        mettaseconds = (total_time/timesteps/len(self.reachlist))*1e6
        message = "Finished in %i minutes (%0.3f microseconds each cycle). Water Balance: %0.3f/%0.3f" %\
                    (total_time, mettaseconds, total_inflow, out)
        self.HS.PB(message)
        self.testfile.close()
        print message

def QuitMessage():
        mess =(("Do you really want to quit Heat Source", "Quit Heat Source",
                ["Cancel", "Yes, quit"]),
               ("Heatsource was developed for real men, not wimps.\nReal men don't quit.\n\nDo you seriously want to quit?", "Environmental Modeling Faux Pas",
                ["Naw, you're right", "Seriously, quit"]),
               ("Dude! You realize that I'm going to call you names and fuck with you for the rest of the day if you do this.\n\nI mean seriously, I won't be responsible for the names people will call you in the hallways!\n\nDo you seriously want to go through with this?","Are you really going to be a quitter!?",
                ["Wow, thanks! Keep going","Man, shut up and quit already!"]),
               ("Alright, I'm quitting.\n\nLook, man, don't come bitch to me when people snub you at cocktail parties!\n\nYou're the one who flip-flopped on this one!\n\n\n(A Harvard man wouldn't have quit.)","Confirmed: You are a wimp.",
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
        f = open("c:\\HSError.txt","w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)
def RunSH(sheet):
    try:
        HSP = HSProfile(sheet,1)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)
def RunHY(sheet):
    try:
        HSP = HSProfile(sheet,2)
        HSP.run()
    except Exception, stderr:
        f = open("c:\\HSError.txt","w")
        print_exc(file=f)
        f.close()
        msgbox("".join(format_tb(exc_info()[2]))+"\nSynopsis: %s"%stderr,"HeatSource Error",err=True)