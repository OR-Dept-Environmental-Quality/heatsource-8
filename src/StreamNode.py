from __future__ import division

class StreamNode(object):
    """Definition of an individual stream segment"""
    def __init__(self, **kwargs):

        #Set up some variables that define the stream node. Technically, these needn't be defined
        # here beacuse we can assign attributes on the fly, but we place them here to document them
        #TODO: Re-evaluate the OOP-ness of this class.

        # These are variables that have some sort of average calculated in the original
        # VB code subroutine called SubLoadModelVariables
        the_attrs = ['RiverKM', 'Slope','N','Width_BF','Width_B','Width_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','T_Accretion','Elevation']
        # These are attributes not used in the averages calculations
        # TODO: Variables that come from the menu (i.e. same for all nodes) should be in a singleton class.
        other_attrs = ['BFWidth','WD','dx','Dx_lc',] #TODO: Get the transfer sample rate input here from the menu
        l = map(the_attrs,lambda x: 'the'+x) # return theATTR for all ATTR in the_attrs
        attrs = the_attrs + other_attrs + l # All attributes

        for attr in attrs: # Set all the attributes to zero, or set from the constructor
            x = kwargs[attr] if attr in kwargs.keys() else 0
            setattr(self,attr,x)

        # Zone get's set differently
        self.Zone = None # This gets built elsewhere
        # theZone should be set to zeroed values
        dir = [] # List to save the seven directions
        for Direction in xrange(1,8):
            z = () #Tuple to store the zones 0-4
            for Zone in xrange(0,5):
                if Zone == 0:
                    #TODO: See what this storage of elevation is used for, because it is also used above.
                    z += VegZone(), #Overhang and Elevation
                    continue #No need to do any more for 0th zone
                z += VegZone(),
            dir.append(z) # append to the proper direction
        self.theZone = Zonator(*dir) # Create a Zonator instance and set the node.Zone attribute

        if self.dx and self.WD: self.CheckDx()


    def __repr__(self):
        if self.RiverKM:
            return '%s @ %.3f km' % (self.__class__.__name__, self.RiverKM)
        else: return self.__class__.__name__
    def CheckDx(self):
        # bottom depth cannot be zero, which will happen if the equation:
        # BFWidth - (2 * dx * depth) <= 0
        # Substituting BFWidth/WD for depth and solving for dx or depth tells us that
        # this case will be true when dx >= WD/2. Thus, we test for this case and deal with it
        # up front.
        if self.dx >= self.WD/2:
            raise Warning("Reach has no bottom width! Recalculating Channel angle.")
            self.dx = 0.99 * (self.WD/2)

    def BFMorph():
        """Calculate cross-sectional channel morphology

        Assumes a trapazoidal channel and calculates the average depth, cross-sectional area
        and bottom width"""
        # Estimate depth of the trapazoid from the width/depth ratio
        self.AveDepth = self.BFWidth/self.WD
        # Calculated the bottom of the channel by subtracting the differences between
        # Top and bottom of the trapazoid
        self.BottomWidth = self.BFWidth - (2 * self.AveDepth * self.dx)
        # Calculate the area of this newly estimated trapazoid
        # TODO: implement if needed:
        #self.BFXArea = (self.BottomWidth + (self.dx * self.AveDepth)) * self.AveDepth

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

