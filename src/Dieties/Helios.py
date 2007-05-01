from __future__ import division
from psyco.classes import psyobj
import math
from datetime import datetime, timedelta
from Dieties.Chronos import Chronos

class HeliosDiety(psyobj):
    """The God personification of The Sun"""
    def __init__(self):
        pass # This needs to be present to use the Singleton baseclass
    def ResetSolarVars(self):
        """Reset solar variables for time=dtime which is a datetime object"""
        JDC = Chronos.JDC
        cos,sin,atan,tan,rad,deg,pi = math.cos, math.sin, math.atan, math.tan, math.radians, math.degrees, math.pi
        #======================================================
        #Obliquity of the eliptic
        #   MeanObliquity: Average obliquity (degrees)
        #   Obliquity: Corrected obliquity (degrees)
        MeanObliquity = 23 + (26 + ((21.448 - JDC * (46.815 + JDC * (0.00059 - JDC * 0.001813))) / 60)) / 60
        Obliquity = MeanObliquity + 0.00256 * cos(rad((125.04 - 1934.136 * JDC)))
        #======================================================
        #Eccentricity of earth's orbit (unitless)
        Eccentricity = 0.016708634 - JDC * (0.000042037 + 0.0000001267 * JDC)
        #======================================================
        #Geometric mean of the longitude of the sun
        # TODO: Check this and the following algorithms
        GeoMeanLongSun = 280.46646 + JDC * (36000.76983 + 0.0003032 * JDC)
        while GeoMeanLongSun < 0 or GeoMeanLongSun > 360:
            if GeoMeanLongSun > 360: GeoMeanLongSun -= 360
            if GeoMeanLongSun < 0: GeoMeanLongSun += 360
        #======================================================
        #Geometric mean of anomaly of the sun
        GeoMeanAnomalySun = 357.52911 + JDC * (35999.05029 - 0.0001537 * JDC)
        #======================================================
        #Equation of the center of the sun (degrees)
        Dummy1 = rad(GeoMeanAnomalySun)
        Dummy2 = sin(Dummy1)
        Dummy3 = sin(Dummy2 * 2)
        Dummy4 = sin(Dummy3 * 3)
        SunEqofCenter = Dummy2 * (1.914602 - JDC * (0.004817 + 0.000014 * JDC)) + Dummy3 * (0.019993 - 0.000101 * JDC) + Dummy4 * 0.000289
        #======================================================
        #True longitude of the sun (degrees)
        #SunTrueLong = GeoMeanLongSun + SunEqofCenter
        #======================================================
        #Apparent longitude of the sun (degrees)
        SunApparentLong = (GeoMeanLongSun + SunEqofCenter) - 0.00569 - 0.00478 * sin(rad((125.04 - 1934.136 * JDC)))
        #======================================================
        #Solar declination (degrees)
        Dummy1 = sin(rad(Obliquity)) * sin(rad(SunApparentLong))
        Declination = deg(atan(Dummy1 / math.sqrt(-Dummy1 * Dummy1 + 1)))
        ## Following is the version from the manual. They seem to yield identical results:
        #Declination = asin(sin(Obliquity * pi / 180) * sin(SunApparentLong * pi / 180)) * (180/pi)
        #======================================================
        # True Anomoly (degrees)
        #SunTrueAnomaly = GeoMeanAnomalySun + SunEqofCenter
        #======================================================
        #Distance to the sun in AU
        SunRadVector = (1.000001018 * (1 - Eccentricity**2)) / (1 + Eccentricity * cos(rad(GeoMeanAnomalySun + SunEqofCenter)))
        #======================================================
        #Equation of time (minutes)
        Dummy = (tan(Obliquity * pi / 360))**2
        Dummy1 = sin(rad(2 * GeoMeanLongSun))
        Dummy2 = sin(rad(GeoMeanAnomalySun))
        Dummy3 = cos(rad(2 * GeoMeanLongSun))
        Dummy4 = sin(rad(4 * GeoMeanLongSun))
        Dummy5 = sin(rad(2 * GeoMeanAnomalySun))
        Et = deg(4 * (Dummy * Dummy1 - 2 * Eccentricity * Dummy2 + 4 * Eccentricity * Dummy * Dummy2 * Dummy3 - 0.5 * (Dummy ** 2) * Dummy4 - 1.25 * (Eccentricity ** 2) * Dummy5))
        return Et, Declination

    def CalcSolarPosition(self, lat, lon):
        """Calculates relative position of sun"""
        Et, Declination = self.ResetSolarVars()
        cos,sin,acos,tan,rad,deg,pi = math.cos, math.sin, math.acos, math.tan, math.radians, math.degrees, math.pi
        #####################################
        ## Numerical methods are copied from Heat Source VB code except where noted

        # Get the time (in DST) from Chronos
        dst = Chronos.TheTime
        #======================================================
        #Solar Time (minutes)
        SolarTime = (dst.hour*60) + (dst.minute) + (dst.second/60) + (Et - 4 * (-1*lon) + (Chronos.TZOffset(dst)*60))
        while SolarTime > 1440: # TODO: What is our goal here?
            SolarTime -= 1440  # this loop should likely be cleaned up
        HourAngle = SolarTime / 4 - 180
        if HourAngle < -180: HourAngle += 360
        #======================================================
        #Uncorrected Solar Zenith (degrees)
        Dummy = sin(rad(lat)) * sin(rad(Declination)) + cos(rad(lat)) * cos(rad(Declination)) * cos(rad(HourAngle))
        if Dummy > 1: Dummy = 1
        elif Dummy < -1: Dummy = -1
        Zenith = deg(acos(Dummy))
        #======================================================
        #Solar Azimuth (degrees)
        Dummy = cos(rad(lat)) * sin(rad(Zenith))
        if abs(Dummy) > 0.001:
            Azimuth = (sin(rad(lat)) * cos(rad(Zenith)) - sin(rad(Declination))) / Dummy
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
                RefractionCorrection = 1735 + AtmElevation * (-518.2 + AtmElevation * (103.4 + AtmElevation * (-12.79 + AtmElevation * 0.711)))
            else:
                RefractionCorrection = -20.774 / Dummy
            RefractionCorrection = RefractionCorrection / 3600
        Zenith = Zenith - RefractionCorrection
        Altitude = 90 - Zenith
        return Azimuth, Altitude, Zenith

Helios = HeliosDiety()

