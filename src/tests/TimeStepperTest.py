from __future__ import division
from unittest import TestCase
from Utils.TimeStepper import TimeStepper
from datetime import datetime, timedelta

class TestTimeStepper(TestCase):
    def setUp(self):
        self.TS = TimeStepper(datetime.now(),timedelta(hours=1.5),datetime.now()+timedelta(days=10))

    def test_GetSet(self):
        print self.TS.start, self.TS.dT, self.TS.stop
        #for i in self.TS:
        #    print i
        for t,n in self.TS.itercount():
            print t,n