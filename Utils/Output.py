from __future__ import division
from datetime import datetime, timedelta
from ..Dieties import IniParams
from ..Dieties import Chronos
from time import localtime
from os.path import join, exists
from os import makedirs

try:
    from ..__debug__ import psyco_optimize
    if psyco_optimize:
        from psyco.classes import psyobj
        object = psyobj
except ImportError: pass

class Output(object):
    def __init__(self, dt_out, reach, write_time):
        self.dt_out = dt_out
        self.reach = reach
        self.write_time = write_time
        self.nodes = sorted(self.reach.itervalues(),reverse=True)
        #In the dictionary below the value is a list, the first item will contain file information and the second
        #item is a love note.  Still need to put in date created.
        self.files = {
                        "Heat_Cond.txt": [None, "Streambed Conduction Flux (w/sq m)"],
                        "Heat_Conv.txt": [None, "Convection Flux (w/sq m)"],
                        "Heat_Evap.txt": [None, "Evaporation Flux (w/sq m)"],
                        "Heat_SR1.txt": [None, "Potential Solar Radiation Flux (w/sq m)"],
                        "Heat_SR4.txt": [None, "Surface Solar Radiation Flux (w/sq m)"],
                        "Heat_SR6.txt": [None, "Received Solar Radiation Flux (w/sq m)"],
                        "Heat_TR.txt": [None, "Thermal Radiation Flux (w/sq m)"],
                        "Hyd_DA.txt": [None, "Ave Depth (m)"],
                        "Hyd_DM.txt": [None, "Max Depth (m)"],
                        "Hyd_Flow.txt": [None, "Flow Rate (cms)"],
                        "Hyd_Hyp.txt": [None, "Hyporheic Exchange (cms)"],
                        "Hyd_Vel.txt": [None, "Flow Velocity (m/s)"],
                        "Hyd_WT.txt": [None, "Top Width (m)"],
                        "Rate_Evap.txt": [None, "Evaporation Rate (mm/hr)"],
                        "Shade.txt": [None, "Effective Shade"],
                        "Temp_H20.txt": [None, "Stream Temperature (*C)"],
                        "Temp_Sed.txt": [None, "Sediment Temperature (*C)"],
                        "VTS.txt": [None, "View to Sky"],
                        "Hyd_Disp.txt": [None, "Hydraulic Dispersion (m2/s)"]
                    }

        for key in self.files.iterkeys():
            if not exists(join(IniParams["outputdir"])):
                makedirs(join(IniParams["outputdir"]))
            self.files[key][0] = open(join(IniParams["outputdir"], key), 'w')
            self.files[key][0].write("Heat Source Hourly Output File:  ")
            self.files[key][0].write(self.files[key][1])
            today = localtime()
            self.files[key][0].write("     File created on %s/%s/%s" % (today[1], today[2], today[0]))
            self.files[key][0].write("\n\n")
            self.files[key][0].write("Datetime".ljust(14))
            for node in sorted(self.reach.iterkeys(),reverse=True):
                aaa = "%0.3f" % node
                self.files[key][0].write(aaa.ljust(14))
            self.files[key][0].write("\n")

    def close(self): [f.close() for f in self.files.itervalues()]

    def __call__(self):
        TheTime = Chronos()
        year, month, day, hour, minute, second, wk,jd,offset = Chronos.TimeTuple()
        if (TheTime < self.write_time) or (Chronos() < Chronos.start): return
        for node in self.nodes:
            try:
                test =  node.E / node.dx / node.W_w * 3600 * 1000,  #TODO: Check
            except:
                test = 9999
            variables = {
                "Heat_Cond.txt": node.F_Conduction,
                "Heat_Conv.txt": node.F_Convection,
                "Heat_Evap.txt": node.F_Evaporation,
                "Heat_SR1.txt": node.F_Solar[1],
                "Heat_SR4.txt": node.F_Solar[4],
                "Heat_SR6.txt": node.F_Solar[6],
                "Heat_TR.txt": node.F_Longwave,
                "Hyd_DA.txt": node.A / node.W_w,
                "Hyd_DM.txt": node.d_w,
                "Hyd_Flow.txt": node.Q,
                "Hyd_Hyp.txt": node.Q_hyp,
                "Hyd_Vel.txt": node.U,
                "Hyd_WT.txt": node.W_w,
                "Rate_Evap.txt": test, #TODO: Check
                "Temp_H20.txt": node.T,
                "Temp_Sed.txt": node.T_sed,
                "Hyd_Disp.txt": node.Disp
            }
            self.append(TheTime, variables, node)
        self.write_time += self.dt_out
        # Is the hour greater than the write_time's hour
        if hour > localtime(self.write_time)[3]:  #new day, print daily outputs
            for node in self.nodes:
                # TODO: What are we trying to accomplish here?
                try:
                    shade = (node.F_DailySum[1] - node.F_DailySum[4]) / node.F_DailySum[1]
                except ZeroDivisionError:
                    shade = node.F_DailySum[4]
                variables = {
                    "Shade.txt": shade,
                    "VTS.txt": node.ViewToSky
                }
                self.append(TheTime, variables, node)

    def append(self, TheTime, variables, node):
        for key in variables.iterkeys():
            if not node.prev_km: # upstream most node has no previous kilometer
                Excel_time = "%0.6f" % Chronos.ExcelTime()
                self.files[key][0].write(Excel_time.ljust(14))
            try:
                dataf = "%0.4f" % variables[key]
            except:
                print variables[key], type(variables[key]), key
                raise
            self.files[key][0].write(dataf.ljust(14))
            if not node.km: # Mouth node is km=0.0 or, another way, km=False
                self.files[key][0].write("\n")
