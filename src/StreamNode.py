from __future__ import division
import math
from Utils.IniParams import IniParams
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator

class StreamNode(object):
    """Definition of an individual stream segment"""
    def __init__(self, **kwargs):
        self.IniParams = IniParams.getInstance()

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
                 'Area_Wetland','Q_Out_Total','Q_Control_Total']
        # Set all the attributes to zero, or set from the constructor
        for attr in attrs:
            x = kwargs[attr] if attr in kwargs.keys() else 0
            setattr(self,attr,x)

        # Some variables that had two values
        lsts = ['AreaX','Depth','Q','T','Velocity']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else [0,0]
            setattr(self, attr, x)

        # Variables that are lists
        lsts = ['Q_In','Cont_Wind','Cont_Humidity','Cont_Air_Temp']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else []
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

    def CalcInitialCond(self, Q_BC, Flag_BC=False):
        if Flag_BC:
            self.Q[0] = Q_BC[0]
        else:
            if self.Q_Control != 0:
                self.Q[0] = self.Q_Control
            else:
                self.Q[0] = self.Upstream.Q[0] + self.Q_In