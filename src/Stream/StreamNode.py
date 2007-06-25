from __future__ import division
import math, wx, bisect
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
             "TopoFactor", # was Topo_W+Topo_S+Topo_E/(90*3) in original code. From Above stream surface solar flux calculations
             "ShaderList", # List of angles and attributes to determine sun shading.
             "F_DailySum", # Specific sums of solar fluxes
             "F_Solar", # List of important solar fluxes
             ]
        # Set all the attributes to bare lists, or set from the constructor
        for attr in s:
            x = kwargs[attr] if attr in kwargs.keys() else None
            setattr(self, attr, x)
        self.T = 0.0
        self.slots += s
        for attr in ["Wind", "Humidity", "T_air", "T_tribs", "Q_tribs"]:
            setattr(self, attr, {})
        # Create an internal dictionary that we can pass to the C module, this contains self.slots attributes
        # and other things the C module needs
        self.F_DailySum = [0]*5
        #TODO: Cleanup this flux dictionary
        self.S1 = 0
        self.Log = Logger
        self.ShaderList = ()

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

    def CalcHydraulics(self, time, hour):
        # Convenience variables
        dt = self.dt
        dx = self.dx
        # Iterate down the stream channel, calculating the discharges
        self.CalculateDischarge(time, hour)
        ################################################################
        ### This section seems unused in the original code. It calculates a stratification
        # tendency factor. We can implement it (possibly in StreamChannel) if we need to
        #===================================================
        #Calculate tendency to stratify
        #try:
        #    self.Froude_Densiometric = math.sqrt(1 / (9.8 * 0.000001)) * dx * self.Q / (self.d_w * self.A * self.dx)
        #except:
        #    print self.d_w, self.A, self.dx
        #    raise
        #===================================================
        #else: #Skip Node - No Flow in Channel
        #    self.Hyporheic_Exchange = 0
        #    self.T = 0
        #    self.Froude_Densiometric = 0

        #===================================================
        #Check to see if wetted widths exceed bankfull widths
        #TODO: This has to be reimplemented somehow, because Excel is involved
        # connected to the backend. Meaning this class has NO understanding of what the Excel
        # spreadsheet is. Thus, something must be propigated backward to the parent class
        # to fiddle with the spreadsheet. Perhaps we can write a report to a text file or
        # something. I'm very hesitant to connect this too tightly with the interface.
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

    def Initialize(self):
        """Methods necessary to set initial conditions of the node"""
        self.SetBankfullMorphology()
    def CalcHeat(self, hour, min, sec, time,JD,JDC,offset):
        Altitude, Zenith, Daytime, dir = self.CalcSolarPosition(self.Latitude, self.Longitude, hour, min, sec, offset, JDC)

        # Set some local variables if they're used more than once
        Elev = self.Elevation
        VTS = self.ViewToSky
        emerg = IniParams["emergent"]
        VHeight = self.VHeight
        cloud = self.C_bc[time]
        dt = self.dt
        dx = self.dx
        T_sed = self.T_sed
        T_prev = self.T_prev
        Q_hyp = self.Q_hyp
        ############################################
        ## Solar Flux Calculation, C-style
        # Testing method, these should return the same (to 1.0e-6 or so) result
#       self.F_Solar = self.Solar_THW(JD,time, hour, Altitude,Zenith,dir,IniParams["transsample"], Daytime)
        if Daytime:
            self.F_Solar = self.CalcSolarFlux(hour, JD, Altitude, Zenith, cloud, self.d_w,
                                              self.W_b, Elev, self.TopoFactor, VTS,
                                              IniParams["transsample"], self.phi, emerg,
                                              self.VDensity, VHeight, self.ShaderList[dir])
            self.F_DailySum[1] += self.F_Solar[1]
            self.F_DailySum[4] += self.F_Solar[4]
        else:
            self.F_Solar = [0]*8
        #Testing method, these should return the same (to 1.0e-6 or so) result
        #self.F_Conduction, self.T_sed, self.F_Longwave, self.F_LW_Atm, self.F_LW_Stream, self.F_LW_Veg, self.F_Evaporation, self.F_Convection, self.E = self.GroundFlux_THW(time)
        self.F_Conduction, self.T_sed, self.F_Longwave, self.F_LW_Atm, self.F_LW_Stream, \
            self.F_LW_Veg, self.F_Evaporation, self.F_Convection, self.E = \
            self.CalcGroundFluxes(cloud, self.Humidity[time], self.T_air[time], self.Wind[time], Elev,
                                self.phi, VHeight, VTS, self.SedDepth, dx,
                                dt, self.SedThermCond, self.SedThermDiff, self.T_alluv, self.P_w,
                                self.W_w, emerg, IniParams["penman"], IniParams["wind_a"], IniParams["wind_b"],
                                IniParams["calcevap"], T_prev, T_sed, Q_hyp, self.F_Solar[5], self.F_Solar[7])

        self.F_Total = self.F_Solar[6] + self.F_Conduction + self.F_Evaporation + self.F_Convection + self.F_Longwave
        self.Delta_T = self.F_Total * self.dt / ((self.A / self.W_w) * 4182 * 998.2) # Vars are Cp (J/kg *C) and P (kgS/m3)

        # If we're a boundary node, we don't calculate MacCormick1, so get out quickly
        if not self.prev_km:
            self.T = self.T_bc[time]
            self.T_prev = self.T_bc[time]
            return

        T2 = self.next_km.T_prev if self.next_km else self.T_prev
        self.T, self.S1 = self.MacCormick(dt, dx, self.U, T_sed, T_prev, Q_hyp, self.Q_tribs[time], self.T_tribs[time],
                                          self.prev_km.Q_prev, self.Delta_T, self.Disp,
                                          False, 0.0, self.prev_km.T_prev, self.T_prev, T2, self.Q_in, self.T_in)

    def MacCormick2(self, time):
        #===================================================
        #Set control temps
        if self.T_cont:
            self.T = self.T_cont
            return
        if not self.prev_km:
            return
        #===================================================
        T2 = self.next_km.T if self.next_km else self.T

        self.T, S = self.MacCormick(self.dt, self.dx, self.U, self.T_sed, self.T_prev, self.Q_hyp,
                                    self.Q_tribs[time], self.T_tribs[time], self.prev_km.Q, self.Delta_T, self.Disp,
                                    True, self.S1, self.prev_km.T, self.T, T2, self.Q_in, self.T_in)
        if self.T > 50 or self.T < 0:
            raise Exception("Unstable model")

    def MacCormick_THW(self, hour):
        dt = self.dt
        dx = self.dx
        mix = 0
        SkipNode = False
        if self.prev_km:
            if not SkipNode:
                mix = self.MixItUp(hour,self.prev_km.Q_prev, self.prev_km.T_prev)
                T0 = self.prev_km.T_prev + mix
                T1 = self.T_prev
                T2 = self.next_km.T_prev if self.next_km else self.T_prev
                Dummy1 = -self.U * (T1 - T0) / dx
#                self.CalcDispersion()
                Dummy2 = self.Disp * (T2 - 2 * T1 + T0) / (dx ** 2)
                S1 = Dummy1 + Dummy2 + self.Delta_T / dt
                T = T1 + S1 * dt
            else:
                T = self.T_prev #TODO: This is wrong, really should be self.T_prev_prev
        else:
            T = self.T_bc[hour]
            T_prev = self.T_bc[hour]
        return T, S1

    def MacCormick_BoundaryNode(self,args):
        if not args[12]: # We're running the first time if we have no S value.
            self.T = self.T_bc[hour]
            self.T_prev = self.T_bc[hour]
        else:
            pass

    def MacCormick2_THW(self,hour):
        #===================================================
        #Set control temps
        if self.T_cont:
            self.T = self.T_cont
            return
        #===================================================
        SkipNode = False
        if self.prev_km:
            if not SkipNode:
                mix = self.MixItUp(hour, self.prev_km.Q, self.prev_km.T)
                T0 = self.prev_km.T + mix
                T1 = self.T
                #======================================================
                #Final MacCormick Finite Difference Calc.
                #===================================================
                Dummy1 = -self.U * (T1 - T0) / dx
                Dummy2 = self.Disp * (T2 - 2 * T1 + T0) / dx ** 2
                S2 = Dummy1 + Dummy2 + self.Delta_T / dt
                self.T = self.T_prev + ((S1 + S2) / 2) * dt
            else:
                self.T = self.T_prev
        if self.T > 50 or self.T < 0:
            raise Exception("Unstable model")

    def MixItUp(self, hour, Q_up, T_up):
        time = Chronos.TheTime
        # Get any point-source inflow data
        if self.Q:
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
        else: return 0