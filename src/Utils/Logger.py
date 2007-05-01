import time

class LoggerDiety(object):
    def __init__(self):
        self._last = None
        self._file = None
    def SetFile(self, filename):
        self._file = filename
    def __call__(self, message, n=None,t=None): self.write(message)
    def write(self, message):
        if message != self._last:
            t = time.strftime("%H:%M:%S",time.localtime(time.time()))
            self._file.write("%s-> %s\n"% (t,message))
            self._last = message

Logger = LoggerDiety()