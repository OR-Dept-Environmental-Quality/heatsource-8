from __future__ import division

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
    def __init__(self, **kwargs):
        attrs = ['Slope',
                 'N',
                 'Width_BF',
                 'Width_B',
                 'Depth_BF',
                 'Z',
                 'X_Weight',
                 'Embeddedness',
                 'Conductivity',
                 'ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','T_Accretion','Elevation','BFWidth','WD','Temp_Sed',
                 'Area_Wetland','Q_Out_Total','Q_Control_Total', 'D_Control_Total',
                 'Rh','Pw']
        # Set all the attributes to zero, or set from the constructor
        for attr in attrs:
            x = kwargs[attr] if attr in kwargs.keys() else 0
            setattr(self,attr,x)

    def checkZ(self):
        # bottom depth cannot be zero, which will happen if the equation:
        # BFWidth - (2 * z * depth) <= 0
        # Substituting BFWidth/WD for depth and solving for dx or depth tells us that
        # this case will be true when z >= WD/2. Thus, we test for this case and deal with it
        # up front.
        if self.Z >= self.WD/2:
            raise Warning("Reach %s has no bottom width. Z: %0.3f, WD:%0.3f. Recalculating Channel angle." % (self, self.Z, self.WD))
            self.Z = 0.99 * (self.WD/2)

    def BFMorph(self):
        """Calculate cross-sectional channel morphology

        Assumes a trapazoidal channel and calculates the average depth, cross-sectional area
        and bottom width. The original VB code contained a couple of questionable loops
        These loops basically recalculated until the calculated cross-sectional area
        equalled the bankfull cross-sectional area. The outcome of this was that the area
        of the trapazoidal stream cross-section was calculated as a rectangle where the
        long edge was the bankfull width and the short edge was the average depth. This is
        larger than the true trapazoidinal shape. It didn't seem that this new, too large,
        cross-sectional area was actually used in the program, but it was spit out to the
        spreadsheet, so it's calculated here.
        """
        self.checkZ()

        # this was originally in the LoadModelVariables subroutine of the VB code, but it
        # makes more sense to do all the node-specific geomorph calculations here.
        self.Area_Wetland += self.Width_BF * self.dx

        # Similarly, this was in LoadModelVariables, but might as well be here.
        # This subtracts the elevation of the 0th node from the elevation of the
        # jth node. What we end up with is a number, called SlopeHeight in the original
        # VB, representing the difference between the stream elevation and the zone's elevation
        for i,j,node in self:
            if not j: pass # Skip if we are the 0th node.
            node.SlopeHeight = node.Elevation - self.Zone[i][0].Elevation
            # ASSUMPTION: We make an assumption that the zone's elevation cannot be less than the
            # stream's elevation. Not necessarily a valid assumption, but potentially unharmful.
            node.SlopeHeight = node.SlopeHeight if node.SlopeHeight > 0 else 0

        # Estimate depth of the trapazoid from the width/depth ratio
        self.AveDepth = self.BFWidth/self.WD
        # Calculated the bottom of the channel by subtracting the differences between
        # Top and bottom of the trapazoid
        self.BottomWidth = self.BFWidth - (2 * self.AveDepth * self.dx)
        # Calculate the area of this newly estimated trapazoid
        self.BFXArea = (self.BottomWidth + (self.dx * self.AveDepth)) * self.AveDepth
        # NOTE: What follows is a strange calculation of the max depth, that was taken from
        # the original VB code. It basically increases depth until the area equals the
        # area of the bankfull rectangle (see the note in the docstring). This is not
        # an accurate representation of the maximum bankfull depth, but is included for
        # legacy reasons.
        BW = self.BottomWidth
        D_Est = self.AveDepth
        XArea = BW / self.WD
        # Here, we add to depth until the area equals the bankfull area.
        while True:
            Delta = (XArea - (BW + self.Z * D_Est) * D_Est)
            if Delta < 0.0001: break
            D_Est += 0.01
        self.MaxDepth = D_Est

    def GetWettedDepth(self, Q_est=None):
        """Use Newton-Raphson method to calculate wetted depth from current conditions

        Details on this can be found in the HeatSource manual Sec. 3.2.
        More general details on the technique can be found in Applied Hydrology
        in section 10.4.
        """
        Q = Q_est or self.Q[0]
        # Some lambdas to use in the calculation
        A = lambda x: x * (self.Width_B + self.Z * x) # Cross-sectional area
        Pw = lambda x: self.Width_B + 2 * x * math.sqrt(1+self.Z**2) # Wetted Perimeter
        Rh = lambda x: A(x)/Pw(x) # Hydraulic Radius
        # The function def is given in the HeatSource manual Sec 3.2
        Yj = lambda x: A(x) * (Rh(x)**(2/3)) - ((Q*self.N)/(self.Slope**(1/2))) # f(y)
        # get the results of SciPy's Newton-Raphson iteration
        # Notes:
        # fprime is the derivative of the function- this is something we might consider
        # args is something that I'm not sure of... perhaps arguments to the function?
        # tol is the error tolerance.
        # maxiter is the maximum number of iterations to try before re-trying.
        # There could be some error checking done here if it was necessary, for example, putting
        # this function call in a try/except block to test for a ValueError or other exception that
        # is returned if the max iterations are reached. However, with the exception of craziness,
        # the function is not hairy enough to cause problems, and should converge within 10 steps
        depth = newton(Yj, 10, fprime=None, args=(), tol=1.48e-008, maxiter=500)

        (x*(w+(z*x))*((x*(w+(z*x)))/(w+(2*x*sqrt(1+z^2))))^(2/3))-((Q*n)/(s^0.5))
        warn("these should be given as a return value, since we need to set different things")
