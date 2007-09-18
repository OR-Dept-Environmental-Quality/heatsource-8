from __future__ import division
import math, decimal
from warnings import warn
import heatsource.heatsource as _HS
from ..Dieties import Chronos as Clock
from ..Dieties import IniParams

class StreamChannel(object):
    """Class that describes the geometry of a stream channel

    This class includes all of the mathematics and geometry
    routines to define a trapezoidal stream channel, including
    methods for calculation of wetted depth from discharge
    using the Newton-Raphson iteration method. In the future,
    an argument can be added to the constructor to define other
    kinds of channels, or some of this can be pushed down to
    a base class.
    """
    def __init__(self):
    # Protect the allowable attributes, so we cannot later add an attribute.
    # This is useful to avoid programming errors where we might set self.Slope
    # at some point, and access self.S at another point.
        self.slots = ["S",        # Slope
                    "n",        # Manning's n
                    "W_bf",     # Bankfull width (surface)
                    "z", # z factor: Ration of run to rise of the side of a trapazoidal channel
                    "d_bf", # Bankfull Depth, See below or HeatSource manual
                    "d_ave", # Average bankfull depth, calculated as W_bf/WD
                    "d_w", # Wetted depth. Calculated in GetWettedDepth()
                    "d_w_prev", # Wetted depth for the previous timestep
                    "d_cont", # Control depth
                    "W_b", # Bottom width, calculated as W_bf - (2 * d_bf * z)
                    "W_w", # Wetted width, calculated as W_b + 2*z*d_w
                    "A", # Cross-sectional Area, calculated d_w * (W_b + z * d_w)
                    "P_w", # Wetted Perimeter, calculated as W_b + 2 * d_w * sqrt(1 + z**2)
                    "R_h", # Hydraulic Radius, calculated as A_x/P_w
                    "WD", # Width/Depth ratio, constant
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
                    "next_km", # Reference to next (downstream) river channel instance (Set externally)
                    "prev_km", # Reference to prevous (Upstream) river channel instance (also set externally)
                    "Q_bc", # Boundary conditions, in a TimeList class, for discharge.
                    "E", # Evaporation volume inm m^3
                    "dt", # This is the timestep (for kinematic wave movement, etc.)
                    "phi", # Porosity of the bed
                    "K_h", # Horizontal bed conductivity
                    "Log",  # Global logging class
                    "Disp", # Dispersion due to shear stress
                    "Q_mass" # Local mass balance variable (StreamChannel level)
                    ]
        for attr in self.slots:
            setattr(self,attr,None)
        self.Q_mass = 0
        self.starttime = Clock.MakeDatetime(IniParams["date"])
        # Make the C module's functions part of the class
        self.CalcSolarPosition = _HS.CalcSolarPosition
        self.CalcSolarFlux = _HS.CalcSolarFlux
        self.CalcGroundFluxes = _HS.CalcGroundFluxes
        self.GetStreamGeometry = _HS.GetStreamGeometry
        self.GetMuskingum = _HS.CalcMuskingum

    def __repr__(self):
        return '%s @ %.3f km' % (self.__class__.__name__, self.km)
    def __lt__(self, other): return self.km < other.km
    def __le__(self, other): return self.km <= other.km
    def __eq__(self, other): return self.km == other.km
    def __ne__(self, other): return self.km != other.km
    def __gt__(self, other): return self.km > other.km
    def __ge__(self, other): return self.km >= other.km

    def CalcDischarge_Opt(self,time,hour):
        """A Version of CalculateDischarge() that does not require checking for boundary conditions"""
        inputs = self.Q_in + self.Q_tribs[hour] - self.Q_out - self.E
        self.Q_mass += inputs
        Q2 = self.prev_km.Q_prev + inputs

        C1,C2,C3 = self.GetMuskingum(Q2, self.U, self.W_w, self.S, self.dx, self.dt)
        # Calculate the new Q
        Q = C1*(self.prev_km.Q + inputs) + C2*Q2 + C3*self.Q
        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge

        if Q > 0.0071: #Channel is not going dry
            self.d_w, self.A,self.P_w,self.R_h,self.W_w,self.U, self.Disp = self.GetStreamGeometry(self.Q, self.W_b, self.z, self.n, self.S, self.d_cont, self.dx, self.dt)
        else:# That's it for discharge, let's recalculate our channel geometry, hyporheic flow, etc.
            self.Log.write("The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime))
            self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U = [0]*6  # Set variables to zero (from VB code)

    def CalcDischarge_BoundaryNode(self, time, hour):
        Q = self.Q_bc[hour] # Get the value at this time, or the closest previous time
        self.Q_mass += self.Q_bc[hour]
        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge

        if Q > 0.0071: #Channel is going dry
            self.d_w, self.A,self.P_w,self.R_h,self.W_w,self.U, self.Disp = self.GetStreamGeometry(self.Q, self.W_b, self.z, self.n, self.S, self.d_cont, self.dx, self.dt)
        else:# That's it for discharge, let's recalculate our channel geometry, hyporheic flow, etc.
            self.Log.write("The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime))
            self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U = [0]*6  # Set variables to zero (from VB code)

    def CalculateDischarge(self, time, hour):
        """Return the discharge for the current timestep

        This method uses the GetKnownDischarges() and GetMuskigum() methods to
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
        inputs = self.Q_in + self.Q_tribs[hour] - self.Q_out - self.E
        # Check if we are a spatial or temporal boundary node
        if self.prev_km and self.Q_prev: # No, there's an upstream channel and a previous timestep
            self.Q_mass += inputs
            # Get all of the discharges that we know about.
            # (t, x-1) = flow from the upstream channel at this timestep
            Q1 = self.prev_km.Q + inputs
            # (t-1, x-1) = flow from the upstream channel's previous timestep.
            Q2 = self.prev_km.Q_prev + inputs
            # (t-1, x) = flow from the previous timestep in this channel (it is the previous timestep
            # because we have not yet assigned a new value for this timesetp)
            Q3 = self.Q

            # Use (t,x-1) to calculate the Muskingum coefficients
            C1,C2,C3 = self.GetMuskingum(Q2, self.U, self.W_w, self.S, self.dx, self.dt)
            # Calculate the new Q
            Q = C1*Q1 + C2*Q2 + C3*Q3
            # If we hit this once, we remap so we can avoid the if statements in the future.
            self.CalculateDischarge = self.CalcDischarge_Opt
        elif not self.prev_km: # We're a spatial boundary, use the boundary condition
            # At spatial boundaries, we return the boundary conditions from Q_bc
            Q = self.Q_bc[hour]
            self.Q_mass += self.Q_bc[hour]
            self.CalculateDischarge = self.CalcDischarge_BoundaryNode
            self.MacCormick = self.MacCormick_BoundaryNode # We're a boundary node, so go ahead and reset MacCormick.
            # TODO: Might want some error checking here.
        elif not self.Q_prev: # There's an upstream channel, but no previous timestep.
            # In this case, we sum the incoming flow which is upstream's current timestep plus inputs.
            Q = self.prev_km.Q_prev + inputs # Add upstream node's discharge at THIS timestep- prev_km.Q would be next timestep.
            self.MacCormick = _HS.CalcMacCormick # We're not a boundary node, so reset MacCormick.

        else: raise Exception("WTF?")

        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q  or Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge

        if Q < 0.0071: #Channel is going dry
            self.Log.write("The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime))
            self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U = [0]*6  # Set variables to zero (from VB code)
        else:# That's it for discharge, let's recalculate our channel geometry, hyporheic flow, etc.
            self.d_w, self.A,self.P_w,self.R_h,self.W_w,self.U, self.Disp = self.GetStreamGeometry(self.Q, self.W_b, self.z, self.n, self.S, self.d_cont, self.dx, self.dt)
    def CalcHydroStability(self):
        """Ensure stability of the timestep using the technique from pg 82 of the HS manual

        This is only used if we are not using Muskingum routing, at least in the original code."""
        #Maxdt = 1e6
        #for node in reach:
        #    Dummy = node.dx / (node.Velocity[0] + math.sqrt(9.861 * node.Depth[0]))
        #    if Dummy < Maxdt: Maxdt = Dummy
        #    Dummy = (node.Rh ** (4 / 3)) / (9.861 * node.Velocity[0] * (node.N ** 2))
        #    if Dummy < Maxdt: Maxdt = Dummy
        #if Maxdt < iniparams.dt: dt = Maxdt
        #else: dt = iniparams.dt
        #return dt
        pass

    def GetMuskingum_THW(self, Q_est):
        """Return the values for the Muskigum routing coefficients
        using current timestep and optional discharge"""
        #Calculate an initial geometry based on an estimated discharge (typically (t,x-1))
        # Taken from the VB source.
        c_k = (5/3) * self.U  # Wave celerity
        X = 0.5 * (1 - Q_est / (self.W_w * self.S * self.dx * c_k))
        if X > 0.5: X = 0.5
        elif X < 0.0: X = 0.0
        K = self.dx / c_k
        dt = self.dt

        # Check the celerity to ensure stability. These tests are from the VB code.
        if dt >= (2 * K * (1 - X)) or dt > (self.dx/c_k):  #Unstable - Decrease dt or increase dx
            raise Exception("Unstable timestep. K=%0.3f, X=%0.3f, tests=(%0.3f, %0.3f)" % (K,X,test0,test1))

        # These calculations are from Chow's "Applied Hydrology"
        D = K * (1 - X) + 0.5 * dt
        C1 = (0.5*dt - K * X) / D
        C2 = (0.5*dt + K * X) / D
        C3 = (K * (1 - X) - 0.5*dt) / D
        # TODO: reformulate this using an updated model, such as Moramarco, et.al., 2006
        return C1, C2, C3

    def SetBankfullMorphology(self):
        """Calculate initial morphological characteristics in terms of W_bf, z and WD"""
        if self.z >= self.WD/2:
            warn("Reach %s has no bottom width. Z: %0.3f, WD:%0.3f. Recalculating Channel angle." % (self, self.z, self.WD))
            self.z = 0.99 * (self.WD/2)

        # Average depth of the trapazoid from the width/depth ratio
        self.d_ave = self.W_bf/self.WD
        # Calculate the maximum depth of the channel and the bottom width by iterating to a solution where
        # the cross-sectional area (Xarea) = trapezoidal area (Tarea)
        Xarea = self.d_ave * self.W_bf
        #Initialize maximum depth and bottom width
        self.d_bf = self.d_ave
        self.W_b = self.W_bf - 2*self.z*self.d_bf
        Trap_area = self.d_bf * (self.W_b + self.W_bf)/2
        self.d_w = self.d_ave # Initialize wetted depth to bankfull wetted depth
        # We have to iterate to find the bottom width and bankful depth because we have two equations
        # and two unknowns, so we iterate until the area of the trapazoid (cross-sectional flow area)
        # is equal to the average area (average depth times bankful width). The purpose of this is to
        # find the channel's bottom width.
        #TODO: Find out whether we need bankful depth, and remove it from the class if not.
        while (Xarea - Trap_area) > 0.001:
            self.d_bf = self.d_bf + 0.01
            self.W_b = self.W_bf - 2*self.z*self.d_bf
            Trap_area = self.d_bf * (self.W_b + self.W_bf)/2
