from __future__ import division
import math,wx
from warnings import warn
from scipy.optimize.minpack import newton
from Containers.IniParams import IniParams
from Containers.VegZone import VegZone
from Containers.Zonator import Zonator
from Containers.BoundCond import BoundCond
from Containers.AttrList import TimeList
from Utils.Maths import NewtonRaphson
from StreamChannel import StreamChannel
from Solar.Helios import Helios
from Time.Chronos import Chronos

class StreamNode(StreamChannel):
    """Definition of an individual stream segment"""
    # Define members in __slots__ to ensure that later member names cannot be added accidentally
    __slots__ = ["Embeddedness","Conductivity","ParticleSize","Porosity",  # From Morphology Data sheet
                 "Topo","Latitude","Longitude","Elevation", # Geographic params
                 "FLIR_Temp","FLIR_Time", # FLIR data
                 "T_cont","T_sed","T_in","T_tribs", # Temperature attrs
                 "VHeight","VDensity",  #Vegetation params
                 "Wind","Humidity","T_air","T_stream" # Continuous data
                 "IniParams","Zone","BC", # Initialization parameters, Zonator and boundary conditions
                 "Flux",
                 "Helios" # Singleton class for Solar Insolation
                 ]
    def __init__(self, **kwargs):
        StreamChannel.__init__(self)
        # Set all the attributes to bare lists, or set from the constructor
        for attr in self.__slots__:
            x = kwargs[attr] if attr in kwargs.keys() else None
            setattr(self,attr,x)
        for attr in ["Wind","Humidity","T_air","T_tribs","Q_tribs","T_stream"]:
            setattr(self,attr,TimeList())
        self.IniParams = IniParams.getInstance()
        self.BC = BoundCond.getInstance() # Class to hold various boundary conditions
        # Set discharge boundary conditions for the StreamChannel
        self.Q_bc = self.BC.Q
        self.Flux = {"Direct": [0]*8,
                     "Diffuse": [0]*8,
                     "Solar": [0]*8}
        self.Topo = {"E": None,
                     "S": None,
                     "W": None}
        self.Chronos = Chronos.getInstance()
        self.Helios = Helios.getInstance()
        # This is a Zonator instance, with 7 directions, each of which holds 5 VegZone instances
        # with values for the sampled zones in each directions. We build a blank Zonator
        # here so that the HeatSourceInterface.BuildStreamNode() method can add values without
        # needing to build anything
        dir = [] # List to save the seven directions
        for Direction in xrange(7):
            z = () #Tuple to store the zones 0-4
            for Zone in xrange(5):
                z += VegZone(),
            dir.append(z) # append to the proper direction
        self.Zone = Zonator(*dir) # Create a Zonator instance and set the node.Zone attribute

    def __eq__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km == cmp
    def __ne__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km != cmp
    def __gt__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km > cmp
    def __lt__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km < cmp
    def __ge__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km >= cmp
    def __le__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km <= cmp
    def GetZones(self):
        return self.Zone
    def Initialize(self):
        """Methods necessary to set initial conditions of the node"""
        self.ViewToSky()
        self.SetBankfullMorphology()

    def CalcHydraulics(self):
        # Convenience variables
        dt = self.dt
        dx = self.dx
        # Iterate down the stream channel, calculating the discharges
        self.CalculateDischarge()

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
        Flag_StoptheModel = False
        if self.W_w > self.W_bf and not self.IniParams.ChannelWidth:

            I = self.km - dx / 1000
            II = self.km
            msg = "The wetted width is exceeding the bankfull width at StreamNode km: %0.2f .  To accomodate flows, the BF X-area should be or greater. Select 'Yes' to continue the model run (and use calc. wetted widths) or select 'No' to stop this model run (suggested X-Area values will be recorded in Column Z in the Morphology Data worksheet)  Do you want to continue this model run?" % self.km
            dlg = wx.MessageDialog(None, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_OK:
                # Put this in a public place so we don't ask again.
                self.IniParams.Flag_ChannelWidth = True
                Flag_StoptheModel = False
            else:    #Stop Model Run and Change Input Data
                Flag_StoptheModel = True
                self.IniParams.ChannelWidth = True
            dlg.Destroy()
#        if Flag_StoptheModel:
#            I = 0
#            while self[(17 + I, 5),"Morphology Data"] < self.km
#                I += 1
#            Dummy = self[17, 5) - Sheet1.Cells(18, 5)
#            For II = I - CInt(dx / (Dummy * 1000)) To I
#                If II >= 0 Then Sheet1.Cells(17 + II, 26) = Round(AreaX(Node, 1) + 0.1, 2)
#            Next II
    def ViewToSky(self):
        #TODO: This method needs to be tested against the values obtained by the VB code
        #======================================================
        #Calculate View to Sky
        VTS_Total = 0
        for D in xrange(7): # Direction
            LC_Angle_Max = 0
            for Z in xrange(1,5): # Zone
                if Z == 1:
                    OH = self.Zone[D][Z].Overhang
                else:
                    OH = 0
                Dummy1 = self.Zone[D][Z].VHeight + self.Zone[D][Z].SlopeHeight
                Dummy2 = self.IniParams.TransSample * (Z - 0.5) - OH
                if Dummy2 <= 0:
                    Dummy2 = 0.0001
                LC_Angle = (180 / math.pi) * math.atan(Dummy1 / Dummy2) * self.Zone[D][Z].VDensity
                if Z == 1:
                    LC_Angle_Max = LC_Angle
                if LC_Angle_Max < LC_Angle:
                    LC_Angle_Max = LC_Angle
            VTS_Total = VTS_Total + LC_Angle_Max
        self.View_To_Sky = (1 - VTS_Total / (7 * 90))

    def CalcSolarPosition(self):
        #Like the others, taken from VB code unless otherwise noted
        #======================================================
        # Get the sun's altitude and azimuth:
        Altitude, Azimuth = self.Helios.CalcSolarPosition(self.Latitude, self.Longitude)
        # Helios calculates the julian date, so we lazily snag that calculation.
        JD = self.Helios.JD
        # If it's night, we get out quick.
        if Altitude <= 0: #Nighttime
            Altitude = 0
            self.Flux["Direct"] = [0]*8
            self.Flux["Diffuse"] = [0]*8
            self.Flux["Solar"] = [0]*8
            return #Nothing else to do, so ignore rest of method
        #######################################
        #   Solar_Constant = kj/m2*hr
        #   Air_Mass = Optical air mass thickness
        #   Trans_Air = Transmissivity of air mass
        #   Clearness_Index = deminsionless ratio
        #   Diffuse_Fraction = Fraction of solar that is diffuse
        #======================================================
        #======================================================
        #Set Directional Land Cover Types & Calculate Riparian Boundaries
        #   LC_TotElev() = Riparian height above stream (meters)
        #   LC_Distance = Distance from stream node to veg (meters)
        #   LC_Elev = Elevation at each land cover sample point
        #   LC_ElevDiff = Elevation differance btwn land cover sample point and stream
        #Set Directional Topo Shade
        #   Topo_Alt = Topo shade angle (rad)
        #======================================================
        if Azimuth <= 67.5: #NE Direction
            Direction = 1
            Topo_Alt = self.Topo['E']
        elif Azimuth > 67.5 and Azimuth <= 112.5: #E Direction
            Direction = 2
            Topo_Alt = self.Topo['E']
        elif Azimuth > 112.5 and Azimuth <= 157.5: #SE Direction
            Direction = 3
            Topo_Alt = 0.5 * (self.Topo['E'] + self.Topo['S'])
        elif Azimuth > 157.5 and Azimuth <= 202.5: #S Direction
            Direction = 4
            Topo_Alt = self.Topo['S']
        elif Azimuth > 202.5 and Azimuth <= 247.5: #SW Direction
            Direction = 5
            Topo_Alt = 0.5 * (self.Topo['W'] + self.Topo['S'])
        elif Azimuth > 247.5 and Azimuth <= 292.5: #W Direction
            Direction = 6
            Topo_Alt = self.Topo['W']
        else: #NW Direction
            Direction = 7
            Topo_Alt = self.Topo['W']
        #======================================================
        #Calculate Land Cover Horizontal Spacing
        #TODO: Figure out the purpose of this and correct it.
#        for i,j,Zone in zonator:
#            if i == 0: continue
#            self.LC_TotElev = theVHeight(Node, Zone, Direction) + theSlopeHeight(Node, Zone, Direction)
#            if Zone == 1:
#                self.LC_Distance = self.IniParams.TransSample * (Zone - 0.5) - theOverHang(Node, Direction)
#            else
#                self.LC_Distance = self.IniParams.TransSample * (Zone - 0.5)
#            if self.LC_Distance < 0:
#                self.LC_Distance = 0.00001
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
        self.CalcFlux0()

    def CalcFlux0(self):
        #======================================================
        # 0 - Edge of atmosphere
        # TODO: Original VB code's JulianDay calculation:
        # JulianDay = -DateDiff("d", theTime, DateSerial(year(theTime), 1, 1))
        # THis calculation for Rad_Vec should be checked, with respect to the DST hour/24 part.
        self.Chronos.TheTime
        Rad_Vec = 1 + 0.017 * math.cos((2 * math.pi / 365) * (186 - JD + Hour_DST / 24))
        Solar_Constant = 1367 #W/m2
        self.Flux["Direct"][0] = (Solar_Constant / (Rad_Vec ** 2)) * math.sin(Altitude * math.pi / 180) #Global Direct Solar Radiation
        self.Flux["Diffuse"][0] = 0
#    def CalcFlux1(self):
#        #======================================================
#        # 1 - Above Topography
#        Dummy1 = 35 / math.sqrt(1224 * math.sin(Altitude * math.pi / 180) + 1)
#        Air_Mass = Dummy1 * math.exp(-0.0001184 * zonator[0][1].Elevation)
#        Trans_Air = 0.0685 * math.cos((2 * math.pi / 365) * (JulianDay + 10)) + 0.8
#        #Calculate Diffuse Fraction
#        self.Flux["Direct"][1] = self.Flux["Direct"][0] * (Trans_Air ** Air_Mass) * (1 - 0.65 * self.Cloudiness[time,-1] ** 2)
#        if self.Flux["Direct"][0] == 0:
#            Clearness_Index = 1
#        else:
#            Clearness_Index = self.Flux["Direct"][1] / self.Flux["Direct"][0]
#        Dummy = self.Flux["Direct"][1]
#        Dummy1 = 0.938 + 1.071 * Clearness_Index
#        Dummy2 = 5.14 * (Clearness_Index ** 2)
#        Dummy3 = 2.98 * (Clearness_Index ** 3)
#        Dummy4 = math.sin(2 * math.pi * (JulianDay - 40) / 365)
#        Dummy5 = (0.009 - 0.078 * Clearness_Index)
#        Diffuse_Fraction = Dummy1 - Dummy2 + Dummy3 - Dummy4 * Dummy5
#        self.Flux["Direct"][1] = Dummy * (1 - Diffuse_Fraction)
#        self.Flux["Diffuse"][1] = Dummy * (Diffuse_Fraction) * (1 - 0.65 * self.Cloudiness[time,-1] ** 2)
#    def CalcFlux2(self):
#        #======================================================
#        #2 - Above Land Cover
#        pass
#    def CalcFlux3(self):
#        #3 - Above Stream Surface (Above Bank Shade)
#        if Altitude <= Topo_Alt:    #>Topographic Shade IS Occurring<
#            Flag_Topo = 1
#            self.Flux["Direct"][2] = 0
#            self.Flux["Diffuse"][2] = self.Flux["Diffuse"][1] * (self.Topo["E"] + self.Topo["S"] + self.Topo["E"]) / (90 * 3)
#            self.Flux["Direct"][3] = 0
#            self.Flux["Diffuse"][3] = self.Flux["Diffuse"][2] * self.View_To_Sky
#        else:  #>Topographic Shade is NOT Occurring<
#            self.Flux["Direct"][2] = self.Flux["Direct"][1]
#            self.Flux["Diffuse"][2] = self.Flux["Diffuse"][1] * (1 - (self.Topo["W"] + self.Topo["S"] + self.Topo["E"]) / (90 * 3))
#            Dummy1 = self.Flux["Direct"][2]
#            for i,j,Zone in zonator:# = 4 To 1 Step -1 #Calculate shade density and self.Flux["Direct"][3]
#                if i != Direction: continue
#                LC_ShadowLength = (zone[Direction][j].VHeight + zone[Direction][j].SlopeHeight) / math.tan(Altitude * math.pi / 180) #Vegetation Shadow Casting
#                if LC_ShadowLength >= LC_Distance: #Veg Shade IS Occurring
#                    Path(Zone) = Dx_lc / math.cos(Altitude * math.pi / 180)
#                    if zone[Direction][j].VDensity == 1:
#                        Rip_Extinct(Zone) = 1
#                        Shade_Density(Zone) = 1
#                    else:
#                        Rip_Extinct(Zone) = -Log(1 - zone[Direction][j].VDensity) / 10
#                        Shade_Density(Zone) = 1 - Exp(-Rip_Extinct(Zone) * Path(Zone))
#                else: #Veg Shade IS NOT Occurring
#                    Shade_Density(Zone) = 0
#                Dummy1 = Dummy1 * (1 - Shade_Density(Zone))
#            self.Flux["Direct"][3] = Dummy1
#            self.Flux["Diffuse"][3] = self.Flux["Diffuse"][2] * self.View_To_Sky
#    def CalcFlux4(self):
#        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#        #4 - Above Stream Surface (What a Solar Pathfinder measures)
#        #Account for bank shade
#        if Flag_Topo == 0:
#            for Zone = 4 To 1 Step -1 #Calculate bank shade and self.Flux["Direct"][4]
#                DEM_ShadowLength = zone[Direction][j].SlopeHeight / math.tan(Altitude * math.pi / 180) #Bank Shadow Casting
#                if DEM_ShadowLength >= self.LC_Distance: #Bank Shade is Occurring
#                    self.Flux["Direct"][4] = 0
#                    self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
#                else:
#                    self.Flux["Direct"][4] = self.Flux["Direct"][3]
#                    self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
#        else:
#            self.Flux["Direct"][4] = 0
#            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][3]
#        #Account for emergent vegetation
#        if Flag_Emergent == 1:
#            Path(0) = zone[Direction][j].VHeight / Sin(Altitude * math.pi / 180)
#            if Path(0) > Width_B(Node):
#                Path(0) = theWidth_B(Node)
#            if zone[0][0].VDensity = 1 Then
#                zone[0][0].VDensity = 0.9999
#                Rip_Extinct(0) = 1
#                Shade_Density(0) = 1
#            elif zone[0][0].VDensity = 0 Then
#                zone[0][0].VDensity = 0.00001
#                Rip_Extinct(0) = 0
#                Shade_Density(0) = 0
#            else:
#                Rip_Extinct(0) = -Log(1 - zone[0][0].VDensity) / 10
#                Shade_Density(0) = 1 - Exp(-Rip_Extinct(0) * Path(0))
#            self.Flux["Direct"][4] = self.Flux["Direct"][4] * (1 - Shade_Density(0))
#            Path(0) = zone[0][0].VHeight
#            Rip_Extinct(0) = -Log(1 - zone[0][0].VDensity) / zone[0][0].VHeight
#            Shade_Density(0) = 1 - Exp(-Rip_Extinct(0) * Path(0))
#            self.Flux["Diffuse"][4] = self.Flux["Diffuse"][4] * (1 - Shade_Density(0))
#    def CalcFlux5(self):
#        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#        #5 - Entering Stream
#        if self.Solar.Zenith > 80:
#            Stream_Reflect = 0.0515 * (self.Solar.Zenith) - 3.636
#        else:
#            Stream_Reflect = 0.091 * (1 / math.cos(self.Solar.Zenith * math.pi / 180)) - 0.0386
#        if abs(Stream_Reflect) > 1:
#            Stream_Reflect = 0.0515 * (self.Solar.Zenith * math.pi / 180) - 3.636
#        if abs(Stream_Reflect) > 1:
#            Stream_Reflect = 0.091 * (1 / self.cos(self.Solar.Zenith * math.pi / 180)) - 0.0386
#        self.Flux["Diffuse"][5] = self.Flux["Diffuse"][4] * 0.91
#        self.Flux["Direct"][5] = self.Flux["Direct"][4] * (1 - Stream_Reflect)
#    def CalcFlux6(self):
#        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#        #6 - Received by Water Column
#        pass
#    def CalcFlux7(self):
#        #7 - Received by Bed
#        Dummy = math.atn((math.sin(self.Solar.Zenith * math.pi / 180) / 1.3333) / math.sqrt(-(math.sin(self.Solar.Zenith * math.pi / 180) / 1.3333) * (math.sin(self.Solar.Zenith * math.pi / 180) / 1.3333) + 1))
#        Water_Path = theDepth(Node, 1) / math.cos(Dummy) #Jerlov (1976)
#        Trans_Stream = 0.415 - (0.194 * math.log10(Water_Path * 100))
#        if Trans_Stream > 1:
#            Trans_Stream = 1
#        Dummy1 = self.Flux["Direct"][5] * (1 - Trans_Stream)       'Direct Solar Radiation attenuated on way down
#        Dummy2 = self.Flux["Direct"][5] - Dummy1                   'Direct Solar Radiation Hitting Stream bed
#        Bed_Reflect = math.exp(0.0214 * (self.Solar.Zenith * math.pi / 180) - 1.941)   'Reflection Coef. for Direct Solar
#        BedRock = 1 - thePorosity
#        Dummy3 = Dummy2 * (1 - Bed_Reflect)                'Direct Solar Radiation Absorbed in Bed
#        Dummy4 = 0.53 * BedRock * Dummy3                   'Direct Solar Radiation Immediately Returned to Water Column as Heat
#        Dummy5 = Dummy2 * Bed_Reflect                      'Direct Solar Radiation Reflected off Bed
#        Dummy6 = Dummy5 * (1 - Trans_Stream)               'Direct Solar Radiation attenuated on way up
#        self.Flux["Direct"][6] = Dummy1 + Dummy4 + Dummy6
#        self.Flux["Direct"][7] = Dummy3 - Dummy4
#        Trans_Stream = 0.415 - (0.194 * math.log10(100 * theDepth(Node, 1)))
#        if Trans_Stream > 1:
#            Trans_Stream = 1
#        if Trans_Stream > 1:
#            Trans_Stream = 1
#        Dummy1 = self.Flux["Diffuse"][5] * (1 - Trans_Stream)      'Diffuse Solar Radiation attenuated on way down
#        Dummy2 = self.Flux["Diffuse"][5] - Dummy1                  'Diffuse Solar Radiation Hitting Stream bed
#        Bed_Reflect = Exp(0.0214 * (0) - 1.941) 'Reflection Coef. for Diffuse Solar
#        Dummy3 = Dummy2 * (1 - Bed_Reflect)                'Diffuse Solar Radiation Absorbed in Bed
#        Dummy4 = 0.53 * BedRock * Dummy3                   'Diffuse Solar Radiation Immediately Returned to Water Column as Heat
#        Dummy5 = Dummy2 * Bed_Reflect                      'Diffuse Solar Radiation Reflected off Bed
#        Dummy6 = Dummy5 * (1 - Trans_Stream)               'Diffuse Solar Radiation attenuated on way up
#        self.Flux["Diffuse"][6] = Dummy1 + Dummy4 + Dummy6
#        self.Flux["Diffuse"][7] = Dummy3 - Dummy4
#        '   Flux_Solar(x) and Flux_Diffuse = Solar flux at various positions
#        '       0 - Edge of atmosphere
#        '       1 - Above Topography
#        '       2 - Above Land Cover
#        '       3 - Above Stream (After Land Cover Shade)
#        '       4 - Above Stream (What a Solar Pathfinder Measures)
#        '       5 - Entering Stream
#        '       6 - Received by Water Column
#        '       7 - Received by Bed
#        self.Flux["Solar"][1] = self.Flux["Diffuse"][1] + self.Flux["Direct"][1]
#        self.Flux["Solar"][2] = self.Flux["Diffuse"][2] + self.Flux["Direct"][2]
#        self.Flux["Solar"][4] = self.Flux["Diffuse"][4] + self.Flux["Direct"][4]
#        self.Flux["Solar"][5] = self.Flux["Diffuse"][5] + self.Flux["Direct"][5]
#        self.Flux["Solar"][6] = self.Flux["Diffuse"][6] + self.Flux["Direct"][6]
#        self.Flux["Solar"][7] = self.Flux["Diffuse"][7] + self.Flux["Direct"][7]
#
#    def CalcConductionFlux()
#        #======================================================
#        #Calculate Bed Conduction FLUX
#        #and hyporheic exchange temperature change
#        #======================================================
#        #Variables used in bed conduction
#        #Substrate Conduction Constants
#        Sed_Density = 1600 #kg/m3
#        Sed_ThermalDiffuse = 0.0000045 #m2/s
#        Sed_HeatCapacity = 2219 #J/(kg *C)
#        #======================================================
#        #Variables used in bed conduction
#        #Water Conduction Constants
#        H2O_Density = 1000 #kg/m3
#        H2O_ThermalDiffuse = 0.00000014331 #m2/s
#        H2O_HeatCapacity = 4187 #J/(kg *C)
#        #======================================================
#        #Variables used in bed conduction
#        #Calculate the sediment depth (conduction layer)
#        Sed_Depth = 10 * self.ParticleSize / 1000
#        if Sed_Depth > 1: Sed_Depth = 1
#        if Sed_Depth < 0.1: Sed_Depth = 0.1
#        #Sed_Depth = 0.2
#        #======================================================
#        #Variables used in bed conduction
#        #Calculate Volumetric Ratio of Water and Substrate
#        #Use this Ratio to Estimate Conduction Constants
#        Volume_Sediment = (1 - self.Porosity) * self.P_w * Sed_Depth * self.dx
#        Volume_H2O = self.Porosity * self.P_w * Sed_Depth * self.dx
#        Volume_Hyp = self.P_w * Sed_Depth * self.dx
#        Ratio_Sediment = Volume_Sediment / Volume_Hyp
#        Ratio_H2O = Volume_H2O / Volume_Hyp
#        Density = (Sed_Density * Ratio_Sediment) + (H2O_Density * Ratio_H2O)
#        HeatCapacity = (Sed_HeatCapacity * Ratio_Sediment) + (H2O_HeatCapacity * Ratio_H2O)
#        ThermalDiffuse = (Sed_ThermalDiffuse * Ratio_Sediment) + (H2O_ThermalDiffuse * Ratio_H2O)
#        #======================================================
#        #Calculate the conduction flux between water column & substrate
#        Flux_Conduction = ThermalDiffuse * Density * HeatCapacity * (self.T_sed - T(0, Node)) / (Sed_Depth / 2)
#        #Calculate the conduction flux between deeper alluvium & substrate
#        # TODO: Figure out when this is necessary or desirable
#    #    If Sheet2.Range("IV21").Value = 1 Then
#    #        Flux_Conduction_Alluvium = ThermalDiffuse * Density * HeatCapacity * (Temp_Sed(Node) - Sheet2.Range("IV20").Value) / (Sed_Depth / 2)
#    #    Else
#        Flux_Conduction_Alluvium = 0
#        #======================================================
#        #Calculate the changes in temperature in the substrate conduction layer
#        #Temperature change in substrate from solar exposure and conducted heat
#        NetHeat_Sed = Flux_Solar7 - Flux_Conduction - Flux_Conduction_Alluvium
#        DT_Sed = NetHeat_Sed * self.P_w * self.dx * self.dt / (Volume_Hyp * Density * HeatCapacity)
#        #======================================================
#        #Calculate the temperature of the substrate conduction layer
#        self.T_sed = T_sed + DT_Sed
#
#    def CalcLongwaveFlux()
#        #=====================================================
#        #Calculate Longwave FLUX
#        #======================================================
#        #Atmospheric variables
#        Air_T = self.T_air[time,-1]
#        Humidity = self.Humidity[time,-1]
#        Pressure = 1013 - 0.1055 * self.Zone[1][0] #mbar
#        Sat_Vapor = 6.1275 * Exp(17.27 * Air_T / (237.3 + Air_T)) #mbar (Chapra p. 567)
#        Air_Vapor = self.Humidity[time,-1] * Sat_Vapor
#        Sigma = 0.0000000567 #Stefan-Boltzmann constant (W/m2 K4)
#        Emissivity = 1.72 * (((Air_Vapor * 0.1) / (273.2 + Air_T)) ** (1 / 7)) * (1 + 0.22 * self.BC.C[time,-1] ** 2) #Dingman p 282
#        #======================================================
#        #Calcualte the atmospheric longwave flux
#        FLUX_LW_Atm = 0.96 * self.View_To_Sky * Emissivity * Sigma * (Air_T + 273.2) ** 4
#        #FLUX_LW_Atm = 0.96 * Emissivity * Sigma * (Air_T + 273.2) ^ 4
#        #Calcualte the backradiation longwave flux
#        FLUX_LW_Stream = -0.96 * Sigma * (self.prev_T + 273.2) ** 4
#        #Calcualte the vegetation longwave flux
#        FLUX_LW_Veg = 0.96 * (1 - self.View_To_Sky) * 0.96 * Sigma * (Air_T + 273.2) ** 4
#        #Calcualte the net longwave flux
#        Flux_Longwave = FLUX_LW_Atm + FLUX_LW_Stream + FLUX_LW_Veg
#
#    def CalcEvapConvFlux()
#        #===================================================
#        #Calculate Evaporation FLUX
#        #===================================================
#        #Atmospheric Variables
#        Wind = self.Wind[time,-1]
#        Air_T = self.T_air[time,-1]
#        Humidity = self.Humidity[time,-1]
#        Pressure = 1013 - 0.1055 * self.Zone[1][0].Elevation #mbar
#        Sat_Vapor = 6.1275 * Exp(17.27 * self.prev_T / (237.3 + self.T)) #mbar (Chapra p. 567)
#        Air_Vapor = self.Humidity[time,-1] * Sat_Vapor
#        #===================================================
#        #Calculate the frictional reduction in wind velocity
#        if Flag_Emergent == 1 and self.Zone[0][0].VHeight > 0:
#            if self.Zone[0][0].VHeight > 2:
#             Dummy = 2
#            Zd = 0.7 * self.Zone[0][0].VHeight
#            Zo = 0.1 * self.Zone[0][0].VHeight
#            Zm = 2
#            Friction_Velocity = Wind * 0.4 / Log((Zm - Zd) / Zo) #Vertical Wind Decay Rate (Dingman p. 594)
#        else:
#            Zo = 0.00023 #Brustsaert (1982) p. 277 Dingman
#            Zd = 0 #Brustsaert (1982) p. 277 Dingman
#            Zm = 2
#            Friction_Velocity = Wind
#        #===================================================
#        #Wind Function f(w)
#        Wind_Function = the_a + the_b * Friction_Velocity #m/mbar/s
#        #===================================================
#        #Latent Heat of Vaporization
#        LHV = 1000 * (2501.4 + (1.83 * T(0, Node))) #J/kg
#        #===================================================
#        #Use Jobson Wind Function
#        if self.IniParams.Penman:
#            #Calculate Evaporation FLUX
#            Gamma = 1003.5 * Pressure / (LHV * 0.62198) #mb/*C  Cuenca p 141
#            Delta = 6.1275 * math.exp(17.27 * Air_T / (237.3 + Air_T)) - 6.1275 * math.xp(17.27 * (Air_T - 1) / (237.3 + Air_T - 1))
#            NetRadiation = (Flux_Solar5 + Flux_Longwave)  #J/m2/s
#            if NetRadiation < 0:
#                NetRadiation = 0 #J/m2/s
#            Ea = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
#            Evap_Rate = ((NetRadiation * Delta / (P * LHV)) + Ea * Gamma) / (Delta + Gamma)
#            FLUX_Evaporation = -Evap_Rate * LHV * P #W/m2
#            #Calculate Convection FLUX
#            Bowen = Gamma * (T(0, Node) - Air_T) / (Sat_Vapor - Air_Vapor)
#            FLUX_Convection = FLUX_Evaporation * Bowen
#        else:
#            #===================================================
#            #Calculate Evaporation FLUX
#            Evap_Rate = Wind_Function * (Sat_Vapor - Air_Vapor)  #m/s
#            FLUX_Evaporation = -Evap_Rate * LHV * P #W/m2
#            #Calculate Convection FLUX
#            if (Sat_Vapor - Air_Vapor) <> 0:
#                Bowen = 0.61 * (Pressure / 1000) * (T(0, Node) - Air_T) / (Sat_Vapor - Air_Vapor)
#            else:
#                Bowen = 1
#            FLUX_Convection = FLUX_Evaporation * Bowen

