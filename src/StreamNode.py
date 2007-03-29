from __future__ import division
import math,wx
from warnings import warn
from scipy.optimize.minpack import newton
from Utils.IniParams import IniParams
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.BoundCond import BoundCond
from Utils.AttrList import TimeList
from Utils.Maths import NewtonRaphson
from StreamChannel import StreamChannel

class StreamNode(StreamChannel):
    """Definition of an individual stream segment"""
    # Define members in __slots__ to ensure that later member names cannot be added accidentally
    __slots__ = ["Embeddedness","Conductivity","ParticleSize","Porosity",  # From Morphology Data sheet
                 "Aspect","Topo_W","Topo_S","Topo_E","Latitude","Longitude","Elevation", # Geographic params
                 "FLIR_Temp","FLIR_Time", # FLIR data
                 "T_cont","T_sed","T_in", # Temperature attrs
                 "VHeight","VDensity",  #Vegetation params
                 "Wind","Humidity","T_air", # Continuous data
                 "IniParams","Zone","BC", # Initialization parameters, Zonator and boundary conditions
                 "View_To_Sky"
                 ]
    def __init__(self, **kwargs):
        StreamChannel.__init__(self)
        # Set all the attributes to bare lists, or set from the constructor
        for attr in self.__slots__:
            x = kwargs[attr] if attr in kwargs.keys() else None
            setattr(self,attr,x)
        for attr in ["Wind","Humidity","T_air"]:#,"FLIR"]:
            setattr(self,attr,TimeList())
        self.IniParams = IniParams.getInstance()
        self.BC = BoundCond.getInstance() # Class to hold various boundary conditions
        # Set discharge boundary conditions for the StreamChannel
        self.Q_bc = self.BC.Q

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

    def __eq__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km == cmp
    def __ne__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km != cmp
    def __gt__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km > cmp
    def __lt__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km < cmp
    def __ge__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km >= cmp
    def __le__(self, other):
        cmp = other.km if isinstance(other,StreamNode) else other
        return self.km <= cmp

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

    def Initialize(self):
        """Methods necessary to set initial conditions of the node"""
        self.ViewToSky()
        self.SetBankfullMorphology()

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
                Dummy2 = self.IniParams.TransSample * (Z - 0.5) - OH
                if Dummy2 <= 0:
                    Dummy2 = 0.0001
                LC_Angle = (180 / math.pi) * math.atan(Dummy1 / Dummy2) * self.Zone[D][Z].VDensity
                if Z == 1:
                    LC_Angle_Max = LC_Angle
                if LC_Angle_Max < LC_Angle:
                    LC_Angle_Max = LC_Angle
            VTS_Total = VTS_Total + LC_Angle_Max
        self.View_To_Sky = (1 - VTS_Total / (7 * 90))

    def CalcHydraulics(self, time):
        # Convenience variables
        dt = self.IniParams.dt
        dx = self.dx
        # Iterate down the stream channel, calculating the discharges
        self.CalculateDischarge(time)

        ################################################################
        ### This section seems unused in the original code. It calculates a stratification
        # tendency factor. We can implement it (possibly in StreamChannel) if we need to
#        #===================================================
#        #Calculate tendency to stratify
#        try:
#            self.Froude_Densiometric = math.sqrt(1 / (9.8 * 0.000001)) * dx * self.Q[1] / (self.Depth[1] * self.AreaX[1] * dx)
#        except:
#            print self.Depth, self.AreaX, dx
#            raise
#        #===================================================
#        else: #Skip Node - No Flow in Channel
#            self.Hyporheic_Exchange = 0
#            self.T[0] = 0
#            self.Froude_Densiometric = 0

        #===================================================
        #Check to see if wetted widths exceed bankfull widths
        #TODO: This has to be reimplemented somehow, because Excel is involved
        # connected to the backend. Meaning this class has NO understanding of what the Excel
        # spreadsheet is. Thus, something must be propigated backward to the parent class
        # to fiddle with the spreadsheet. Perhaps we can write a report to a text file or
        # something. I'm very hesitant to connect this too tightly with the interface.
        Flag_StoptheModel = False
        if self.W_w > self.W_bf and not self.IniParams.ChannelWidth:

            I = self.km - dx / 1000
            II = self.km
            msg = "The wetted width is exceeding the bankfull width at %s.  To accomodate flows, the BF X-area should be or greater. Select 'Yes' to continue the model run (and use calc. wetted widths) or select 'No' to stop this model run (suggested X-Area values will be recorded in Column Z in the Morphology Data worksheet)  Do you want to continue this model run?" % self.__class__.__name__
            dlg = wx.MessageDialog(None, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_OK:
                # Put this in a public place so we don't ask again.
                self.IniParams.Flag_ChannelWidth = True
                Flag_StoptheModel = False
            else:    #Stop Model Run and Change Input Data
                Flag_StoptheModel = True
                self.IniParams.ChannelWidth = True
            dlg.Destroy()
#        if Flag_StoptheModel:
#            I = 0
#            while self[(17 + I, 5),"Morphology Data"] < self.km
#                I += 1
#            Dummy = self[17, 5) - Sheet1.Cells(18, 5)
#            For II = I - CInt(dx / (Dummy * 1000)) To I
#                If II >= 0 Then Sheet1.Cells(17 + II, 26) = Round(AreaX(Node, 1) + 0.1, 2)
#            Next II
