from __future__ import division
import math, decimal, weakref
from warnings import warn
import heatsource.heatsource as _HS
from ..Dieties import Chronos
from ..Dieties import IniParams

class Nothing(object):
    """Class that returns None when called"""
    def __call__(self): return None

class StreamChannel(object):
    """Class that describes the geometry of a stream channel

    This class includes all of the mathematics and geometry
    routines to define a trapezoidal stream channel, including
    methods for calculation of wetted depth from discharge
    using the Newton-Raphson iteration method. In the future,
    an argument can be added to the constructor to define other
    kinds of channels, or some of this can be pushed down to
    a base class. This class is designed to use the heatsource
    C module extensively.
    """
    def __init__(self):
        # This was originally a use of the __slots__ attribute that didn't work with subclasses.
        # We could do this differently, but this is just as good.
        slots = ["S",        # Slope
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
                    "Disp", # Dispersion due to shear stress
                    "next_km", "prev_km",
                    "Q_mass" # Local mass balance variable (StreamChannel level)
                    ]
        for attr in slots:
            setattr(self,attr,None)
        self.Q_mass = 0
        self.starttime = Chronos.MakeDatetime(IniParams["modelstart"])


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
        inputs = self.Q_in + sum(self.Q_tribs[hour]) - self.Q_out - self.E
        self.Q_mass += inputs
        up = self.prev_km
        Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                _HS.CalcFlows(self.U, self.W_w, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont,
                             self.Q, up.Q, up.Q_prev, inputs, -1)
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge

        if Q < 0.003: #Channel is not going dry
            print "The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime)

    def CalcDischarge_BoundaryNode(self, time, hour):
        Q_bc = self.Q_bc[hour]
        self.Q_mass += Q_bc
        # We fill the discharge arguments with 0 because it is unused in the boundary case
        Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                _HS.CalcFlows(self.U, self.W_w, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont,
                              0.0, 0.0, 0.0, 0.0, Q_bc)
        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge
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
            Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                    _HS.CalcFlows(0.0, 0.0, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont, 0.0, 0.0, 0.0, inputs, Q)
            # If we hit this once, we remap so we can avoid the if statements in the future.
            self.CalculateDischarge = self.CalcDischarge_Opt
        else: # We're a spatial boundary, use the boundary condition
            # At spatial boundaries, we return the boundary conditions from Q_bc
            Q_bc = self.Q_bc[hour]
            self.Q_mass += Q_bc
            # We pad the arguments with 0 because some are unused (or currently None) in the boundary case
            Q, self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U, self.Disp = \
                    _HS.CalcFlows(0.0, 0.0, self.W_b, self.S, self.dx, self.dt, self.z, self.n, self.d_cont, 0.0, 0.0, 0.0, inputs, Q_bc)
            self.CalculateDischarge = self.CalcDischarge_BoundaryNode

        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        self.Q_prev = self.Q  or Q
        self.Q = Q
        self.Q_hyp = Q * self.hyp_exch # Hyporheic discharge

        if Q < 0.003: #Channel is going dry
            self.Log.write("The channel is going dry at %s, model time: %s." % (self, Chronos.TheTime))

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
        if dt >= (2 * K * (1 - X)):  #Unstable - Decrease dt or increase dx
            raise Exception("Unstable timestep. K=%0.3f, X=%0.3f, tests=(%0.3f, %0.3f)" % (K,X,test0,test1))

        # These calculations are from Chow's "Applied Hydrology"
        D = K * (1 - X) + 0.5 * dt
        C1 = (0.5*dt - K * X) / D
        C2 = (0.5*dt + K * X) / D
        C3 = (K * (1 - X) - 0.5*dt) / D
        # TODO: reformulate this using an updated model, such as Moramarco, et.al., 2006
        return C1, C2, C3
