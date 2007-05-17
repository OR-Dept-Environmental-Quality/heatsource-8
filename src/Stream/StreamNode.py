from __future__ import division
import math, wx, bisect
import heatsource
from warnings import warn
from Dieties.Chronos import Chronos
from Dieties.IniParams import IniParams
from StreamChannel import StreamChannel
from Utils.Logger import Logger


class StreamNode(StreamChannel):
    """Definition of an individual stream segment"""
    def __init__(self, **kwargs):
        StreamChannel.__init__(self)
        # Define members in __slots__ to ensure that later member names cannot be added accidentally
        s = ["Embeddedness", "Conductivity", "ParticleSize", # From Morphology Data sheet
             "Latitude", "Longitude", "Elevation", # Geographic params
             "FLIR_Temp", "FLIR_Time", # FLIR data
             "T_cont", "T_sed", "T_in", "T_tribs", # Temperature attrs
             "VHeight", "VDensity", #Vegetation params
             "Wind", "Humidity", "T_air", # Continuous data
             "Zone", "T_bc", "C_bc", # Initialization parameters, Zonator and boundary conditions
             "Delta_T", # Current temperature calculated from only local fluxes
             "T", "T_prev", # Current and previous stream temperature
             "Flux", # Dictionary to hold heat flux values
             "Evap_Rate",  #Evaportion in m/s
             "TopoFactor", # was Topo_W+Topo_S+Topo_E/(90*3) in original code. From Above stream surface solar flux calculations
             "ShaderList" # List of angles and attributes to determine sun shading.
             ]
        # Set all the attributes to bare lists, or set from the constructor
        for attr in s:
            x = kwargs[attr] if attr in kwargs.keys() else None
            setattr(self, attr, x)
        self.slots += s
        for attr in ["Wind", "Humidity", "T_air", "T_tribs", "Q_tribs"]:
            setattr(self, attr, {})
        self.Flux = {"Direct":  [0]*8,
                     "Diffuse": [0]*8,
                     "Solar":   [0]*8,
                     "Solar_daily_sum": [0]*5}
        self.Log = Logger
        self.CalcSolarPosition = heatsource.CalcSolarPosition
        self.ShaderList = ()
        self.SampleDist = IniParams["transsample"]

    def __eq__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km == cmp
    def __ne__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km != cmp
    def __gt__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km > cmp
    def __lt__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km < cmp
    def __ge__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km >= cmp
    def __le__(self, other):
        cmp = other.km if isinstance(other, StreamNode) else other
        return self.km <= cmp
    def GetZones(self):
        return self.Zone
    def GetAttributes(self, zone=False):
        """Return a dictionary of all class attribute names and values

        This class returns a dictionary with keys that are the attribute name
        and values that are the current value for that attribute. All attributes
        in __slots__ and in self.slots (which hold the values for the StreamChannel)
        are included, including an optional breakdown of the values in the Zonator instance.

        If the argument zone is boolean True, then the values of the Zonator instance
        are given as well. The values in the Zonator are given differently named keys,
        in the form of X_Y_ATTR where X is the cardinal direction, clockwise from 0=NE to
        6=NW; Y is the zone number (0-4) and ATTR is the attribute name
        (e.g. VDensity). This dictionary can then be iterated over in a single
        call for printing. Internal dictionaries and lists are returned as objects
        and should be dealt with as such. (e.g. boundary conditions and such should
        be iterated over externally).
        """
        # Make a dictionary to return
        attrDict = {}
        ignoreList = ["Zone", "Chronos", "Helios", "IniParams", "Log"]
        # First we get all the attributes of __slots__
        for k in self.slots:
            if k in ignoreList: continue # Ignore the Zonator, clock, etc.
            try:
                attrDict[k] = getattr(self, k)
            except AttributeError:
                attrDict[k] = None
        if zone:
            for k, v in self.GetZoneAttributes().iteritems():
                attrDict[k] = v
        return attrDict
    def GetZoneAttributes(self):
        """Return a dictionary of key/value pairs for the internal Zonator instance.

        See GetAttributes() for details of the key format"""
        attrDict = {}
        # Expand the Zonator portion into the dictionary
        for i, j, zone in self.Zone:
            for attr in zone.__slots__:
                k = "%i_%i_%s" %(i, j, attr)
                attrDict[k] = getattr(zone, attr)
        return attrDict
    def Initialize(self):
        """Methods necessary to set initial conditions of the node"""
        self.SetBankfullMorphology()

    def CalcHydraulics(self, time, hour):
        # Convenience variables
        dt = self.dt
        dx = self.dx
        # Iterate down the stream channel, calculating the discharges
        self.CalculateDischarge(time, hour)
        if self.W_w > self.W_bf:
            if not IniParams["channelwidth"]:
                self.Log.write("Wetted width (%0.2f) at StreamNode %0.2f km exceeds bankfull width (%0.2f)" %(self.W_w, self.km, self.W_bf))
                msg = "The wetted width is exceeding the bankfull width at StreamNode km: %0.2f .  To accomodate flows, the BF X-area should be or greater. Select 'Yes' to continue the model run (and use calc. wetted widths) or select 'No' to stop this model run (suggested X-Area values will be recorded in Column Z in the Morphology Data worksheet)  Do you want to continue this model run?" % self.km
                dlg = wx.MessageDialog(None, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
                if dlg.ShowModal() == wx.ID_YES:
                    # Put this in a public place so we don't ask again.
                    IniParams["channelwidth"] = True
                else:    #Stop Model Run and Change Input Data
                    import sys
                    sys.exit(1)
                dlg.Destroy()
        ################################################################
        ### This section seems unused in the original code. It calculates a stratification
        # tendency factor. We can implement it (possibly in StreamChannel) if we need to
#        #===================================================
#        #Calculate tendency to stratify
#        try:
#            self.Froude_Densiometric = math.sqrt(1 / (9.8 * 0.000001)) * dx * self.Q / (self.d_w * self.A * self.dx)
#        except:
#            print self.d_w, self.A, self.dx
#            raise
#        #===================================================
#        else: #Skip Node - No Flow in Channel
#            self.Hyporheic_Exchange = 0
#            self.T = 0
#            self.Froude_Densiometric = 0

        #===================================================
        #Check to see if wetted widths exceed bankfull widths
        #TODO: This has to be reimplemented somehow, because Excel is involved
        # connected to the backend. Meaning this class has NO understanding of what the Excel
        # spreadsheet is. Thus, something must be propigated backward to the parent class
        # to fiddle with the spreadsheet. Perhaps we can write a report to a text file or
        # something. I'm very hesitant to connect this too tightly with the interface.

    def CalcHeat(self, time, hour,JD,JDC,offset):
        # Move our current temperature to T_prev before we calculate
        # our new temperature. This just ensures that T and T_prev are
        # known at this point as the current and future temperature.
#        self.T_prev = self.T
#        self.T = None # This just ensures we don't accidentally use it until it's reset
        DayTime = self.CalcSolarFlux(time, hour,JD,JDC,offset) # Returns false if night
        self.CalcConductionFlux()
        self.CalcLongwaveFlux(hour)
        self.CalcEvapConvFlux(hour)
        self.RecordHeatData(DayTime)
        self.MDispersion,self.MS1 = self.MacCormick1(hour)

    def CalcSolarFlux(self, time, hour, JD, JDC, offset):
        #Like the others, taken from VB code unless otherwise noted
        #TODO: This is a ridiculously long method. It should be cleaned up.
        #======================================================
        # Get the sun's altitude and azimuth:
        #All angles are in degrees
        Azimuth,Altitude,Zenith = self.CalcSolarPosition(self.Latitude, self.Longitude, time.hour, time.minute, time.second, offset, JDC)
#        raise Exception("break")
        AzimuthBreaks = [0,67.5,112.5,157.5,202.5,247.5,292.5]
        Direction = bisect.bisect(AzimuthBreaks,Azimuth)-1
        FullSunAngle, TopoShadeAngle, BankShadeAngle, RipExtinction, VegetationAngle = self.ShaderList[Direction]  #The angles are in degrees
        #print self.km, FullSunAngle, TopoShadeAngle, RipExtinction
        SampleDist = self.SampleDist
        Shade_Density = [0]*4
        # Helios calculates the julian date, so we lazily snag that calculation.
        # Make all math functions local to save time by preventing failed searches of local, class and global namespaces
        pi,exp,log10,log,sqrt = math.pi,math.exp,math.log10,math.log,math.sqrt
        sin,cos,tan,atan,radians = math.sin,math.cos,math.tan,math.atan,math.radians
        # If it's night, we get out quick.  TODO: would it save some run time to do this only once per night?
        if Altitude <= 0: #Nighttime
            Altitude = 0
            self.Flux["Direct"] = [0]*8
            self.Flux["Diffuse"] = [0]*8
            self.Flux["Solar"] = [0]*8
            if time.hour == 1: self.Flux["Solar_daily_sum"] = [0]*5   #reset for the new day
            return False #Nothing else to do, so ignore rest of method

        #############################################################
        #Route solar radiation to the stream surface
        #   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
        #       0 - Edge of atmosphere
        #       1 - Above Topography
        #       2 - Above Land Cover
        #       3 - Above Stream (After Land Cover Shade)
        #       4 - Above Stream (What a Solar Pathfinder Measures)
        #       5 - Entering Stream
        #       6 - Received by Water Column
        #       7 - Received by Bed
        ########################################################
        #======================================================
        # 0 - Edge of atmosphere
        # TODO: Original VB code's JulianDay calculation:
        # JulianDay = -DateDiff("d", theTime, DateSerial(year(theTime), 1, 1))
        # THis calculation for Rad_Vec should be checked, with respect to the DST hour/24 part.
#        Rad_Vec = 1 + 0.017 * cos((2 * pi / 365) * (186 - JD + time.hour / 24))
#        Solar_Constant = 1367 #W/m2
#        self.Flux["Direct"][0] = (Solar_Constant / (Rad_Vec ** 2)) * sin(radians(Altitude)) #Global Direct Solar Radiation
#        self.Flux["Diffuse"][0] = 0
#
#        #F_Direct, F_Diffuse = heatsource.CalcSolarFlux(JD,time.hour,Altitude,self.Elevation, self.C_bc[hour])
#
#        ########################################################
#        #======================================================
#        # 1 - Above Topography
#        Air_Mass = (35 / sqrt(1224 * sin(radians(Altitude)) + 1)) * \
#            exp(-0.0001184 * self.Elevation)
#        Trans_Air = 0.0685 * cos((2 * pi / 365) * (JD + 10)) + 0.8
#        #Calculate Diffuse Fraction
#        self.Flux["Direct"][1] = self.Flux["Direct"][0] * (Trans_Air ** Air_Mass) * (1 - 0.65 * self.C_bc[hour] ** 2)
#        if self.Flux["Direct"][0] == 0:
#            Clearness_Index = 1
#        else:
#            Clearness_Index = self.Flux["Direct"][1] / self.Flux["Direct"][0]
#
#        Dummy = self.Flux["Direct"][1]
#        Diffuse_Fraction = (0.938 + 1.071 * Clearness_Index) - \
#            (5.14 * (Clearness_Index ** 2)) + \
#            (2.98 * (Clearness_Index ** 3)) - \
#            (sin(2 * pi * (JD - 40) / 365)) * \
#            (0.009 - 0.078 * Clearness_Index)
#        self.Flux["Direct"][1] = Dummy * (1 - Diffuse_Fraction)
#        self.Flux["Diffuse"][1] = Dummy * (Diffuse_Fraction) * (1 - 0.65 * self.C_bc[hour] ** 2)

        F_Direct, F_Diffuse =  heatsource.CalcSolarFlux(JD,time.hour,Altitude,self.Elevation, self.C_bc[hour])
        self.Flux["Direct"][:2], self.Flux["Diffuse"][:2] = F_Direct, F_Diffuse
        ########################################################
        #======================================================
        #2 - Above Land Cover
        # Empty
        ########################################################
        #======================================================
        #3 - Above Stream Surface (Above Bank Shade)
#        if self.km == 0.15:
#            print time, Altitude, TopoShadeAngle, FullSunAngle, Direction
        if Altitude <= TopoShadeAngle:    #>Topographic Shade IS Occurring<
            self.Flux["Direct"][2] = 0
            self.Flux["Diffuse"][2] = self.Flux["Diffuse"][1] * self.TopoFactor
            self.Flux["Direct"][3] = 0
            self.Flux["Diffuse"][3] = self.Flux["Diffuse"][2] * self.ViewToSky
#            self.Flux["Direct"][4] = 0
#            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
        elif Altitude < FullSunAngle:  #Partial shade from veg
            self.Flux["Direct"][2] = self.Flux["Direct"][1]
            self.Flux["Diffuse"][2] = self.Flux["Diffuse"][1] * (1 - self.TopoFactor)
            Dummy1 = self.Flux["Direct"][2]
            zone = 0
            for vegangle in VegetationAngle:  #Loop to find if shading is occuring from veg. in that zone
                if Altitude < vegangle:  #veg shading is occurring from this zone
                    Dummy1 *= (1-(1-exp(-1* RipExtinction[zone] * (SampleDist/cos(radians(Altitude))))))
                zone += 1
            self.Flux["Direct"][3] = Dummy1
            self.Flux["Diffuse"][3] = self.Flux["Diffuse"][2] * self.ViewToSky
#            self.Flux["Direct"][4] = self.Flux["Direct"][3]
#            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
        else: # Full sun
            self.Flux["Direct"][2] = self.Flux["Direct"][1]
            self.Flux["Diffuse"][2] = self.Flux["Diffuse"][1] * (1 - self.TopoFactor)
            self.Flux["Direct"][3] = self.Flux["Direct"][2]
            self.Flux["Diffuse"][3] = self.Flux["Diffuse"][2] * self.ViewToSky
#            self.Flux["Direct"][4] = self.Flux["Direct"][3]
#            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
        #4 - Above Stream Surface (What a Solar Pathfinder measures)
        #Account for bank shade
        if Altitude > TopoShadeAngle and Altitude <= BankShadeAngle:  #Bank shade is occurring
            self.Flux["Direct"][4] = 0
            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
        else:  #bank shade is not occurring
            self.Flux["Direct"][4] = self.Flux["Direct"][3]
            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]

        #Account for emergent vegetation
        if IniParams["emergent"]:
            Path[0] = zone[0][0].VHeight / sin(radians(Altitude))
            if Path[0] > self.W_b:
                Path[0] = self.W_b
            if zone[0][0].VDensity == 1:
                zone[0][0].VDensity = 0.9999
                Rip_Extinct[0] = 1
                Shade_Density[0] = 1
            elif zone[0][0].VDensity == 0:
                zone[0][0].VDensity = 0.00001
                Rip_Extinct[0] = 0
                Shade_Density[0] = 0
            else:
                Rip_Extinct[0] = -log(1 - zone[0][0].VDensity) / 10
                Shade_Density[0] = 1 - exp(-Rip_Extinct[0] * Path[0])
            self.Flux["Direct"][4] = self.Flux["Direct"][4] * (1 - Shade_Density[0])
            Path[0] = zone[0][0].VHeight
            Rip_Extinct[0] = -log(1 - zone[0][0].VDensity) / zone[0][0].VHeight
            Shade_Density[0] = 1 - exp(-Rip_Extinct[0] * Path[0])
            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][4] * (1 - Shade_Density[0])

#        raise Exception("Debug Breakpoint")
        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #5 - Entering Stream
#        Zenith = 90 - Altitude
        if Zenith > 80:
            Stream_Reflect = 0.0515 * (Zenith) - 3.636
        else:
            Stream_Reflect = 0.091 * (1 / cos(Zenith * pi / 180)) - 0.0386
        if abs(Stream_Reflect) > 1:
            Stream_Reflect = 0.0515 * (Zenith * pi / 180) - 3.636
        if abs(Stream_Reflect) > 1:
            Stream_Reflect = 0.091 * (1 / self.cos(Zenith * pi / 180)) - 0.0386
        self.Flux["Diffuse"][5] = self.Flux["Diffuse"][4] * 0.91
        self.Flux["Direct"][5] = self.Flux["Direct"][4] * (1 - Stream_Reflect)
        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #6 - Received by Water Column
        #=========================================================

        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        #7 - Received by Bed
        Water_Path = self.d_w / cos(atan((sin(radians(Zenith)) / 1.3333) / sqrt(-(sin(radians(Zenith)) / 1.3333) * (sin(radians(Zenith)) / 1.3333) + 1)))         #Jerlov (1976)
        Trans_Stream = 0.415 - (0.194 * log10(Water_Path * 100))
        if Trans_Stream > 1:
            Trans_Stream = 1
        Dummy1 = self.Flux["Direct"][5] * (1 - Trans_Stream)       #Direct Solar Radiation attenuated on way down
        Dummy2 = self.Flux["Direct"][5] - Dummy1                   #Direct Solar Radiation Hitting Stream bed
        Bed_Reflect = exp(0.0214 * (Zenith * pi / 180) - 1.941)   #Reflection Coef. for Direct Solar
        BedRock = 1 - self.phi
        Dummy3 = Dummy2 * (1 - Bed_Reflect)                #Direct Solar Radiation Absorbed in Bed
        Dummy4 = 0.53 * BedRock * Dummy3                   #Direct Solar Radiation Immediately Returned to Water Column as Heat
        Dummy5 = Dummy2 * Bed_Reflect                      #Direct Solar Radiation Reflected off Bed
        Dummy6 = Dummy5 * (1 - Trans_Stream)               #Direct Solar Radiation attenuated on way up
        self.Flux["Direct"][6] = Dummy1 + Dummy4 + Dummy6
        self.Flux["Direct"][7] = Dummy3 - Dummy4
        Trans_Stream = 0.415 - (0.194 * log10(100 * self.d_w))
        if Trans_Stream > 1:
            Trans_Stream = 1
        Dummy1 = self.Flux["Diffuse"][5] * (1 - Trans_Stream)      #Diffuse Solar Radiation attenuated on way down
        Dummy2 = self.Flux["Diffuse"][5] - Dummy1                  #Diffuse Solar Radiation Hitting Stream bed
        Bed_Reflect = exp(0.0214 * (0) - 1.941)               #Reflection Coef. for Diffuse Solar
        Dummy3 = Dummy2 * (1 - Bed_Reflect)                #Diffuse Solar Radiation Absorbed in Bed
        Dummy4 = 0.53 * BedRock * Dummy3                   #Diffuse Solar Radiation Immediately Returned to Water Column as Heat
        Dummy5 = Dummy2 * Bed_Reflect                      #Diffuse Solar Radiation Reflected off Bed
        Dummy6 = Dummy5 * (1 - Trans_Stream)               #Diffuse Solar Radiation attenuated on way up
        self.Flux["Diffuse"][6] = Dummy1 + Dummy4 + Dummy6
        self.Flux["Diffuse"][7] = Dummy3 - Dummy4
        #=========================================================

#        '   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
#        '       0 - Edge of atmosphere
#        '       1 - Above Topography
#        '       2 - Above Land Cover
#        '       3 - Above Stream (After Land Cover Shade)
#        '       4 - Above Stream (What a Solar Pathfinder Measures)
#        '       5 - Entering Stream
#        '       6 - Received by Water Column
#        '       7 - Received by Bed
        self.Flux["Solar"][1] = self.Flux["Diffuse"][1] + self.Flux["Direct"][1]
        self.Flux["Solar"][2] = self.Flux["Diffuse"][2] + self.Flux["Direct"][2]
        self.Flux["Solar"][4] = self.Flux["Diffuse"][4] + self.Flux["Direct"][4]
        self.Flux["Solar"][5] = self.Flux["Diffuse"][5] + self.Flux["Direct"][5]
        self.Flux["Solar"][6] = self.Flux["Diffuse"][6] + self.Flux["Direct"][6]
        self.Flux["Solar"][7] = self.Flux["Diffuse"][7] + self.Flux["Direct"][7]
        self.Flux["Solar_daily_sum"][1] += self.Flux["Solar"][1]
        self.Flux["Solar_daily_sum"][4] += self.Flux["Solar"][4]


        return True

    def CalcConductionFlux(self):
        #======================================================
        #Calculate Bed Conduction FLUX
        #and hyporheic exchange temperature change
        #======================================================
        #Variables used in bed conduction
        #Substrate Conduction Constants
        Sed_Density = 1600 #kg/m3
        Sed_ThermalDiffuse = 4.5e-6 #m2/s
        Sed_HeatCapacity = 2219 #J/(kg *C)
        #======================================================
        #Variables used in bed conduction
        #Water Conduction Constants
        H2O_Density = 1000 #kg/m3
        H2O_ThermalDiffuse = 14.331e-8 #m2/s
        H2O_HeatCapacity = 4187 #J/(kg *C)
        #======================================================
        #Variables used in bed conduction
        #Calculate the sediment depth (conduction layer)
        Sed_Depth = 10 * self.ParticleSize / 1000
        if Sed_Depth > 1: Sed_Depth = 1
        if Sed_Depth < 0.1: Sed_Depth = 0.1
        #Sed_Depth = 0.2
        #======================================================
        #Variables used in bed conduction
        #Calculate Volumetric Ratio of Water and Substrate
        #Use this Ratio to Estimate Conduction Constants
        Volume_Sediment = (1 - self.phi) * self.P_w * Sed_Depth * self.dx
        Volume_H2O = self.phi * self.P_w * Sed_Depth * self.dx
        Volume_Hyp = self.P_w * Sed_Depth * self.dx
        Ratio_Sediment = Volume_Sediment / Volume_Hyp
        Ratio_H2O = Volume_H2O / Volume_Hyp
        Density = (Sed_Density * Ratio_Sediment) + (H2O_Density * Ratio_H2O)
        HeatCapacity = (Sed_HeatCapacity * Ratio_Sediment) + (H2O_HeatCapacity * Ratio_H2O)
        ThermalDiffuse = (Sed_ThermalDiffuse * Ratio_Sediment) + (H2O_ThermalDiffuse * Ratio_H2O)
        #======================================================
        #Calculate the conduction flux between water column & substrate
        self.Flux["Conduction"] = ThermalDiffuse * Density * HeatCapacity * (self.T_sed - self.T_prev) / (Sed_Depth / 2)
        #Calculate the conduction flux between deeper alluvium & substrate
        # TODO: Figure out when this is necessary or desirable
##        If Sheet2.Range("IV21").Value = 1 Then
##            Flux_Conduction_Alluvium = ThermalDiffuse * Density * HeatCapacity * (Temp_Sed(Node) - Sheet2.Range("IV20").Value) / (Sed_Depth / 2)
##        Else
        Flux_Conduction_Alluvium = 0
        #======================================================
        #Calculate the changes in temperature in the substrate conduction layer
        #Temperature change in substrate from solar exposure and conducted heat
        NetHeat_Sed = self.Flux["Solar"][7] - self.Flux["Conduction"] - Flux_Conduction_Alluvium
        DT_Sed = NetHeat_Sed * self.P_w * self.dx * self.dt / (Volume_Hyp * Density * HeatCapacity)
        #======================================================
        #Calculate the temperature of the substrate conduction layer
        self.T_sed = self.T_sed + DT_Sed
#
    def CalcLongwaveFlux(self, hour):
        #=====================================================
        #Calculate Longwave FLUX
        #======================================================
        #Atmospheric variables
        exp = math.exp
        time = Chronos.TheTime
        Humidity = self.Humidity[hour]
        Air_T = self.T_air[hour]
        Pressure = 1013 - 0.1055 * self.Elevation #mbar
        Sat_Vapor = 6.1275 * exp(17.27 * Air_T / (237.3 + Air_T)) #mbar (Chapra p. 567)
        Air_Vapor = self.Humidity[hour] * Sat_Vapor
        Sigma = 5.67e-8 #Stefan-Boltzmann constant (W/m2 K4)
        Emissivity = 1.72 * (((Air_Vapor * 0.1) / (273.2 + Air_T)) ** (1 / 7)) * (1 + 0.22 * self.C_bc[hour] ** 2) #Dingman p 282
        #======================================================
        #Calcualte the atmospheric longwave flux
        self.Flux["LW_Atm"] = 0.96 * self.ViewToSky * Emissivity * Sigma * (Air_T + 273.2) ** 4
        #Calcualte the backradiation longwave flux
        self.Flux["LW_Stream"] = -0.96 * Sigma * (self.T_prev + 273.2) ** 4
        #Calcualte the vegetation longwave flux
        self.Flux["LW_Veg"] = 0.96 * (1 - self.ViewToSky) * 0.96 * Sigma * (Air_T + 273.2) ** 4
        #Calcualte the net longwave flux
        self.Flux["Longwave"] = self.Flux["LW_Atm"] + self.Flux["LW_Stream"] + self.Flux["LW_Veg"]

    def CalcEvapConvFlux(self, hour):
        #===================================================
        #Calculate Evaporation FLUX
        #===================================================
        #Atmospheric Variables
        log,exp = math.log,math.exp
        time = Chronos.TheTime
        Wind = self.Wind[hour]
        Air_T = self.T_air[hour]
        Humidity = self.Humidity[hour]
        Pressure = 1013 - 0.1055 * self.Elevation #mbar
        Sat_Vapor = 6.1275 * exp(17.27 * self.T_prev / (237.3 + self.T_prev)) #mbar (Chapra p. 567)
        Air_Vapor = self.Humidity[hour] * Sat_Vapor
        #===================================================
        #Calculate the frictional reduction in wind velocity
        if IniParams["emergent"] and self.VHeight > 0:
            Zd = 0.7 * self.Zone[0][0].VHeight
            Zo = 0.1 * self.Zone[0][0].VHeight
            Zm = 2
            Friction_Velocity = Wind * 0.4 / Log((Zm - Zd) / Zo) #Vertical Wind Decay Rate (Dingman p. 594)
        else:
            Zo = 0.00023 #Brustsaert (1982) p. 277 Dingman
            Zd = 0 #Brustsaert (1982) p. 277 Dingman
            Zm = 2
            Friction_Velocity = Wind
        #===================================================
        #Wind Function f(w)
        Wind_Function = IniParams["wind_a"] + IniParams["wind_b"] * Friction_Velocity #m/mbar/s
        #===================================================
        #Latent Heat of Vaporization
        LHV = 1000 * (2501.4 + (1.83 * self.T_prev)) #J/kg
        #===================================================
        #Use Jobson Wind Function
        if IniParams["penman"]:
            #Calculate Evaporation FLUX
            P = 998.2 # kg/m3
            Gamma = 1003.5 * Pressure / (LHV * 0.62198) #mb/*C  Cuenca p 141
            Delta = 6.1275 * exp(17.27 * Air_T / (237.3 + Air_T)) - 6.1275 * exp(17.27 * (Air_T - 1) / (237.3 + Air_T - 1))
            NetRadiation = self.Flux["Solar"][5] + self.Flux["Longwave"]  #J/m2/s
            if NetRadiation < 0:
                NetRadiation = 0 #J/m2/s
            Ea = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
            self.Evap_Rate = ((NetRadiation * Delta / (P * LHV)) + Ea * Gamma) / (Delta + Gamma)
            self.Flux["Evaporation"] = -self.Evap_Rate * LHV * P #W/m2
            #Calculate Convection FLUX
            Bowen = Gamma * (self.T_prev - Air_T) / (Sat_Vapor - Air_Vapor)
            self.Flux["Convection"] = self.Flux["Evaporation"] * Bowen
        else:
            #===================================================
            #Calculate Evaporation FLUX
            self.Evap_Rate = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
            P = 998.2 # kg/m3
            self.Flux["Evaporation"] = -self.Evap_Rate * LHV * P #W/m2
            #Calculate Convection FLUX
            if (Sat_Vapor - Air_Vapor) <> 0:
                Bowen = 0.61 * (Pressure / 1000) * (self.T_prev - Air_T) / (Sat_Vapor - Air_Vapor)
            else:
                Bowen = 1
            self.Flux["Convection"] = self.Flux["Evaporation"] * Bowen

    def RecordHeatData(self,DayTime):
        dt = self.dt
        Heat = {"Solar": [0]*8}
#        if DayTime:
        self.Flux["Total"] = self.Flux["Solar"][6] + self.Flux["Conduction"] + self.Flux["Evaporation"] + self.Flux["Convection"] + self.Flux["Longwave"]
        Cp = 4182 # J/kg *C
        P = 998.2 # kgS/m3
        ave = self.A / self.W_w #TODO: include in above calcuation.
        self.Delta_T = self.Flux["Total"] * dt / (ave * Cp * P)

#        if self.km == 3.05:
#            print self.Delta_T, self.Flux["Total"], dt, ave, Cp, P
#        else:
#            self.Flux["Total"] = 0
#            self.Flux["Conduction"] = 0
#            self.Flux["Evaporation"] = 0
#            self.Flux["Convection"] = 0
#            self.Flux["Longwave"] = 0
#            self.Delta_T = 0
#            self.Flux["Solar"][1] = 0
#            self.Flux["Solar"][4] = 0
#            self.Flux["Solar"][6] = 0
#            self.E = 0

        if False:#Chronos.TheTime > Chronos.start:
            #Calculate Heat by process (J/m2 per day)
            Heat["Solar"][1] = Heat["Solar"][1] + dt * self.Flux["Solar"][1]
            Heat["Solar"][2] = Heat["Solar"][2] + dt * self.Flux["Solar"][2]
            Heat["Solar"][4] = Heat["Solar"][4] + dt * self.Flux["Solar"][4]
            Heat["Solar"][6] = Heat["Solar"][6] + dt * self.Flux["Solar"][6]
            Heat["Conduction"] = dt * self.Flux["Conduction"]
            Heat["Longwave"] = dt * self.Flux["Longwave"]
            Heat["LW_Atm"] = dt * self.Flux["LW_Atm"]
            Heat["LW_LC"] = dt * self.Flux["LW_Veg"]
            Heat["LW_BR"] = dt * self.Flux["LW_Stream"]
            Heat["Evaporation"] = dt * self.Flux["Evaporation"]
            Heat["Convection"] = dt * self.Flux["Convection"]
            Heat["Total"] = dt * self.Flux["Total"]


    def MacCormick1(self, hour):
        sqrt = math.sqrt
        dt = self.dt
        dx = self.dx
        Dispersion = 0
        S1 = 0
        SkipNode = False
        if self.prev_km:
            if not SkipNode:
                mix = self.MixItUp(hour,0)
                T0 = self.prev_km.T_prev + mix
                T1 = self.T_prev
                T2 = self.next_km.T_prev if self.next_km else self.T_prev
                if not self.S:
                    Shear_Velocity = self.U
                else:
                    Shear_Velocity = sqrt(9.8 * self.d_w * self.S)
                Dispersion = 0.011 * (self.U ** 2) * (self.W_w ** 2) / (self.d_w * Shear_Velocity)
                if Dispersion * dt / (dx ** 2) > 0.5:
                    Dispersion = (0.45 * (dx ** 2)) / dt
                    print self.km, Dispersion
                Dummy1 = -self.U * (T1 - T0) / dx
                Dummy2 = Dispersion * (T2 - 2 * T1 + T0) / (dx ** 2)
                S1 = Dummy1 + Dummy2 + self.Delta_T / dt
                self.T = T1 + S1 * dt
#                if self.km == 3.05:
#                    print Chronos.TheTime, "M1", T0, T1, T2, Dummy1, Dummy2, S1, dt, self.Delta_T, self.T
            else:
                self.T = self.T_prev #TODO: This is wrong, really should be self.T_prev_prev
        else:
            self.T = self.T_bc[hour]
            self.T_prev = self.T_bc[hour] #I think this is what the VB code does
        return Dispersion,S1

    def MacCormick2(self, hour):
        sqrt = math.sqrt
        Dispersion = self.MDispersion
        S1 = self.MS1
        dt = self.dt
        dx = self.dx
        SkipNode = False
        #===================================================
        #Set control temps
        if self.T_cont:
            self.T = self.T_cont
            return
        #===================================================
        if self.prev_km:
            if not SkipNode:
                mix = self.MixItUp(hour, 1)
                T0 = self.prev_km.T + mix
                T1 = self.T
                T2 = self.next_km.T if self.next_km else self.T
                #======================================================
                #Final MacCormick Finite Difference Calc.
                #===================================================
                Dummy1 = -self.U * (T1 - T0) / dx
                Dummy2 = Dispersion * (T2 - 2 * T1 + T0) / dx ** 2
                S2 = Dummy1 + Dummy2 + self.Delta_T / dt
                self.T = self.T_prev + ((S1 + S2) / 2) * dt
            else:
                self.T = self.T_prev
        if self.T > 50 or self.T < 0:
            raise Exception("Unstable model")

    def MixItUp(self, hour, timestep=0):
        time = Chronos.TheTime
        if self.Q:
            Q_up = self.prev_km.Q if timestep else self.prev_km.Q_prev
            T_up = self.prev_km.T if timestep else self.prev_km.T_prev
        else:
            Q_up = 0
        if Q_up:
            # Get any point-source inflow data
            try:
                Q_in = self.Q_tribs[hour]
                T_in = self.T_tribs[hour]
            except KeyError:
                Q_in = 0
                T_in = 0
            # Hyporheic flows if available
            Q_hyp = self.Q_hyp or 0
            # And accretionary flows
            Q_accr = self.Q_in or 0
            T_accr = self.T_in or 0
            #Calculate temperature change from mass transfer from point inflows
            T_mix = ((Q_in * T_in) + (T_up * Q_up)) / (Q_up + Q_in)
            #Calculate temperature change from mass transfer from hyporheic zone
            T_mix = ((self.T_sed * Q_hyp) + (T_mix * (Q_up + Q_in))) / (Q_hyp + Q_up + Q_in)
            #Calculate temperature change from accretion inflows
            T_mix = ((Q_accr * T_accr) + (T_mix * (Q_up + Q_in + Q_hyp))) / (Q_accr + Q_up + Q_in + Q_hyp)
            return T_mix - T_up
        else:
            return 0
