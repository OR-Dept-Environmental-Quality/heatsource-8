from datetime import datetime, timedelta
import time

class Output(object):
    def __init__(self, dt_out, reach, write_time):
        self.dt_out = dt_out
        self.reach = reach
        self.write_time = write_time
        self.file = open("D:\\dan\\heatsource tests\\test.txt", 'w')
    
    def __del__(self):
        self.file.close()

    def Store(self, TheTime):
        if TheTime < self.write_time:
            return
        elif TheTime >= self.write_time:
            self.append()
            self.write_time += self.dt_out

    def append(self):
        self.file.write(`self.write_time` + "something\n")
        self.file.flush()
        print "aaa"