from __future__ import division
import math,wx
from scipy.optimize.minpack import newton
from Utils.IniParams import IniParams
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.BoundCond import BoundCond
from Utils.AttrList import TimeList

class StreamNode(object):
    """Definition of an individual stream segment"""
    def __init__(self, **kwargs):
        self.IniParams = IniParams.getInstance()
        self.BC = BoundCond.getInstance() # Class to hold various boundary conditions
        # Attributes, which are either values from the spreadsheet if distance step
        # equals the longitudinal sample rate, or averages if the distance step is
        # a multiple of the sample rate.
        # TODO: There are possibly meaningless attributes here.
        # For instance, Q_Out and Q_Out_Total. It may not be necessary to have both,
        # but we need to find out what they do.
        attrs = ['RiverKM', 'Slope','N','Width_BF','Width_B','Depth_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','T_Accretion','Elevation','BFWidth','WD','Temp_Sed',
                 'Area_Wetland','Q_Out_Total','Q_Control_Total','Rh','Pw']
        # Set all the attributes to zero, or set from the constructor
        for attr in attrs:
            x = kwargs[attr] if attr in kwargs.keys() else 0
            setattr(self,attr,x)

        self.km = self.RiverKM # create an attribute for sorting in the PlaceList object.
        self.prev_km = None# Upstream Node
        self.next_km = None# Downstream Node

        # Some variables that had two values
        lsts = ['AreaX','Depth','Q','T','Velocity']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else [0,0]
            setattr(self, attr, x)

        # Variables that are lists
        lsts = ['Q_In']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else []
            setattr(self, attr, x)
        
        # TimeList objects to hold continuous data
        lsts = ['Cont_Wind','Cont_Humidity','Cont_Air_Temp']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else TimeList()
            setattr(self, attr, x)

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

    def __repr__(self):
        return '%s @ %.3f km' % (self.__class__.__name__, self.RiverKM)
    def __eq__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM == cmp
    def __ne__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM != cmp
    def __gt__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM > cmp
    def __lt__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM < cmp
    def __ge__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM >= cmp
    def __le__(self, other):
        cmp = other.RiverKM if isinstance(other,StreamNode) else other
        return self.RiverKM <= cmp

    def __iter__(self):
        """Iterator that cycles through the zonator

        This method returns a tuple (i,j,zone) where i is the cardinal direction of the
        Zonator instance (0-6) and j is the zone number (0-4). zone is the actual zone
        instance so that the following syntax can be used:

        >>> SN = StreamNode()
        >>> for i,j,zone in SN:
        >>>     print i, j, zone
        0 0 VZ:(0, 0, 0, 0, 0)
        0 1 VZ:(0, 0, 0, 0, 0)
        0 2 VZ:(0, 0, 0, 0, 0)
        0 3 VZ:(0, 0, 0, 0, 0)
        0 4 VZ:(0, 0, 0, 0, 0)
        1 0 VZ:(0, 0, 0, 0, 0)
        1 1 VZ:(0, 0, 0, 0, 0)
        ...
        """
        for i in xrange(7):
            for j in xrange(5):
                yield i,j,self.Zone[i][j]

    # This is a property-based attribute holding a reference to the upstream and the downstream
    # neighbor
    def GetUp(self): return self.__UP
    def GetDn(self): return self.__DN
    def SetUp(self, node):
        if node: # Node can be 'None' meaning we are most upstream node
            if not isinstance(node, StreamNode): raise Exception("Value must be a StreamNode instance")
        self.__UP = node
    def SetDn(self, node):
        if node: # Node can be 'None' meaning we are most downstream node
            if not isinstance(node, StreamNode): raise Exception("Value must be a StreamNode instance")
        self.__DN = node
    Upstream = property(GetUp, SetUp)
    Downstream = property(GetDn, SetDn)
    def GetQ(self):
        """Return value of Q calculated from current conditions"""
        return (1/self.n)*self.A*(self.Rh**(2/3))*(self.S**(1/5))
    Q_calc = property(GetQ)

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
                Dummy2 = self.dx * (Z - 0.5) - OH
                if Dummy2 <= 0:
                    Dummy2 = 0.0001
                LC_Angle = (180 / math.pi) * math.atan(Dummy1 / Dummy2) * self.Zone[D][Z].VDensity
                if Z == 1:
                    LC_Angle_Max = LC_Angle
                if LC_Angle_Max < LC_Angle:
                    LC_Angle_Max = LC_Angle
            VTS_Total = VTS_Total + LC_Angle_Max
        self.View_To_Sky = (1 - VTS_Total / (7 * 90))

    def CalcIC(self, Q_BC, T_BC):
        # IC for flow
        if not self.Upstream: # Are we the most upstream node?
            self.Q[0] = Q_BC[0]
        else:
            if self.Q_Control != 0:
                self.Q[0] = self.Q_Control
            else:
                self.Q[0] = self.Upstream.Q[0] + self.Q_In[0] + self.Q_Accretion - self.Q_Out
        self.Q[1] = self.Q[0]
        # IC for Temperature
        if Flag_HS == 1:
            self.T[0] = self.t[1] = self.Temp_Sed = self.T_BC[0]
        # IC for Hydraulics
        self.Q[0] = self.Q_Control if self.Q_Control else self.Q[0]
        self.Depth[0] = self.D_Control if self.D_Control else self.Depth[0]

        # Depth IC
        # With Control Depth
        Flag_SkipNode = False
        if self.D_Control:
            # Calculate the area, which is, at this point, still calculated as bankfull
            # area because bottom width has not been changed at this point and has been
            # calculated using bankfull width.
            # ASSUMPTION: Cross-sectional area is calculated using bankfull width
            # Look at Chow's Open Channel Hydraulics, Table 2-1 for details on these equations
            self.AreaX[0] = self.Depth[0] * (self.Width_B + self.Z * self.Depth[0])
            # Wetted Perimeter
            self.Pw = self.Width_B + 2 * self.Depth[0] * math.sqrt(1 + self.Z**2)
            self.Pw = 0.00001 if self.Pw <= 0 else self.Pw
            self.Rh = self.AreaX[0] / self.Pw
            Flag_SkipNode = False

        #No Control Depth
        else:
            if self.theSlope <= 0:
                raise Exception("Slope cannot be less than or equal to zero unless you enter a control depth.")
            self.Depth[0] = self.Upslope.Depth[0] if self.Upslope else 1
            if self.Q[0] < 0.0071: #Channel is going dry
                Flag_SkipNode = True
                self.T_Last = self.T[0] # What is this?
                if not self.IniParams.DryChannel:
                    msg = "The channel is going dry at %s.  The model will either skip these 'dry stream segments' or you can stop this model run and change input data.  Do you want to continue this model run?" % self
                    dlg = wx.MessageDialog(self, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
                    if dlg.ShowModal() == wx.ID_OK:
                        self.IniParams.DryChannel = True
                    else:
                        raise Exception("Dry channel, model run ended by user")
                    dlg.Destroy()
            else:    #Channel has sufficient flow
                Flag_SkipNode = False
        SetWettedDepth(Flag_SkipNode)

    def SetWettedDepth(self, zero=False):
        """Use Newton-Raphson method to calculate wetted depth from current conditions

        Details on this can be found in the HeatSource manual Sec. 3.2.
        More general details on the technique can be found in Applied Hydrology
        in section 10.4.
        This method uses the newton() function from SciPy because it is highly optimized
        and very fast. Rather than do this entire calculation by hand, we just send the
        function to newton() and get an answer. The only problem is that without a
        defined derivative function, the secant method is used, which is slightly
        less accurate than the tangent method. It shouldn't matter, but if it does, we
        can add a derivative function
        """
        # The original code tested whether we skipped a particular node and set everything
        # to zero if we did. That functionality is kept here just in case.
        # TODO: Remove this if it's not necessary.
        if zero:
            Q_Est = 0
            self.Depth[0] = 0
            self.AreaX[0] = 0
            self.Pw = 0
            self.Rh = 0
            self.Width = 0
            self.DepthAve = 0
            self.Velocity[0] = 0
            self.Q[0] = 0
            self.Celerity = 0
            return
        # Some lambdas to use in the calculation
        A = lambda x: x * (self.Width_B + self.Z * x) # Cross-sectional area
        Pw = lambda x: self.Width_B + 2 * x * math.sqrt(1+self.Z**2) # Wetted Perimeter
        Rh = lambda x: A(x)/Pw(x) # Hydraulic Radius
        # The function def is given in the HeatSource manual Sec 3.2
        Yj = lambda x: A(x) * (Rh(x)**(2/3)) - ((self.Q[0]*self.N)/(self.Slope**(1/2))) # f(y)
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

        self.Depth[0] = depth
        self.AreaX[0] = A(depth)
        self.Velocity[0] = self.Q[0] / self.AreaX[0]
        self.Width = self.Width_B + 2 * self.Z * self.Depth[0]
        self.Celerity = self.Velocity[0] + math.sqrt(9.861 * self.Depth[0])
        # NOTE: Check whether it is safe to always ensure this check can always be performed.
        # In the original code, dt was set to dx/celerity if certain conditions were true, the
        # main one is the if statement below. Because of the relationship between celerity, dx
        # and dt (see Chow's 'Open Channel Hydraulics' sec. 18-6), I'm assuming this shouldn't
        # fail. This may be an invalid assumption if I turn out to be a dolt.
        if self.IniParams.dt > dx / self.Celerity:
            #dt = dx / self.Celerity
            raise Exception("Timestep needs adjustment (Possible error in Programming)")
