from __future__ import division

from math import pi,exp,log10,log,sqrt,sin,cos,tan,atan,radians

from itertools import count
from warnings import warn
from ..Dieties import Chronos
from ..Dieties import IniParams
from ..Utils.Logger import Logger
from ..Utils.easygui import indexbox, msgbox
_HS = None # Placeholder for heatsource module
Outfile = open("E:\evans.out","w")

class StreamNode(object):
    """Definition of an individual stream segment"""
    __slots__ = ["Latitude", "Longitude", "Elevation", # Geographic params
                "FLIR_Temp", "FLIR_Time", # FLIR data
                "T_sed", "T_in", "T_tribs", # Temperature attrs
                "VHeight", "VDensity", "Overhang", #Vegetation params
                "ContData", # Continuous data
                "Zone", "T_bc", # Initialization parameters, Zone and boundary conditions
                "Delta_T", # Current temperature calculated from only local fluxes
                "T", "T_prev", # Current and previous stream temperature
                "TopoFactor", # was Topo_W+Topo_S+Topo_E/(90*3) in original code. From Above stream surface solar flux calculations
                "ViewToSky", # Total angle of full sun view
                "ShaderList", # List of angles and attributes to determine sun shading.
                "F_DailySum", "F_Total", # Specific sums of solar fluxes
                "SedThermCond", "SedThermDiff", "SedDepth", # Sediment conduction values
                "hyp_percent", "T_alluv", # Percent hyporheic exchange and alluvium temperature
                "F_Solar", # List of important solar fluxes
                "S",        # Slope
                "n",        # Manning's n
                "z", # z factor: Ration of run to rise of the side of a trapazoidal channel
                "d_w", # Wetted depth. Calculated in GetWettedDepth()
                "d_w_prev", # Wetted depth for the previous timestep
                "d_cont", # Control depth
                "W_b", # Bottom width
                "W_w", # Wetted width, calculated as W_b + 2*z*d_w
                "A", # Cross-sectional Area, calculated d_w * (W_b + z * d_w)
                "P_w", # Wetted Perimeter, calculated as W_b + 2 * d_w * sqrt(1 + z**2)
                "R_h", # Hydraulic Radius, calculated as A_x/P_w
                "dx", # Length of this stream reach.
                "U", # Velocity from Manning's relationship
                "Q", # Discharge, from Manning's relationship
                "Q_prev", # Discharge at previous timestep, previous space step is taken from another node
                "Q_cont", # Control discharge
                "V", # Total volume, based on current flow
                "Q_tribs", # Inputs from tribs.
                "Q_in", # Inputs from "accretion" in cubic meters per second
                "Q_out", # Withdrawls from the stream, in cubic meters per second
                "Q_hyp", # Hyporheic flow
                "km", # River kilometer, from mouth
                "Q_bc", # Boundary conditions, in a TimeList class, for discharge.
                "E", # Evaporation volume inm m^3
                "dt", # This is the timestep (for kinematic wave movement, etc.)
                "phi", # Porosity of the bed
                "Log",  # Global logging class
                "Disp", "S1", # Dispersion due to shear stress and placeholder calculation variable
                "next_km", "prev_km", "head", # reference placeholders for next, previous nodes and headwater node
                "Q_mass", # Local mass balance variable (StreamChannel level)
                "F_Conduction","F_Convection","F_Longwave","F_Evaporation", # Ground flux variables
                "F_LW_Stream", "F_LW_Atm", "F_LW_Veg", # Longwave fluxes
                "C_args", # tuple of variables that do not change during the model
                "CalcHeat", "CalcDischarge", # Reference to correct heat calculation method
                "SolarPos" # Solar position variables (headwater node only)
                ]
    def __init__(self, **kwargs):
        # Define members in __slots__ to ensure that later member names cannot be added accidentally
        # Set all the attributes to bare lists, or set from the constructor
        for attr in self.__slots__:
            x = kwargs[attr] if attr in kwargs.keys() else None
            setattr(self, attr, x)
        self.T = 0.0
        self.Q_mass = 0
        for attr in ["ContData", "T_tribs", "Q_tribs"]:
            setattr(self, attr, {})
        # Create an internal dictionary that we can pass to the C module, this contains self.slots attributes
        # and other things the C module needs
        for attr in ["F_Conduction","F_Convection","F_Longwave","F_Evaporation"]:
            setattr(self, attr, 0)
        self.F_Solar = [0]*8
        self.F_Total = 0.0
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
    def __repr__(self):
        return '%s @ %.3f km' % (self.__class__.__name__, self.km)

    def Initialize(self):
        """Methods necessary to set initial conditions of the node"""
        global _HS
        has_prev = self.prev_km is not None
        if has_prev:
            self.CalcHeat = self.CalcHeat_Opt
        else:
            self.CalcHeat = self.CalcHeat_BoundaryNode
        if IniParams["runmodule"] == "Python Source":
            import PyHeatsource
            _HS = PyHeatsource
        else:
            import heatsource
            _HS = heatsource.heatsource
        self.CalcDischarge = self.CalculateDischarge
        self.C_args = (self.W_b, self.Elevation, self.TopoFactor, self.ViewToSky, self.phi, self.VDensity, self.VHeight,
                       self.SedDepth, self.dx, self.dt, self.SedThermCond, self.SedThermDiff, self.Q_in, self.T_in, has_prev,
                       IniParams["longsample"],IniParams["emergent"], IniParams["wind_a"], IniParams["wind_b"],
                       IniParams["calcevap"], IniParams["penman"])

    def CalcDischarge_Opt(self,time,hour):
        """A Version of CalculateDischarge() that does not require checking for boundary conditions"""
        inputs = self.Q_in + sum(self.Q_tribs[hour]) - self.Q_out - self.E
        self.Q_mass += inputs
        up = self.prev_km
        try:
            Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                    _HS.CalcFlows(self.U, self.W_w, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont,
                                 self.Q, up.Q, up.Q_prev, inputs, -1)
        except _HS.HeatSourceError, (stderr):
            self.CatchException(stderr)
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_percent # Hyporheic discharge

        if Q < 0.003: #Channel is not going dry
            print "The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime)

    def CalcDischarge_BoundaryNode(self, time, hour):
        Q_bc = self.Q_bc[hour]
        self.Q_mass += Q_bc
        # We fill the discharge arguments with 0 because it is unused in the boundary case
        try:
            Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                    _HS.CalcFlows(self.U, self.W_w, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont,
                                  0.0, 0.0, 0.0, 0.0, Q_bc)
        except _HS.HeatSourceError, (stderr):
            self.CatchException(stderr)

        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_percent # Hyporheic discharge
        if Q < 0.003: #Channel is going dry
            print "The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime)

    def CalculateDischarge(self, time, hour):
        """Return the discharge for the current timestep

        This method uses the GetKnownDischarges() and GetMuskigum() methods (in C module) to
        grab the values necessary to calculate the discharge at the current timestep for
        the channel. If we are at a boundary (spatial or temporal) the appropriate
        boundary condition is returned. When the new discharge is calculated, the previous
        discharge value is placed in Q_prev for use by the downstream channel. This method
        makes some assumptions, one is that Q_bc is a TimeList instance holding boundary conditions
        for the given node, and that this is only True if this node has no upstream channel. Two
        is that the values for Q_tribs is a TimeList instance or None, that Q_in and Q_out are values
        in cubic meters per second of inputs and withdrawls or None. The argument t is for a
        Python datetime object and can (should) be None if we are not at a spatial boundary. dt is
        the timestep in minutes, which cannot be None.
        """
        inputs = self.Q_in + sum(self.Q_tribs[hour]) - self.Q_out - self.E
        # Check if we are a spatial or temporal boundary node
        if self.prev_km: # There's an upstream channel, but no previous timestep.
            # In this case, we sum the incoming flow which is upstream's current timestep plus inputs.
            Q = self.prev_km.Q_prev + inputs # Add upstream node's discharge at THIS timestep- prev_km.Q would be next timestep.
            try:
                Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                        _HS.CalcFlows(0.0, 0.0, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont, 0.0, 0.0, 0.0, inputs, Q)
            except _HS.HeatSourceError, (stderr):
                self.CatchException(stderr)
            # If we hit this once, we remap so we can avoid the if statements in the future.
            self.CalcDischarge = self.CalcDischarge_Opt
        else: # We're a spatial boundary, use the boundary condition
            # At spatial boundaries, we return the boundary conditions from Q_bc
            Q_bc = self.Q_bc[hour]
            self.Q_mass += Q_bc
            # We pad the arguments with 0 because some are unused (or currently None) in the boundary case
            try:
                Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                        _HS.CalcFlows(0.0, 0.0, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont, 0.0, 0.0, 0.0, inputs, Q_bc)
            except _HS.HeatSourceError, (stderr):
                self.CatchException(stderr)
            self.CalcDischarge = self.CalcDischarge_BoundaryNode

        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q  or Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_percent # Hyporheic discharge

        if Q < 0.003: #Channel is going dry
            self.Log.write("The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime))

    def CatchException(self, sterr, time):
        msg = "At %s and time %s\n"%(self,time.isoformat(" ") )
        if isinstance(stderr,tuple):
            msg += """%s\n\tVariables causing this affliction:
dt: %4.0f
dx: %4.0f
K: %4.4f
X: %3.4f
c_k: %3.4f""" % stderr
        else: msg += stderr

        msg += "\nThe model run has been halted. You may ignore any further error messages."
        msgbox(msg)
        raise SystemExit

    def CalcHeat_Opt(self, hour, min, sec, bc_hour,JD,JDC,offset, file=None):
        """Inlined version of CalcHeat optimized for non-boundary nodes (removes a bunch of if/else statements)"""
        # Reset temperatures
        self.T_prev = self.T
        self.T = None
        Altitude, Zenith, Daytime, dir = self.head.SolarPos
        try:
            self.F_Solar, \
                (self.F_Conduction, self.T_sed, self.F_Longwave, self.F_LW_Atm, self.F_LW_Stream, \
                 self.F_LW_Veg, self.F_Evaporation, self.F_Convection, self.E), self.F_Total, self.Delta_T, self.T, self.S1 = \
                _HS.CalcHeatFluxes(self.ContData[bc_hour], self.C_args, self.d_w, self.A, self.P_w, self.W_w, self.U,
                            self.Q_tribs[bc_hour], self.T_tribs[bc_hour], self.T_alluv, self.T_prev, self.T_sed,
                            self.Q_hyp,self.next_km.T_prev, self.ShaderList[dir], self.Disp,
                            hour, JD, Daytime,Altitude, Zenith, self.prev_km.Q_prev, self.prev_km.T_prev)
        except _HS.HeatSourceError, (stderr):
            self.CatchException(stderr)
        T, S1 = self.MacCormick_THW(bc_hour)

        self.F_DailySum[1] += self.F_Solar[1]
        self.F_DailySum[4] += self.F_Solar[4]

    def CalcHeat_BoundaryNode(self, hour, min, sec, bc_hour,JD,JDC,offset, file):
        # Reset temperatures
        self.T_prev = self.T
        self.T = None
        Altitude, Zenith, Daytime, dir = _HS.CalcSolarPosition(self.Latitude, self.Longitude, hour, min, sec, offset, JDC)
        self.SolarPos = Altitude, Zenith, Daytime, dir
        try:
            self.F_Solar, \
                (self.F_Conduction, self.T_sed, self.F_Longwave, self.F_LW_Atm, self.F_LW_Stream, \
                 self.F_LW_Veg, self.F_Evaporation, self.F_Convection, self.E), self.F_Total, self.Delta_T = \
                _HS.CalcHeatFluxes(self.ContData[bc_hour], self.C_args, self.d_w, self.A, self.P_w, self.W_w, self.U,
                            self.Q_tribs[bc_hour], self.T_tribs[bc_hour], self.T_alluv, self.T_prev, self.T_sed,
                            self.Q_hyp, self.next_km.T_prev, self.ShaderList[dir], self.Disp,
                            hour, JD, Daytime, Altitude, Zenith, 0.0, 0.0)
        except _HS.HeatSourceError, (stderr):
            self.CatchException(stderr)
        self.F_DailySum[1] += self.F_Solar[1]
        self.F_DailySum[4] += self.F_Solar[4]

        self.T = self.T_bc[bc_hour]
        self.T_prev = self.T_bc[bc_hour]

    def MacCormick2(self, hour):
        #===================================================
        #Set control temps
        if not self.prev_km:
            return
        #===================================================
        self.T, S = _HS.CalcMacCormick(self.dt, self.dx, self.U, self.T_sed, self.T_prev, self.Q_hyp,
                                    self.Q_tribs[hour], self.T_tribs[hour], self.prev_km.Q, self.Delta_T, self.Disp,
                                    True, self.S1, self.prev_km.T, self.T, self.next_km.T, self.Q_in, self.T_in)

    def CalcDispersion(self):
        dx = self.dx
        dt = self.dt
        if not self.S:
            Shear_Velocity = self.U
        else:
            Shear_Velocity = sqrt(9.8 * self.d_w * self.S)
        Disp = 0.011 * (self.U ** 2) * (self.W_w ** 2) / (self.d_w * Shear_Velocity)
        if Disp * dt / (dx ** 2) > 0.5:
            Disp = (0.45 * (dx ** 2)) / dt
        return Disp

    def MacCormick_THW(self, bc_hour):
        mix = self.MixItUp(bc_hour,self.prev_km.Q_prev, self.prev_km.T_prev) if self.Q else 0
        T0 = self.prev_km.T_prev + mix
        T1 = self.T_prev
        T2 = self.next_km.T_prev if self.next_km else self.T_prev
        Dummy1 = -self.U * (T1 - T0) / self.dx
        Disp = self.CalcDispersion()
        Dummy2 = Disp * (T2 - 2 * T1 + T0) / (self.dx ** 2)
        S1 = Dummy1 + Dummy2 + self.Delta_T / self.dt
        T = T1 + S1 * self.dt
        return T, S1

    def MacCormick_BoundaryNode(self,args):
        if not args[12]: # We're running the first time if we have no S value.
            self.T = self.T_bc[hour]
            self.T_prev = self.T_bc[hour]
        else:
            pass

    def MacCormick2_THW(self,hour):
        SkipNode = False
        if self.prev_km:
            print self.prev_km.T
            if not SkipNode:
                mix = self.MixItUp(hour, self.prev_km.Q, self.prev_km.T) if self.Q else 0
                T0 = self.prev_km.T + mix
                T1 = self.T
                T2 = self.next_km.T if self.next_km else self.T
                #======================================================
                #Final MacCormick Finite Difference Calc.
                #===================================================
                Dummy1 = -self.U * (T1 - T0) / self.dx
                Dummy2 = self.Disp * (T2 - 2 * T1 + T0) / (self.dx ** 2)
                S2 = Dummy1 + Dummy2 + self.Delta_T / self.dt
                T = self.T_prev + ((self.S1 + S2) / 2) * self.dt
            else:
                T = self.T_prev
        else: T = self.T_prev
        if T > 50 or T < 0:
            raise Exception("Unstable model")
        return T

    def MixItUp(self, bc_hour, Q_up, T_up):
        Q_in = 0
        T_in = 0
        for i in xrange(len(self.Q_tribs[bc_hour])):
            Q_in += self.Q_tribs[bc_hour][i] if self.Q_tribs[bc_hour][i] > 0 else 0
            T_in += self.T_tribs[bc_hour][i] if self.Q_tribs[bc_hour][i] > 0 else 0

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
#            T_mix = ((Q_accr * T_accr) + (T_mix * (Q_up + Q_in))) / (Q_accr + Q_up + Q_in)
        return T_mix - T_up
