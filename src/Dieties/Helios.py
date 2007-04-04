from __future__ import division
import math
from datetime import datetime, timedelta
from Dieties.Chronos import Chronos
from Utils.SingletonMixin import Singleton

class Helios(Singleton):
    """The God personification of The Sun"""
    def __init__(self):
        self.DST = None # Holder for a time object
        self.UTC = None # datetime object is Coordinated Universal Time (Greenwich Mean Time in the ol' days)
        self.JD = None # Julian Date
        self.JDC = None # Julian Century
        self.Chronos = Chronos.getInstance() # The God of Time

    def ResetSolarVars(self):
        """Reset solar variables for time=dtime which is a datetime object"""
        self.JD, self.JDC = self.Chronos.JD, self.Chronos.JDC
        #======================================================
        #Obliquity of the eliptic
        #   MeanObliquity: Average obliquity (degrees)
        #   Obliquity: Corrected obliquity (degrees)
        seconds = 21.448 - self.JDC * (46.815 + self.JDC * (0.00059 - self.JDC * 0.001813))
        self.MeanObliquity = 23 + (26 + (seconds / 60)) / 60
        omega = 125.04 - 1934.136 * self.JDC
        self.Obliquity = self.MeanObliquity + 0.00256 * math.cos(omega * math.pi / 180)
        #======================================================
        #Eccentricity of earth's orbit (unitless)
        self.Eccentricity = 0.016708634 - self.JDC * (0.000042037 + 0.0000001267 * self.JDC)
        #======================================================
        #Geometric mean of the longitude of the sun
        # TODO: Check this and the following algorithms
        self.GeoMeanLongSun = 280.46646 + self.JDC * (36000.76983 + 0.0003032 * self.JDC)
        while self.GeoMeanLongSun < 0 or self.GeoMeanLongSun > 360:
            if self.GeoMeanLongSun > 360: self.GeoMeanLongSun -= 360
            if self.GeoMeanLongSun < 0: self.GeoMeanLongSun += 360
        #======================================================
        #Geometric mean of anomaly of the sun
        self.GeoMeanAnomalySun = 357.52911 + self.JDC * (35999.05029 - 0.0001537 * self.JDC)
        #======================================================
        #Equation of the center of the sun (degrees)
        Dummy1 = self.GeoMeanAnomalySun * math.pi / 180
        Dummy2 = math.sin(Dummy1)
        Dummy3 = math.sin(Dummy2 * 2)
        Dummy4 = math.sin(Dummy3 * 3)
        self.SunEqofCenter = Dummy2 * (1.914602 - self.JDC * (0.004817 + 0.000014 * self.JDC)) + Dummy3 * (0.019993 - 0.000101 * self.JDC) + Dummy4 * 0.000289
        #======================================================
        #True longitude of the sun (degrees)
        self.SunTrueLong = self.GeoMeanLongSun + self.SunEqofCenter
        #======================================================
        #Apparent longitude of the sun (degrees)
        self.SunApparentLong = self.SunTrueLong - 0.00569 - 0.00478 * math.sin(omega * math.pi / 180)
        #======================================================
        #Solar declination (degrees)
        Dummy1 = math.sin(self.Obliquity * math.pi / 180) * math.sin(self.SunApparentLong * math.pi / 180)
        Declination = math.atan(Dummy1 / math.sqrt(-Dummy1 * Dummy1 + 1))
        self.Declination = Declination * 180 / math.pi
        ## Following is the version from the manual. They seem to yield identical results:
        #self.Declination = math.asin(math.sin(self.Obliquity * math.pi / 180) * math.sin(self.SunApparentLong * math.pi / 180)) * (180/math.pi)
        #======================================================
        # True Anomoly (degrees)
        self.SunTrueAnomaly = self.GeoMeanAnomalySun + self.SunEqofCenter
        #======================================================
        #Distance to the sun in AU
        self.unRadVector = (1.000001018 * (1 - self.Eccentricity**2)) / (1 + self.Eccentricity * math.cos(self.SunTrueAnomaly * math.pi / 180))
        #======================================================
        #Equation of time (minutes)
        Dummy = (math.tan(self.Obliquity * math.pi / 360))**2
        Dummy1 = math.sin(2 * self.GeoMeanLongSun * math.pi / 180)
        Dummy2 = math.sin(self.GeoMeanAnomalySun * math.pi / 180)
        Dummy3 = math.cos(2 * self.GeoMeanLongSun * math.pi / 180)
        Dummy4 = math.sin(4 * self.GeoMeanLongSun * math.pi / 180)
        Dummy5 = math.sin(2 * self.GeoMeanAnomalySun * math.pi / 180)
        self.Et = 4 * (Dummy * Dummy1 - 2 * self.Eccentricity * Dummy2 + 4 * self.Eccentricity * Dummy * Dummy2 * Dummy3 - 0.5 * (Dummy ** 2) * Dummy4 - 1.25 * (self.Eccentricity ** 2) * Dummy5) * (180/math.pi)

    def CalcSolarPosition(self, lat, lon):
        """Calculates relative position of sun"""
        self.ResetSolarVars()
        #####################################
        ## Numerical methods are copied from Heat Source VB code except where noted

        # Get the time (in DST) from Chronos
        dst = self.Chronos.TheTime
        #########################################################
        # We need to get the DST hour, minute, second and offset from the python class
        H = dst.hour*60
        M = dst.minute
        S = dst.second/60
        tz = self.Chronos.TZOffset(dst)*60
        print H,M,S,type(tz)
        #======================================================
        #Solar Time (minutes)
        SolarTime = H + M + S + (self.Et - 4 * (-1*lon) + tz)
        while SolarTime > 1440: # TODO: What is our goal here?
            SolarTime -= 1440  # this loop should likely be cleaned up
        HourAngle = SolarTime / 4 - 180
        if HourAngle < -180: HourAngle += 360
        #======================================================
        #Uncorrected Solar Zenith (degrees)
        Dummy = math.sin(lat * math.pi / 180) * math.sin(self.Declination * math.pi / 180) + math.cos(lat * math.pi / 180) * math.cos(self.Declination * math.pi / 180) * math.cos(HourAngle * math.pi / 180)
        if Dummy > 1: Dummy = 1
        elif Dummy < -1: Dummy = -1
        Dummy1 = math.acos(Dummy)
        Zenith = Dummy1 * 180 / math.pi
        #======================================================
        #Solar Azimuth (degrees)
        Dummy = math.cos(lat * math.pi / 180) * math.sin(Zenith * math.pi / 180)
        if abs(Dummy) > 0.001:
            Azimuth = (math.sin(lat * math.pi / 180) * math.cos(Zenith * math.pi / 180) - math.sin(self.Declination * math.pi / 180)) / Dummy
            # TODO: Find out what this is supposed to do!!
            # We test to see if it's greater than one, then if so, we test to see if it's less than zero...
            # This makes no logical sense.
            if abs(Azimuth) > 1:
                if Azimuth < 0:
                    Azimuth = -1
                else:
                    Azimuth = 1
            Azimuth = 180 - (math.acos(Azimuth) * 180 / math.pi)
            if HourAngle > 0: Azimuth = -1*Azimuth
        else:
            if lat > 0:
                Azimuth = 180
            else:
                Azimuth = 0
        if Azimuth < 0: Azimuth += 360
        #======================================================
        #Solar Zenith Corrected for Refraction (degrees)
        #Solar Altitude Corrected for Refraction (degrees)
        AtmElevation = 90 - Zenith
        if AtmElevation > 85:
            RefractionCorrection = 0
        else:
            Dummy = math.tan(AtmElevation * math.pi / 180)
            if AtmElevation > 5:
                RefractionCorrection = 58.1 / Dummy - 0.07 / Dummy ^ 3 + 0.000086 / Dummy ^ 5
            elif AtmElevation > -0.575:
                Dummy1 = -12.79 + AtmElevation * 0.711
                Dummy2 = 103.4 + AtmElevation * Dummy1
                Dummy3 = -518.2 + AtmElevation * Dummy2
                RefractionCorrection = 1735 + AtmElevation * Dummy3
            else:
                RefractionCorrection = -20.774 / Dummy
            RefractionCorrection = RefractionCorrection / 3600
        Zenith = Zenith - RefractionCorrection
        Altitude = 90 - Zenith
        return Azimuth, Altitude


