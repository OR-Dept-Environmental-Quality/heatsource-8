from __future__ import division
from unittest import TestCase
from Utils.TimeStepper import TimeStepper
from datetime import datetime, timedelta

class TestTimeStepper(TestCase):
    def setUp(self):
        self.TS = TimeStepper.getInstance()

    def test_GetSet(self):
        start = datetime.now()
        minute = timedelta(minutes=1)
        stop = start + timedelta(days=10)
        dT = timedelta(hours=1)

        self.TS.start = start
        self.TS.dT = dT
        self.TS.stop = stop

        print self.TS.start, self.TS.dT, self.TS.stop
