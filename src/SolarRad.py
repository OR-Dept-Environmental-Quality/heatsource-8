from __future__ import division
import math
from datetime import datetime, timedelta
from Utils.TimeUtil import TimeUtil
from Utils.SingletonMixin import Singleton

# TODO: Remove all members of SolarRad that are not needed.
# There are likely a lot of calculations made only to be used in a later calculation. Maintaining
# all of these numbers as members will add a (small) amount to the size of the object, thus adding to
# memory space and load times. We should trim this down by making temporary calculations temporary so that
# the memory buffers are cleared when they are not needed.

class SolarRad(Singleton):
    def __init__(self):
        self.DST = None # Holder for a time object
        self.UTC = None # datetime object is Coordinated Universal Time (Greenwich Mean Time in the ol' days)
        self.JD = None # Julian Date
        self.JDC = None # Julian Century
        self.TimeUtil = TimeUtil()
    def TestDtime(self, dtime):
        if not isinstance(dtime, datetime):
            raise Exception("%s must be used with a Python datetime.datetime instance, not %s"% \
                            (self.__class__.__name__, dtime.__class__.__name__))
    def SetTime(self,dtime):
        """Create julian date and julian century as defined in HeatSource manual"""
        self.TestDtime(dtime)
        self.JD,self.JDC = self.TimeUtil.GetJD(dtime) # Then create julian date and century in UTC
        if not self.JD or not self.JDC:
            raise Exception("No Julian date calculated")

    def ResetSolarVars(self, dtime):
        """Reset solar variables for time=dtime which is a datetime object"""
        self.SetTime(dtime)
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
        SolarDeclination = math.atan(Dummy1 / math.sqrt(-Dummy1 * Dummy1 + 1))
        self.SolarDeclination = SolarDeclination * 180 / math.pi
        ## Following is the version from the manual. They seem to yield identical results:
        #self.SolarDeclination = math.asin(math.sin(self.Obliquity * math.pi / 180) * math.sin(self.SunApparentLong * math.pi / 180)) * (180/math.pi)
        #======================================================
        #Solar True Anomoly (degrees)
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

    def CalcSolarPosition(self, dtime, lat, lon):
        """Calculates relative position of sun"""
        self.ResetSolarVars(dtime)
        #####################################
        ## Numerical methods are copied from Heat Source VB code except where noted

        #########################################################
        # We need to get the DST hour, minute, second and offset from the python class
        H = self.DST.hour*60
        M = self.DST.minute
        S = self.DST.second/60
        tz = self.t.GetTZOffset(self.DST)*60

        #======================================================
        #Solar Time (minutes)
        SolarTime = hour + minute + second + (self.Et - 4 * (-1*long) + tz)
        while SolarTime > 1440: # TODO: What is our goal here?
            SolarTime -= 1440  # this loop should likely be cleaned up
        HourAngle = SolarTime / 4 - 180
        if HourAngle < -180: HourAngle += 360
        #======================================================
        #Uncorrected Solar Zenith (degrees)
        Dummy = math.sin(lat * math.pi / 180) * math.sin(self.SolarDeclination * math.pi / 180) + math.cos(lat * math.pi / 180) * math.cos(self.SolarDeclination * math.pi / 180) * math.cos(HourAngle * math.pi / 180)
        if Dummy > 1: Dummy = 1
        elif Dummy < -1: Dummy = -1
        Dummy1 = math.acos(Dummy)
        self.SolarZenith = Dummy1 * 180 / math.pi
        #======================================================
        #Solar Azimuth (degrees)
        Dummy = math.cos(lat * math.pi / 180) * math.sin(self.SolarZenith * math.pi / 180)
        if abs(Dummy) > 0.001:
            self.SolarAzimuth = (math.sin(lat * math.pi / 180) * math.cos(self.SolarZenith * math.pi / 180) - math.sin(self.SolarDeclination * math.pi / 180)) / Dummy
            # TODO: Find out what this is supposed to do!!
            # We test to see if it's greater than one, then if so, we test to see if it's less than zero...
            # This makes no logical sense.
            if abs(self.SolarAzimuth) > 1:
                if self.SolarAzimuth < 0:
                    self.SolarAzimuth = -1
                else:
                    self.SolarAzimuth = 1
            self.SolarAzimuth = 180 - (math.acos(self.SolarAzimuth) * 180 / math.pi)
            if HourAngle > 0: self.SolarAzimuth = -1*self.SolarAzimuth
        else:
            if lat > 0:
                self.SolarAzimuth = 180
            else:
                self.SolarAzimuth = 0
        if self.SolarAzimuth < 0: self.SolarAzimuth += 360
        #======================================================
        #Solar Zenith Corrected for Refraction (degrees)
        #Solar Altitude Corrected for Refraction (degrees)
        AtmElevation = 90 - self.SolarZenith
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
        self.SolarZenith = self.SolarZenith - RefractionCorrection
        self.SolarAltitude = 90 - self.SolarZenith

#    def CalcSolarFlux(self):
#        #Like the others, taken from VB code unless otherwise noted
#        #======================================================
#        # If it's night, we get out quick, rather than use the old if format.
#        if self.SolarAltitude <= 0: #Nighttime
#            self.SolarAltitude = 0
#            self.FLUX_Direct = [0 for i in xrange(8)]
#            self.FLUX_Diffuse = [0 for i in xrange(8)]
#            self.FLUX_Solar = [0 for i in xrange(7)]
#            return #Nothing else to do, so ignore rest of method
#        #######################################
#
#        #   Solar_Constant = kj/m2*hr
#        #   Air_Mass = Optical air mass thickness
#        #   Trans_Air = Transmissivity of air mass
#        #   Clearness_Index = deminsionless ratio
#        #   Diffuse_Fraction = Fraction of solar that is diffuse
#        #======================================================
#        #======================================================
#        #Set Directional Land Cover Types & Calculate Riparian Boundaries
#        #   LC_TotElev() = Riparian height above stream (meters)
#        #   LC_Distance = Distance from stream node to veg (meters)
#        #   LC_Elev = Elevation at each land cover sample point
#        #   LC_ElevDiff = Elevation differance btwn land cover sample point and stream
#        #Set Directional Topo Shade
#        #   Topo_Alt = Topo shade angle (rad)
#        #======================================================
#            if self.SolarAzimuth <= 67.5: #NE Direction
#                Direction = 1
#                Topo_Alt = theTopo_E(Node)
#            ElseIf SolarAzimuth > 67.5 And SolarAzimuth <= 112.5 Then 'E Direction
#                Direction = 2
#                Topo_Alt = theTopo_E(Node)
#            ElseIf SolarAzimuth > 112.5 And SolarAzimuth <= 157.5 Then  'SE Direction
#                Direction = 3
#                Topo_Alt = 0.5 * (theTopo_E(Node) + theTopo_S(Node))
#            ElseIf SolarAzimuth > 157.5 And SolarAzimuth <= 202.5 Then 'S Direction
#                Direction = 4
#                Topo_Alt = theTopo_S(Node)
#            ElseIf SolarAzimuth > 202.5 And SolarAzimuth <= 247.5 Then 'SW Direction
#                Direction = 5
#                Topo_Alt = 0.5 * (theTopo_W(Node) + theTopo_S(Node))
#            ElseIf SolarAzimuth > 247.5 And SolarAzimuth <= 292.5 Then 'W Direction
#                Direction = 6
#                Topo_Alt = theTopo_W(Node)
#            Else 'NW Direction
#                Direction = 7
#                Topo_Alt = theTopo_W(Node)
#            End If
#            '======================================================
#            'Calculate Land Cover Horizontal Spacing
#            For Zone = 1 To 4
#                LC_TotElev(Zone) = theVHeight(Node, Zone, Direction) + theSlopeHeight(Node, Zone, Direction)
#                If Zone = 1 Then
#                    LC_Distance(Zone) = Dx_lc * (Zone - 0.5) - theOverHang(Node, Direction)
#                Else
#                    LC_Distance(Zone) = Dx_lc * (Zone - 0.5)
#                End If
#                If LC_Distance(Zone) < 0 Then LC_Distance(Zone) = 0.00001
#            Next Zone
#            '======================================================
#            'Route solar radiation to the stream surface
#            '   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
#            '       0 - Edge of atmosphere
#            '       1 - Above Topography
#            '       2 - Above Land Cover
#            '       3 - Above Stream (After Land Cover Shade)
#            '       4 - Above Stream (What a Solar Pathfinder Measures)
#            '       5 - Entering Stream
#            '       6 - Received by Water Column
#            '       7 - Received by Bed
#            '======================================================
#            '0 - Edge of atmosphere
#            JulianDay = -DateDiff("d", theTime, DateSerial(year(theTime), 1, 1))
#            Rad_Vec = 1 + 0.017 * Cos((2 * Pi / 365) * (186 - JulianDay + Hour_DST / 24))
#            Solar_Constant = 1367 'W/m2
#            FLUX_Direct(0) = (Solar_Constant / Rad_Vec ^ 2) * Sin(SolarAltitude * Pi / 180) 'Global Direct Solar Radiation
#            FLUX_Diffuse(0) = 0
#            '======================================================
#            '1 - Above Topography
#            Dummy1 = 35 / Sqr(1224 * Sin(SolarAltitude * Pi / 180) + 1)
#            Air_Mass = Dummy1 * Exp(-0.0001184 * theElevation(Node, 0, 1))
#            Trans_Air = 0.0685 * Cos((2 * Pi / 365) * (JulianDay + 10)) + 0.8
#            'Calculate Diffuse Fraction
#            FLUX_Direct(1) = FLUX_Direct(0) * (Trans_Air ^ Air_Mass) * (1 - 0.65 * Cloudiness(theHour) ^ 2)
#            If FLUX_Direct(0) = 0 Then
#                Clearness_Index = 1
#            Else
#                Clearness_Index = FLUX_Direct(1) / FLUX_Direct(0)
#            End If
#            Dummy = FLUX_Direct(1)
#            Dummy1 = 0.938 + 1.071 * Clearness_Index
#            Dummy2 = 5.14 * Clearness_Index ^ 2
#            Dummy3 = 2.98 * Clearness_Index ^ 3
#            Dummy4 = Sin(2 * Pi * (JulianDay - 40) / 365)
#            Dummy5 = (0.009 - 0.078 * Clearness_Index)
#            Diffuse_Fraction = Dummy1 - Dummy2 + Dummy3 - Dummy4 * Dummy5
#            FLUX_Direct(1) = Dummy * (1 - Diffuse_Fraction)
#            FLUX_Diffuse(1) = Dummy * (Diffuse_Fraction) * (1 - 0.65 * Cloudiness(theHour) ^ 2)
#            '======================================================
#            '2 - Above Land Cover
#            '3 - Above Stream Surface (Above Bank Shade)
#            If SolarAltitude <= Topo_Alt Then  '>Topographic Shade IS Occurring<
#                Flag_Topo = 1
#                FLUX_Direct(2) = 0
#                FLUX_Diffuse(2) = FLUX_Diffuse(1) * (theTopo_W(Node) + theTopo_S(Node) + theTopo_E(Node)) / (90 * 3)
#                FLUX_Direct(3) = 0
#                FLUX_Diffuse(3) = FLUX_Diffuse(2) * View_To_Sky(Node)
#            Else  '>Topographic Shade is NOT Occurring<
#                FLUX_Direct(2) = FLUX_Direct(1)
#                FLUX_Diffuse(2) = FLUX_Diffuse(1) * (1 - (theTopo_W(Node) + theTopo_S(Node) + theTopo_E(Node)) / (90 * 3))
#                Dummy1 = FLUX_Direct(2)
#                For Zone = 4 To 1 Step -1 'Calculate shade density and FLUX_Direct(3)
#                    LC_ShadowLength = (theVHeight(Node, Zone, Direction) + theSlopeHeight(Node, Zone, Direction)) / Tan(SolarAltitude * Pi / 180) 'Vegetation Shadow Casting
#                    If LC_ShadowLength >= LC_Distance(Zone) Then 'Veg Shade IS Occurring
#                        Path(Zone) = Dx_lc / Cos(SolarAltitude * Pi / 180)
#                        If theVDensity(Node, Zone, Direction) = 1 Then
#                            Rip_Extinct(Zone) = 1
#                            Shade_Density(Zone) = 1
#                        Else
#                            Rip_Extinct(Zone) = -Log(1 - theVDensity(Node, Zone, Direction)) / 10
#                            Shade_Density(Zone) = 1 - Exp(-Rip_Extinct(Zone) * Path(Zone))
#                        End If
#                    Else 'Veg Shade IS NOT Occurring
#                        Shade_Density(Zone) = 0
#                    End If
#                    Dummy1 = Dummy1 * (1 - Shade_Density(Zone))
#                Next Zone
#                FLUX_Direct(3) = Dummy1
#                FLUX_Diffuse(3) = FLUX_Diffuse(2) * View_To_Sky(Node)
#            End If
#            ':::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#            '4 - Above Stream Surface (What a Solar Pathfinder measures)
#            'Account for bank shade
#            If Flag_Topo = 0 Then
#                For Zone = 4 To 1 Step -1 'Calculate bank shade and FLUX_Direct(4)
#                    DEM_ShadowLength = theSlopeHeight(Node, Zone, Direction) / Tan(SolarAltitude * Pi / 180) 'Bank Shadow Casting
#                    If DEM_ShadowLength >= LC_Distance(Zone) Then 'Bank Shade is Occurring
#                        FLUX_Direct(4) = 0
#                        FLUX_Diffuse(4) = FLUX_Diffuse(3)
#                    Else
#                        FLUX_Direct(4) = FLUX_Direct(3)
#                        FLUX_Diffuse(4) = FLUX_Diffuse(3)
#                    End If
#                Next Zone
#            Else
#                FLUX_Direct(4) = 0
#                FLUX_Diffuse(4) = FLUX_Diffuse(3)
#            End If
#            'Account for emergent vegetation
#            If Flag_Emergent = 1 Then
#                Path(0) = theVHeight(Node, 0, 0) / Sin(SolarAltitude * Pi / 180): If Path(0) > theWidth_B(Node) Then Path(0) = theWidth_B(Node)
#                If theVDensity(Node, 0, 0) = 1 Then
#                    theVDensity(Node, 0, 0) = 0.9999
#                    Rip_Extinct(0) = 1
#                    Shade_Density(0) = 1
#                ElseIf theVDensity(Node, 0, 0) = 0 Then
#                    theVDensity(Node, 0, 0) = 0.00001
#                    Rip_Extinct(0) = 0
#                    Shade_Density(0) = 0
#                Else
#                    Rip_Extinct(0) = -Log(1 - theVDensity(Node, 0, 0)) / 10
#                    Shade_Density(0) = 1 - Exp(-Rip_Extinct(0) * Path(0))
#                End If
#                FLUX_Direct(4) = FLUX_Direct(4) * (1 - Shade_Density(0))
#                Path(0) = theVHeight(Node, 0, 0)
#                Rip_Extinct(0) = -Log(1 - theVDensity(Node, 0, 0)) / theVHeight(Node, 0, 0)
#                Shade_Density(0) = 1 - Exp(-Rip_Extinct(0) * Path(0))
#                FLUX_Diffuse(4) = FLUX_Diffuse(4) * (1 - Shade_Density(0))
#            End If
#            ':::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#            '5 - Entering Stream
#            If SolarZenith > 80 Then
#                Stream_Reflect = 0.0515 * (SolarZenith) - 3.636
#            Else
#                Stream_Reflect = 0.091 * (1 / Cos(SolarZenith * Pi / 180)) - 0.0386
#            End If
#            If Abs(Stream_Reflect) > 1 Then Stream_Reflect = 0.0515 * (SolarZenith * Pi / 180) - 3.636
#            If Abs(Stream_Reflect) > 1 Then Stream_Reflect = 0.091 * (1 / Cos(SolarZenith * Pi / 180)) - 0.0386
#            FLUX_Diffuse(5) = FLUX_Diffuse(4) * 0.91
#            FLUX_Direct(5) = FLUX_Direct(4) * (1 - Stream_Reflect)
#            ':::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#            '6 - Received by Water Column
#            '7 - Received by Bed
#            Dummy = Atn((Sin(SolarZenith * Pi / 180) / 1.3333) / Sqr(-(Sin(SolarZenith * Pi / 180) / 1.3333) * (Sin(SolarZenith * Pi / 180) / 1.3333) + 1))
#            Water_Path = theDepth(Node, 1) / Cos(Dummy) 'Jerlov (1976)
#            Trans_Stream = 0.415 - (0.194 * Log10(Water_Path * 100))
#            If Trans_Stream > 1 Then Trans_Stream = 1
#            Dummy1 = FLUX_Direct(5) * (1 - Trans_Stream)       'Direct Solar Radiation attenuated on way down
#            Dummy2 = FLUX_Direct(5) - Dummy1                   'Direct Solar Radiation Hitting Stream bed
#            Bed_Reflect = Exp(0.0214 * (SolarZenith * Pi / 180) - 1.941)   'Reflection Coef. for Direct Solar
#            BedRock = 1 - thePorosity
#            Dummy3 = Dummy2 * (1 - Bed_Reflect)                'Direct Solar Radiation Absorbed in Bed
#            Dummy4 = 0.53 * BedRock * Dummy3                   'Direct Solar Radiation Immediately Returned to Water Column as Heat
#            Dummy5 = Dummy2 * Bed_Reflect                      'Direct Solar Radiation Reflected off Bed
#            Dummy6 = Dummy5 * (1 - Trans_Stream)               'Direct Solar Radiation attenuated on way up
#            FLUX_Direct(6) = Dummy1 + Dummy4 + Dummy6
#            FLUX_Direct(7) = Dummy3 - Dummy4
#            Trans_Stream = 0.415 - (0.194 * Log10(100 * theDepth(Node, 1)))
#            If Trans_Stream > 1 Then Trans_Stream = 1
#            If Trans_Stream > 1 Then Trans_Stream = 1
#            Dummy1 = FLUX_Diffuse(5) * (1 - Trans_Stream)      'Diffuse Solar Radiation attenuated on way down
#            Dummy2 = FLUX_Diffuse(5) - Dummy1                  'Diffuse Solar Radiation Hitting Stream bed
#            Bed_Reflect = Exp(0.0214 * (0) - 1.941) 'Reflection Coef. for Diffuse Solar
#            Dummy3 = Dummy2 * (1 - Bed_Reflect)                'Diffuse Solar Radiation Absorbed in Bed
#            Dummy4 = 0.53 * BedRock * Dummy3                   'Diffuse Solar Radiation Immediately Returned to Water Column as Heat
#            Dummy5 = Dummy2 * Bed_Reflect                      'Diffuse Solar Radiation Reflected off Bed
#            Dummy6 = Dummy5 * (1 - Trans_Stream)               'Diffuse Solar Radiation attenuated on way up
#            FLUX_Diffuse(6) = Dummy1 + Dummy4 + Dummy6
#            FLUX_Diffuse(7) = Dummy3 - Dummy4
#        Else 'It is nighttime
#        End If
#            '   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
#            '       0 - Edge of atmosphere
#            '       1 - Above Topography
#            '       2 - Above Land Cover
#            '       3 - Above Stream (After Land Cover Shade)
#            '       4 - Above Stream (What a Solar Pathfinder Measures)
#            '       5 - Entering Stream
#            '       6 - Received by Water Column
#            '       7 - Received by Bed
#        Flux_Solar1 = FLUX_Diffuse(1) + FLUX_Direct(1)
#        Flux_Solar2 = FLUX_Diffuse(2) + FLUX_Direct(2)
#        Flux_Solar4 = FLUX_Diffuse(4) + FLUX_Direct(4)
#        Flux_Solar5 = FLUX_Diffuse(5) + FLUX_Direct(5)
#        Flux_Solar6 = FLUX_Diffuse(6) + FLUX_Direct(6)
#        Flux_Solar7 = FLUX_Diffuse(7) + FLUX_Direct(7)
#End Sub

