from __future__ import division
from unittest import TestCase
from Time.Chronos import Chronos
from datetime import datetime, timedelta

class TestChronos(TestCase):
    def setUp(self):
        self.TS = Chronos.getInstance()
        self.TS.Start(datetime.now(),timedelta(hours=1.5),datetime.now()+timedelta(days=10))

    def test_TheTime(self):
        # Ensure that the iterator value t is always equal to TheTime
        for t in self.TS:
            self.assertEqual(t, self.TS.TheTime)