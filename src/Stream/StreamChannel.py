from __future__ import division
import math
from warnings import warn
from itertools import imap
from Utils.Maths import NewtonRaphson

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
        slots = ["S",        # Slope
                 "n",        # Manning's n
                 "W_bf",     # Bankfull width (surface)
                 "z",        # z factor: Ration of run to rise of the side of a trapazoidal channel
                 "d_bf",     # Bankfull Depth, See below or HeatSource manual
                 "d_ave",    # Average bankfull depth, calculated as W_bf/WD
                 "d_w",      # Wetted depth. Calculated in GetWettedDepth()
                 "d_cont",   # Control depth
                 "W_b",      # Bottom width, calculated as W_bf - (2 * d_bf * z)
                 "W_w",      # Wetted width, calculated as W_b + 2*z*d_w
                 "A",        # Cross-sectional Area, calculated d_w * (W_b + z * d_w)
                 "P_w",      # Wetted Perimeter, calculated as W_b + 2 * d_w * sqrt(1 + z**2)
                 "R_h",      # Hydraulic Radius, calculated as A_x/P_w
                 "WD",       # Width/Depth ratio, constant
                 "dx",       # Length of this stream reach.
                 "U",        # Velocity from Manning's relationship
                 "Q",        # Discharge, from Manning's relationship
                 "Q_prev",   # Discharge at previous timestep, previous space step is taken from another node
                 "Q_cont",   # Control discharge
                 "V",        # Total volume, based on current flow
                 "Q_tribs",  # Inputs from tribs. This is a TimeList class object
                 "Q_in",     # Inputs from "accretion" in cubic meters per second
                 "Q_out",    # Withdrawls from the stream, in cubic meters per second
                 "Q_hyp",    # Hyporheic flow
                 "km",       # River kilometer, from mouth
                 "next_km",  # Reference to next (downstream) river channel instance (Set externally)
                 "prev_km",  # Reference to prevous (Upstream) river channel instance (also set externally)
                 "Q_bc",      # Boundary conditions, in a TimeList class, for discharge.
                 "E",        # Evaporation rate (currently unused)
                 "dt",        # This is the timestep (for kinematic wave movement, etc.)
                 "phi",      # Porosity of the bed
                 "K_h"      # Horizontal bed conductivity
                 ]
        for attr in slots:
            setattr(self,attr,None)
    def __repr__(self):
        return '%s @ %.3f km' % (self.__class__.__name__, self.km)

    def GetInputs(self, t=None):
        """Returns a value for inputs-outputs to the channel at the time=t"""
        Q = 0
        Q += self.Q_in or 0 # Input volume
        Q -= self.Q_out or 0 # Output volume
        try:
            Q += self.Q_tribs[t,-1]# Tributary volume
        except TypeError: pass
        if self.E: # Evaporation volume
            Q -= self.E * self.dx * self.W_w
        return Q

    def CalculateDischarge(self, t=None):
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
        # Check if we are a spatial or temporal boundary node
        if self.prev_km and self.Q_prev: # No, there's an upstream channel and a previous timestep
            # Get the tuples for C and Q values, multiply the each C by the cooresponding Q, then sum it up
            Q = sum(imap(lambda x,y:x*y,self.GetMuskingum(),self.GetKnownDischarges()))

        elif not self.prev_km: # We're a spatial boundary, use the boundary condition
            # At spatial boundaries, we return the boundary conditions from Q_bc
            Q = self.Q_bc[t,-1] # Get the value at this time, or the closest previous time
            # TODO: Might want some error checking here.
        elif not self.Q_prev: # There's an upstream channel, but no previous timestep.
            # In this case, we sum the incoming flow which is upstream's current timestep plus inputs.
            Q_in = self.GetInputs(t) # Add up our inputs to this segment
            Q = self.prev_km.Q + Q_in
        else: raise Exception("WTF?")

        # Now we've got a value for Q(t,x), so the current Q becomes Q_prev.
        try:
            self.Q_prev = self.Q
        except AttributeError: # If there's no Q, then we are here for the first time. Set to Boundary Condition
            self.Q_prev = self.Q_bc[t,-1]
        self.Q = Q

        if Q < 0.0071: #Channel is going dry
            warn("The channel is going dry at %s." % self)
            self.d_w, self.A, self.P_w, self.R_h, self.W_w, self.U = [0]*6  # Set variables to zero (from VB code)
            return

        # That's it for discharge, let's recalculate our channel geometry, hyporheic flow, etc.
        self.CalcGeometry()
        self.CalcHyporheic()

    def GetKnownDischarges(self):
        """Returns the known discharges necessary to calculate current discharge

        This method returns a tuple of discharge values used in calculations. To calculate
        our current discharge at this timestep (t) and space step (x) we need three
        values, one value is our discharge from the last space step (t,x-1), which is
        essentially the outflow of the upslope cell at this timestep; one is
        the discharge of the last time step (t-1,xj); and the third is the flow from the last
        time AND space step (t-1,x-1). This method knows how to retrieve these
        values and returns a tuple in the form of (Q1,Q2,Q3,Q4) where Q1 is the last space step,
        Q2 is the last time AND space step, and Q3 is the last time step. Q4 is either a lateral
        discharge, if it will be calculated by a muskingum coefficient, or 1 if the discharge
        is included in the muskingum coefficient itself. The order of these corresponds to the
        order in which the Muskigum coefficients are returned
        in GetMuskigum, and also to the order in which they are defined in "Applied Hydrology."
        This method assumes that we are at neither a spatial or temporal boundary, and should
        be called accordingly.
        """
        # (t, x-1) = flow from the upstream channel at this timestep
        Q1 = self.prev_km.Q
        # Then we make sure it's been calculated- in case there's a problem with the code
        if Q1 is None: raise Exception("Previous channel of %s has no discharge calculation" % self)

        # (t-1, x-1) = flow from the upstream channel's previous timestep.
        Q2 = self.prev_km.Q_prev
        if Q2 is None: raise Exception("Previous channel of %s has no previous discharge calculation" % self)

        # (t-1, x) = flow from the previous timestep in this channel
        Q3 = self.Q_prev
        if Q3 is None: raise Exception("Channel %s has no previous discharge calculation" % self)

        return Q1,Q2,Q3,1

    def CalcGeometry(self, Q_est=None):
        """Calculate all morphological characteristics that are flow dependent

        This method takes a discharge value, Q_est, and uses GetWettedDepth() to get
        a depth value that is then used to calculate all depth dependent channel
        characteristics.
        """
        Q_est = Q_est or self.Q
        # Set using control depth or GetWettedDepth
        if self.d_cont:
            dw = self.d_cont
        else:
            if not self.S: raise Exception("Must have a control depth with zero slope")
            dw = self.GetWettedDepth(Q_est)

        self.d_w = dw
        self.A = dw + (self.W_b + self.z*dw)
        self.P_w = self.W_b + 2 * dw * math.sqrt(1+self.z**2)
        self.R_h = self.A/self.P_w
        self.W_w = self.W_b + 2 * self.z * dw
        self.U = Q_est / self.A

    def GetMuskingum(self, Q=None):
        """Return the values for the Muskigum routing coefficients
        using current timestep and optional discharge"""
        # Taken from the VB source.
        if not self.W_w:
            pass
        try:
            A = self.Q / (2 * self.W_w * self.S)
        except ZeroDivisionError, err:
            print err.args, err.message, err.__class__.__name__
            raise
        B = (5/3) * self.U * self.dx
        X = 0.5 * (1 - A / B)
        if X > 0.5: X = 0.5
        elif X < 0.0: X = 0.0
        K = self.dx / ((5 * self.U) / 3) # Wave celerity
        dt = self.dt

        # Check the celerity to ensure stability
        test = 2 * K * (1 - X)
        if dt > test: raise Exception("Unstable timestep. dt should be less than %0.3f" % test/60)

        # These calculations are from Chow's "Applied Hydrology"
        D = 2 * K * (1 - X) + dt
        C1 = (dt - 2 * K * X) / D
        C2 = (dt + 2 * K * X) / D
        C3 = (2 * K * (1 - X) - dt) / D
        # For the lateral inflow (C4), we need [l/t], given as the input depth for the channel. Thus,
        # we divide the input inflows in cms by the channel length times one unit. This gives us a
        # rate for lateral inflow per unit length of stream. The formula in Bedient and Huber for the
        # inflow is (q*dt*dx)/D. This would mean that we divide Q/dx=q (because dx*1=dx) then
        # remultiply by dx. We save a step here by only multiplying Q*dt and achieve the same
        # result (plus something like 3.5e-16 seconds too! :)
        # TODO: reformulate this using an updated model, such as Moramarco, et.al., 2006
        C4 = (self.GetInputs()*dt)/D
        test = C1 + C2 + C3
        if 1-test > 0.015: warn("Muskigum coefficents (C1: %0.3f, C2: %0.3f, C3: %0.3f) not at unity in %s" %(C1,C2,C3,self))
        return C1, C2, C3, C4


    def SetBankfullMorphology(self):
        """Calculate initial morphological characteristics in terms of W_bf, z and WD"""
        if self.z >= self.WD/2:
            raise Warning("Reach %s has no bottom width. Z: %0.3f, WD:%0.3f. Recalculating Channel angle." % (self, self.z, self.WD))
            z = 0.99 * (self.WD/2)

        # Estimate depth of the trapazoid from the width/depth ratio
        self.d_ave = self.W_bf/self.WD
        # Calculated the bottom of the channel by subtracting the differences between
        # Top and bottom of the trapazoid
        self.W_b = self.W_bf - (2 * self.d_ave * self.z)
        # Calculate the area of this newly estimated trapazoid. This will get reset when the
        # wetted depth changes
        self.A = (self.z * self.d_ave) * ((self.W_b + self.W_bf)/2)
        w = (self.W_bf - self.W_b)/self.W_bf
        self.d_bf = self.d_ave/(w + ((1-w)/2))

    def GetWettedDepth(self, Q_est=None):
        """Use Newton-Raphson method to calculate wetted depth from current conditions

        Details on this can be found in the HeatSource manual Sec. 3.2.
        More general details on the technique can be found in Applied Hydrology
        in section 10.4.
        This method uses the NewtonRaphson method defined in Maths. It requires the
        derivative of the function, but we go ahead and work that out because using the
        derivative is more accurate and faster (programatically) than the secant method
        used in the original code.
        """
        if not Q_est: raise Exception("Method must be called with estimated discharge")
        if not self.W_b: raise Exception("Bankfull morphology must be set before calculations can be performed")
        z = self.z
        W = self.W_b
        # The function def is given in the HeatSource manual Sec 3.2... in three sections
        first = lambda x: x * (W + z * x) # Cross-sectional area formula
        second = lambda x: x * ((W + z * x) / (W + 2 * x * math.sqrt(1+(z**2))))**(2/3) # Hydraulic Radius to the 2/3,
        # The functional definition of wetted depth:
        Fd = lambda x: first(x) * second(x) - ((Q_est*self.n)/(self.S**(1/2)))
        # Here is the formula in terms of x, where x is the wetted depth.
        # (x*(w+(z*x))*((x*(w+(z*x)))/(w+(2*x*sqrt(1+z^2))))^(2/3))-((Q*n)/(s^(1/2)))
        # This can be used to calculate the derivative using software such as that on
        # http://wims.unice.fr/wims/ which will calculate derivatives online. Not that I'm too lazy
        # to do it myself or anything.

        # Here is the derivative of the equation in sections.
        first = lambda x: (5 * (x**(2/3)) * (x*z+W)**(5/3)) / (3*((2*x*math.sqrt((z**2)+1)+W)**(2/3)))
        second = lambda x: (5 * (x**(5/3)) * z * ((x*z+W)**(2/3))) / (3*((2*x*math.sqrt((z**2)+1)+W)**(2/3)))
        third = lambda x: (4 * (x**(5/3)) * (x*z+W)**(5/3) * math.sqrt(z**2+1)) / (3*((2*x*math.sqrt((z**2)+1)+W)**(5/3)))

        Fdd = lambda x: first(x) + second(x) - third(x)

        # Our Newton-Raphson method uses bracketing and binary search methods to dial down the function's zero.
        # Since we don't know our brackets each time, we make one up here, and assume that no stream is more than
        # 20 meters deep. We CAN put these minimum and maximum values in the IniParams class just to make things
        # easier to change, but until we know we need to, they will be left here.
        try:
            return NewtonRaphson(Fd, Fdd, 0, 50) # Assume minimum (0) and maximum (20) meters in depth
        except:
            print "Failure to converge on a depth. Check minimum and maximum values defined in this method."
            raise

    def CalcHyporheic(self):
        """Calculate the hyporheic exchange value"""
        # Taken directly from the VB code
        #======================================================
        #Calc hyporheic flow in cell Q(0,1)
        #Calculate head at top (ho) and bottom (hL) of reach
        if not self.prev_km:
            ho = self.S * self.dx
            hL = 0
        else:
            try:
                ho = self.prev_km.d_w + self.S * self.dx
            except:
                print self.S, self.prev_km.d_w
                raise
            hL = self.d_w
        #Calculate Hyporheic Flows
        self.Q_hyp = abs(self.phi * self.P_w * self.K_h * (ho ** 2 - hL ** 2) / (2 * self.dx))
        self.Q_hyp = self.Q if self.Q_hyp > self.Q else self.Q_hyp