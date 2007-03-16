from unittest import TestCase
from Excel.HeatSourceInterface import HeatSourceInterface
from Utils.Time import TimeUtil
from SolarRad import SolarRad
from PyTZ import timezone,utc
import datetime

class TestDataSheet(TestCase):
    def setUp(self):
        self.time = TimeUtil()
        pst = timezone('US/Pacific')
        self.date1 = datetime.datetime(2007, 2, 12, 9, 35, 15,tzinfo=pst)
        lat = 45 + (31/60)
        lon = -1*(122 + (39/60))
        self.solar = SolarRad(lat,lon)
    def tearDown(self): pass
    def testPrintSolarVars(self):
        self.solar.ResetSolarVars(self.date1)
        l = ['JD','JDC','MeanObliquity','Obliquity','Eccentricity',
             'GeoMeanLongSun','GeoMeanAnomalySun',
             'SunEqofCenter','SunTrueLong','SunApparentLong',
             'SolarDeclination','SunTrueAnomaly',
             'unRadVector', 'Et']
        for i in xrange(len(l)):
            print "'%s': %0.9f," % (l[i], getattr(self.solar,l[i]))
        #results for 12Feb2007 09:35:15:
        res = {'JD': 2454144.232810000,
                'JDC': 0.071163116,
                'MeanObliquity': 23.438365693,
                'Obliquity': 23.440864049,
                'Eccentricity': 0.016705642,
                'GeoMeanLongSun': 322.393417437,
                'GeoMeanAnomalySun': 2919.333697299,
                'SunEqofCenter': 1.232480167,
                'SunTrueLong': 323.625897604,
                'SunApparentLong': 323.621250259,
                'SolarDeclination': -13.647313406,
                'SunTrueAnomaly': 2920.566177466,
                'unRadVector': 0.987193925,
                'Et': -14.257934091,}
