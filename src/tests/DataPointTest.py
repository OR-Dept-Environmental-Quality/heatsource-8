from __future__ import division
import datetime, math
from unittest import TestCase
from Utils.DataPoint import DataPoint

class TestDataPoint(TestCase):
    def setUp(self):
        self.date1 = datetime.datetime(2007, 2, 12, 9, 35, 15)
        self.date2 = datetime.datetime(2001, 7, 8, 1, 0, 0)

        self.place1 = (3,5.7)
        self.place2 = (8.3, 5)

        self.datapoint = DataPoint(4, time=self.date1, place=self.place1)
    
        self.timepoint = DataPoint(8, time=self.date2)
        self.placepoint = DataPoint(28, place=self.place2)

    def tearDown(self):
        pass
    def test_DataPoints(self):
        TP = DataPoint(18, time=self.date1)
        PP = DataPoint(3, place=self.place1)

        self.assertNotEqual(TP,PP)
        self.assertEqual(TP, PP*6)

        self.assertEqual(TP.time, self.datapoint.time)
        self.assertEqual(PP.place, self.datapoint.place)
        self.assertEqual(TP.place, PP.time)

        a = math.cos((TP/3) * 48)
        b = math.cos((PP*2) * 48)
        c = math.cos((9-3) *48)

        self.assertEqual(a,b)
        self.assertEqual(b,c)
