from __future__ import division
from datetime import datetime, timedelta
import time
from Dieties.IniParams import IniParams
from os import path
import os


class Output(object):
    def __init__(self, dt_out, reach, write_time):
        self.dt_out = dt_out
        self.reach = reach
        self.write_time = write_time
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
                        "Hyd_Froude.txt": [None, "Densiometric Froude"],
                        "Hyd_Hyp.txt": [None, "Hyporheic Exchange (cms)"],
                        "Hyd_Vel.txt": [None, "Flow Velocity (m/s)"],
                        "Hyd_WT.txt": [None, "Top Width (m)"],
                        "Rate_Evap.txt": [None, "Evaporation Rate (mm/hr)"],
                        "Shade.txt": [None, "Effective Shade"],
                        "Temp_H20.txt": [None, "Stream Temperature (*C)"],
                        "Temp_Sed.txt": [None, "Sediment Temperature (*C)"],
                        "VTS.txt": [None, "View to Sky"]
                    }

        for key in self.files.iterkeys():
            if not os.path.exists(path.join(IniParams["outputdir"])):
                os.makedirs(path.join(IniParams["outputdir"]))
            self.files[key][0] = open(path.join(IniParams["outputdir"], key), 'w')
            self.files[key][0].write("Heat Source Hourly Output File:  ")
            self.files[key][0].write(self.files[key][1])
            today = time.localtime()
            self.files[key][0].write("     File created on %s/%s/%s" % (today[1], today[2], today[0]))
            self.files[key][0].write("\n\n")
            self.files[key][0].write("Datetime".ljust(14))
            for node in sorted(self.reach.iterkeys(),reverse=True):
                aaa = "%0.3f" % node
                self.files[key][0].write(aaa.ljust(14))
            self.files[key][0].write("\n")


    def __del__(self):
        for filename in self.files.itervalues():
            filename[0].close()


    def __call__(self, TheTime):
        if TheTime < self.write_time:
            return
        elif TheTime >= self.write_time:
            for node in sorted(self.reach.itervalues(),reverse=True):
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
                    "Hyd_Froude.txt": -999,    #TODO: check to see if calculated
                    "Hyd_Hyp.txt": node.Q_hyp,
                    "Hyd_Vel.txt": node.U,
                    "Hyd_WT.txt": node.W_w,
                    "Rate_Evap.txt": test, #TODO: Check
                    "Temp_H20.txt": node.T,
                    "Temp_Sed.txt": node.T_sed,
                }
                self.append(TheTime, variables, node)
            self.write_time += self.dt_out
            if TheTime.hour > self.write_time.hour:  #new day, print daily outputs
                for node in sorted(self.reach.itervalues(),reverse=True):
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
        last = min(self.reach.keys())
        first = max(self.reach.keys())
        for key in variables.iterkeys():
            if node.km == first:
                Excel_time = "%0.6f" % (TheTime.toordinal() - 693594 + (TheTime.hour +  (TheTime.minute + TheTime.second / 60) / 60 ) / 24)
                self.files[key][0].write(Excel_time.ljust(14))
            try:
                dataf = "%0.4f" % variables[key]
            except:
                print variables[key], type(variables[key]), key
                raise
            self.files[key][0].write(dataf.ljust(14))
            if node.km == last:
                self.files[key][0].write("\n")
            #self.files[key][0].flush()

            #    def dailyout(self):
#        lastnode = self.reach[-1]
#        for node in self.reach:
#
#
#            for key in variables.iterkeys():
#                if node == self.reach[0]:
#                    Excel_time = "%0.6f" % (TheTime.toordinal() - 693594 + (TheTime.hour +  (TheTime.minute + TheTime.second / 60) / 60 ) / 24)
#                    self.files[key].write(Excel_time.ljust(14))
#                dataf = "%0.3f" % variables[key]
#                self.files[key].write(dataf.ljust(14))
#                if node == self.reach[-1]:
#                    self.files[key].write("\n")
#                self.files[key].flush()


