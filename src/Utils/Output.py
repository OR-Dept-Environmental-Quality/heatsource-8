from __future__ import division
from datetime import datetime, timedelta
import time
from Dieties.IniParams import IniParams


class Output(object):
    def __init__(self, dt_out, reach, write_time):
        self.dt_out = dt_out
        self.reach = reach
        self.write_time = write_time
        self.files = {
                        "Heat_Cond.txt": None,
                        "Heat_Conv.txt": None,
                        "Heat_Evap.txt": None,
                        "Heat_SR1.txt": None,
                        "Heat_SR4.txt": None,
                        "Heat_SR6.txt": None,
                        "Heat_TR.txt": None,
                        "Hyd_DA.txt": None,
                        "Hyd_DM.txt": None,
                        "Hyd_Flow.txt": None,
                        "Hyd_Froude.txt": None,
                        "Hyd_Hyp.txt": None,
                        "Hyd_Vel.txt": None,
                        "Hyd_WT.txt": None,
                        "Rate_Evap.txt": None,
                        "Shade.txt": None,
                        "Temp_H20.txt": None,
                        "Temp_Sed.txt": None,
                        "VTS.txt": None
                    }

        for key in self.files.iterkeys():
            self.files[key] = open(IniParams.OutputDirectory + key, 'w')
            self.files[key].write("Heat Source Hourly Output File:\n\n")
            self.files[key].write("Datetime".ljust(14))
            for node in self.reach:
                aaa = "%0.3f" % node.km
                self.files[key].write(aaa.ljust(14))
                if node == self.reach[-1]:
                    self.files[key].write("\n")


    def __del__(self):
        for key in self.files.iterkeys():
            self.files[key].close()

    def Store(self, TheTime):
        if TheTime < self.write_time:
            return
        elif TheTime >= self.write_time:
            for node in self.reach:
                variables = {
                    "Heat_Cond.txt": node.Flux["Conduction"],
                    "Heat_Conv.txt": node.Flux["Convection"],
                    "Heat_Evap.txt": node.Flux["Evaporation"],
                    "Heat_SR1.txt": node.Flux["Solar"][1],
                    "Heat_SR4.txt": node.Flux["Solar"][4],
                    "Heat_SR6.txt": node.Flux["Solar"][6],
                    "Heat_TR.txt": node.Flux["Longwave"],
                    "Hyd_DA.txt": node.A / node.W_w,
                    "Hyd_DM.txt": node.d_w,
                    "Hyd_Flow.txt": node.Q,
                    "Hyd_Froude.txt": -999,    #TODO: check to see if calculated
                    "Hyd_Hyp.txt": -999,     #TODO: check to see if calculated
                    "Hyd_Vel.txt": node.U,
                    "Hyd_WT.txt": node.W_w,
                    "Rate_Evap.txt": node.Evap_Rate,
                    "Temp_H20.txt": node.T,
                    "Temp_Sed.txt": node.T_sed,
                }
                self.append(TheTime, variables, node)
            self.write_time += self.dt_out
            if TheTime.hour > self.write_time.hour:  #new day, print daily outputs
                for node in self.reach:
                    variables = {
                        "Shade.txt": (node.Flux["Solar_daily_sum"][1] - node.Flux["Solar_daily_sum"][4]) / node.Flux["Solar_daily_sum"][1],
                        "VTS.txt": node.ViewToSky
                    }
                    self.append(TheTime, variables, node)


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


    def append(self, TheTime, variables, node):
        for key in variables.iterkeys():
            if node == self.reach[0]:
                Excel_time = "%0.6f" % (TheTime.toordinal() - 693594 + (TheTime.hour +  (TheTime.minute + TheTime.second / 60) / 60 ) / 24)
                self.files[key].write(Excel_time.ljust(14))
            dataf = "%0.3f" % variables[key]
            self.files[key].write(dataf.ljust(14))
            if node == self.reach[-1]:
                self.files[key].write("\n")
            self.files[key].flush()

