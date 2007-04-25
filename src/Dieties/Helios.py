from __future__ import division
import math
from datetime import datetime, timedelta
from Dieties.Chronos import Chronos
from Utils.SingletonMixin import Singleton

class HeliosDiety(Singleton):
    """The God personification of The Sun"""
    def __init__(self):
        self.JD = None # Julian Date
        self.JDC = None # Julian Century

    def ResetSolarVars(self):
        """Reset solar variables for time=dtime which is a datetime object"""
        self.JD, self.JDC = Chronos.JD, Chronos.JDC
        cos,sin,atan,tan,rad,deg,pi = math.cos, math.sin, math.atan, math.tan, math.radians, math.degrees, math.pi
        #======================================================
        #Obliquity of the eliptic
        #   MeanObliquity: Average obliquity (degrees)
        #   Obliquity: Corrected obliquity (degrees)
        seconds = 21.448 - self.JDC * (46.815 + self.JDC * (0.00059 - self.JDC * 0.001813))
        self.MeanObliquity = 23 + (26 + (seconds / 60)) / 60
        omega = 125.04 - 1934.136 * self.JDC
        self.Obliquity = self.MeanObliquity + 0.00256 * cos(rad(omega))
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
        Dummy1 = rad(self.GeoMeanAnomalySun)
        Dummy2 = sin(Dummy1)
        Dummy3 = sin(Dummy2 * 2)
        Dummy4 = sin(Dummy3 * 3)
        self.SunEqofCenter = Dummy2 * (1.914602 - self.JDC * (0.004817 + 0.000014 * self.JDC)) + Dummy3 * (0.019993 - 0.000101 * self.JDC) + Dummy4 * 0.000289
        #======================================================
        #True longitude of the sun (degrees)
        self.SunTrueLong = self.GeoMeanLongSun + self.SunEqofCenter
        #======================================================
        #Apparent longitude of the sun (degrees)
        self.SunApparentLong = self.SunTrueLong - 0.00569 - 0.00478 * sin(rad(omega))
        #======================================================
        #Solar declination (degrees)
        Dummy1 = sin(rad(self.Obliquity)) * sin(rad(self.SunApparentLong))
        Declination = atan(Dummy1 / math.sqrt(-Dummy1 * Dummy1 + 1))
        self.Declination = deg(Declination)
        ## Following is the version from the manual. They seem to yield identical results:
        #self.Declination = asin(sin(self.Obliquity * pi / 180) * sin(self.SunApparentLong * pi / 180)) * (180/pi)
        #======================================================
        # True Anomoly (degrees)
        self.SunTrueAnomaly = self.GeoMeanAnomalySun + self.SunEqofCenter
        #======================================================
        #Distance to the sun in AU
        self.SunRadVector = (1.000001018 * (1 - self.Eccentricity**2)) / (1 + self.Eccentricity * cos(rad(self.SunTrueAnomaly)))
        #======================================================
        #Equation of time (minutes)
        Dummy = (tan(self.Obliquity * pi / 360))**2
        Dummy1 = sin(rad(2 * self.GeoMeanLongSun))
        Dummy2 = sin(rad(self.GeoMeanAnomalySun))
        Dummy3 = cos(rad(2 * self.GeoMeanLongSun))
        Dummy4 = sin(rad(4 * self.GeoMeanLongSun))
        Dummy5 = sin(rad(2 * self.GeoMeanAnomalySun))
        self.Et = deg(4 * (Dummy * Dummy1 - 2 * self.Eccentricity * Dummy2 + 4 * self.Eccentricity * Dummy * Dummy2 * Dummy3 - 0.5 * (Dummy ** 2) * Dummy4 - 1.25 * (self.Eccentricity ** 2) * Dummy5))

    def CalcSolarPosition(self, lat, lon):
        """Calculates relative position of sun"""
        self.ResetSolarVars()
        cos,sin,acos,tan,rad,deg,pi = math.cos, math.sin, math.acos, math.tan, math.radians, math.degrees, math.pi
        #####################################
        ## Numerical methods are copied from Heat Source VB code except where noted

        # Get the time (in DST) from Chronos
        dst = Chronos.TheTime
        #########################################################
        # We need to get the DST hour, minute, second and offset from the python class
        H = dst.hour*60
        M = dst.minute
        S = dst.second/60
        tz = Chronos.TZOffset(dst)*60
        #======================================================
        #Solar Time (minutes)
        SolarTime = H + M + S + (self.Et - 4 * (-1*lon) + tz)
        while SolarTime > 1440: # TODO: What is our goal here?
            SolarTime -= 1440  # this loop should likely be cleaned up
        HourAngle = SolarTime / 4 - 180
        if HourAngle < -180: HourAngle += 360
        #======================================================
        #Uncorrected Solar Zenith (degrees)
        Dummy = sin(rad(lat)) * sin(rad(self.Declination)) + cos(rad(lat)) * cos(rad(self.Declination)) * cos(rad(HourAngle))
        if Dummy > 1: Dummy = 1
        elif Dummy < -1: Dummy = -1
        Dummy1 = acos(Dummy)
        Zenith = deg(Dummy1)
        #======================================================
        #Solar Azimuth (degrees)
        Dummy = cos(rad(lat)) * sin(rad(Zenith))
        if abs(Dummy) > 0.001:
            Azimuth = (sin(rad(lat)) * cos(rad(Zenith)) - sin(rad(self.Declination))) / Dummy
            # TODO: Find out what this is supposed to do!!
            # We test to see if it's greater than one, then if so, we test to see if it's less than zero...
            # This makes no logical sense.
            if abs(Azimuth) > 1:
                if Azimuth < 0:
                    Azimuth = -1
                else:
                    Azimuth = 1
            Azimuth = 180 - deg(acos(Azimuth))
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
            Dummy = tan(rad(AtmElevation))
            if AtmElevation > 5:
                RefractionCorrection = 58.1 / Dummy - 0.07 / Dummy ** 3 + 0.000086 / Dummy ** 5
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
        return Azimuth, Altitude, Zenith

Helios = HeliosDiety.getInstance()

