from unittest import TestCase
from Excel.HeatSourceInterface import HeatSourceInterface
from Utils.Time import TimeUtil
from pytz import timezone,utc
import datetime

class TestDataSheet(TestCase):
    def setUp(self):
        self.time = TimeUtil()
        pst = timezone('US/Pacific')
        self.date1 = datetime.datetime(2007, 2, 12, 9, 35, 15,tzinfo=pst)
        self.date2 = datetime.datetime(2001, 7, 8, 1, 0, 0, tzinfo=pst)
        self.JD, self.JDC = 2454144.23281,0.0711631159
        self.JD1,self.JDC1 = 2452098.875,0.015164271
    def tearDown(self): pass
    def testMakeTime(self):
        """Test ability to make a datetime object"""
        doc = HeatSourceInterface("c:\\eclipse\\HeatSource\\Toketee_CCC.xls")
        date = doc.GetValue("G18","Continuous Data")
        self.assertEqual(self.time.MakeDatetime(date), self.date2)
        del doc
    def testJD(self):
        JD,JDC = self.time.GetJD(self.date1)
        JD1,JDC1 = self.time.GetJD(self.date2)
        self.assertEqual(JD,self.JD)
        self.assertEqual(JDC,self.JDC)
        self.assertEqual(JD1,self.JD1)
        self.assertEqual(JDC1,self.JDC1)
    def testTZOffset(self):
        date1 = self.time.MakeDatetime(self.date1)
        self.assertEqual(self.time.TZOffset(date1),8)
    def testGetUTC(self):
        date1 = self.time.MakeDatetime(self.date1)
        tup1 = self.date1.utctimetuple()
        tup2 = self.time.GetUTC(date1).timetuple()
        self.assertEqual(tup1,tup2)
