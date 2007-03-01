from __future__ import division
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
        attrs = ['RiverKM', 'Slope','N','Width_BF','Width_B','Depth_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','T_Accretion','Elevation','BFWidth','WD','Temp_Sed']
        # Set all the attributes to zero, or set from the constructor
        for attr in attrs:
            x = kwargs[attr] if attr in kwargs.keys() else 0
            setattr(self,attr,x)

        # Some variables that had two values
        lsts = ['AreaX','Depth','Q','T','Velocity']
        for attr in lsts:
            x = xwargs[attr] if attr in kwargs.keys() else [0,0]
            setattr(self, attr, x)

        # This is a Zonator instance, with 7 directions, each of which holds 5 VegZone instances
        # with values for the sampled zones in each directions
        self.Zone = None

        self.dx = self.IniParams.Dx
        if self.dx and self.WD: self.checkDx()

    def __repr__(self):
        return '%s @ %.3f km' % (self.__class__.__name__, self.RiverKM)

    def checkDx(self):
        # bottom depth cannot be zero, which will happen if the equation:
        # BFWidth - (2 * dx * depth) <= 0
        # Substituting BFWidth/WD for depth and solving for dx or depth tells us that
        # this case will be true when dx >= WD/2. Thus, we test for this case and deal with it
        # up front.
        if self.dx >= self.WD/2:
            raise Warning("Reach has no bottom width! Recalculating Channel angle.")
            self.dx = 0.99 * (self.WD/2)

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

    def ViewtoSky(self, Flag_HS):
        if Flag_HS == 1 or Flag_HS == 2:
            #======================================================
            #Calculate View to Sky
            VTS_Total = 0
            for Direction in xrange(1,8):
                LC_Angle_Max = 0
                for Zone in xrange(5):
                    if Zone == 0: OH = self.theZone[Direction][Zone]
                    else: OH = 0
                    Dummy1 = self.theZone[Direction][Zone].VHeight + self.theZone[Direction][Zone].SlopeHeight
                    Dummy2 = Dx_lc * (Zone - 0.5) - OH #Dx_lc is the transverse sample rate from the main menu.
                    if Dummy2 <= 0: Dummy2 = 0.0001
                    LC_Angle = (180 / math.pi) * math.atan(Dummy1 / Dummy2) * self.theZone[Direction][Zone]
                    if Zone == 0: LC_Angle_Max = LC_Angle
                    if LC_Angle_Max < LC_Angle: LC_Angle_Max = LC_Angle
                VTS_Total = VTS_Total + LC_Angle_Max
            self.View_To_Sky = (1 - VTS_Total / (7 * 90))

