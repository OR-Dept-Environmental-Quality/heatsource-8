from datetime import datetime, timedelta
import time
from Dieties.IniParams import IniParams

class Output(object):
    def __init__(self, dt_out, reach, write_time):
        self.dt_out = dt_out
        self.reach = reach
        self.write_time = write_time
        self.files = {"solar1": None,
                      "solar4": None,
                      "solar6": None}

        for key in self.files.iterkeys():
            self.files[key] = open(IniParams.Output_directory + key + ".txt", 'w')
            self.files[key].write("Datetime\t")
            for node in self.reach:
                self.files[key].write(`node.km` + "\t")
                if node == self.reach[-1]:
                    self.files[key].write("\n")


    def __del__(self):
        for key in self.files.iterkeys():
            self.files[key].close()

    def Store(self, TheTime):
        if TheTime < self.write_time:
            return
        elif TheTime >= self.write_time:
            self.append(TheTime)
            self.write_time += self.dt_out

    def append(self, TheTime):

        lastnode = self.reach[-1]
        for node in self.reach:
            variables = {"solar1": node.Flux["Solar"][1],
                         "solar4": node.Flux["Solar"][4],
                         "solar6": node.Flux["Solar"][6]}

            for key in self.files.iterkeys():
                if node == self.reach[0]:
                    self.files[key].write("%s\t" % TheTime.isoformat(' ')[:-6])
                    label = 1
                self.files[key].write(`variables[key]` + "\t")
                if node == self.reach[-1]:
                    self.files[key].write("\n")
                self.files[key].flush()
