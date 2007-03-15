from __future__ import division
import math,wx
from scipy.optimize.minpack import newton
from Utils.IniParams import IniParams
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.BoundCond import BoundCond
from Utils.AttrList import TimeList
from warnings import warn

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
        self.RiverKM = None
        self.Area_Wetland = 0
        self.Pw = 0
        self.Rh = 0
        attrs = ['Slope','N','Width_BF','Width_B','Depth_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','T_Accretion','Elevation','WD','Temp_Sed']
        # Set all the attributes to zero, or set from the constructor
        for attr in attrs:
            x = kwargs[attr] if attr in kwargs.keys() else []
            setattr(self,attr,x)

        self.km = self.RiverKM # create an attribute for sorting in the PlaceList object.
        self.prev_km = None# Upstream Node
        self.next_km = None# Downstream Node

        # Some variables that had two values
        lsts = ['AreaX','Depth','Q','T','Velocity']
        for attr in lsts:
            x = kwargs[attr] if attr in kwargs.keys() else [0,0]
            setattr(self, attr, x)

        # TimeList objects to hold continuous data
        lsts = ['Cont_Wind','Cont_Humidity','Cont_Air_Temp','Q_In','T_In']
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
    def GetUp(self): return self.prev_km
    def GetDn(self): return self.next_km
    Upstream = property(GetUp)
    Downstream = property(GetDn)
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
        self.AveDepth = self.Width_BF/self.WD
        # Calculated the bottom of the channel by subtracting the differences between
        # Top and bottom of the trapazoid
        self.BottomWidth = self.Width_BF - (2 * self.AveDepth * self.dx)
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

    def SetWettedDepth(self, Q_est=None):
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


        warn("these should be given as a return value, since we need to set different things")
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
        if self.IniParams.dt > self.dx / self.Celerity:
            #dt = dx / self.Celerity
            raise Exception("Timestep needs adjustment (Possible error in Programming)")

    def CalcStreamGeom(self, Q_est=None, failSlope=None):
        """Calculate the stream geometry

        failSlope is a boolean that tells us whether whe should allow a zero slope
        and calculate it as we calculate control depths, or whether we should fail when
        we encounter a slope of zero."""
        # IC for flow
        if not self.Upstream: # Are we the most upstream node?
            self.Q[0] = self.BC.Q[0]
        else:
            if self.Q_Control != 0:
                self.Q[0] = self.Q_Control
            else:
                self.Q[0] = self.Upstream.Q[0] + self.Q_In[0] + self.Q_Accretion - self.Q_Out
        self.Q[1] = self.Q[0]
        # IC for Temperature
        self.T[0] = self.T[1] = self.Temp_Sed = self.BC.T[0]
        # IC for Hydraulics
        self.Q[0] = self.Q_Control or self.Q[0]
        self.Depth[0] = self.D_Control or self.Depth[0]

        Q_est = Q_est or self.Q[0]

        # Depth IC
        # With Control Depth
        if self.D_Control or (self.D_Control and self.theSlope <= 0):
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
            self.Flag_SkipNode = False

        #No Control Depth
        else:
            self.Depth[0] = self.Upslope.Depth[0] if self.Upslope else 1
            if Q_est < 0.0071: #Channel is going dry
                self.Flag_SkipNode = True
                self.T_Last = self.T[0] # What is this?
                if not self.IniParams.DryChannel:
                    msg = "The channel is going dry at %s.  The model will either skip these 'dry stream segments' or you can stop this model run and change input data.  Do you want to continue this model run?" % self
                    dlg = wx.MessageDialog(self, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
                    if dlg.ShowModal() == wx.ID_OK:
                        self.IniParams.DryChannel = True
                    else:
                        raise Exception("Dry channel, model run ended by user")
                    dlg.Destroy()
                # Set the values to zero for a dry channel.
                self.Depth[0] = 0
                self.AreaX[0] = 0
                self.Pw = 0
                self.Rh = 0
                self.Width = 0
                self.DepthAve = 0
                self.Velocity[0] = 0
                self.Q[0] = 0
                self.Celerity = 0
                return # No need to run SetWettedDepth()
            else: self.Flag_SkipNode = False
        self.SetWettedDepth(Q_est)

    def CalcHydraulics(self, time):
        # Convenience variables
        dt = self.IniParams.dt
        dx = self.dx
        #======================================================
        #Calculate Initial Condition Hydraulics
        if self.Q_Control: self.Q[0] = self.Q_Control
        if self.D_Control: self.Depth[1] = self.D_Control
        if not self.Upstream:
            self.Q[0] = self.BC.Q[time,0] #index by time
            Q_In_0 = self.Q[0]
            Q_In_1 = self.Q[1]
            Q_Out_0 = self.Q[0]
            self.T[0] = self.BC.T[time,0] # index by time
        else:
            Q_In_0 = self.Upstream.Q[0]
            Q_In_1 = self.Upstream.Q[1]
            Q_Out_0 = self.Upstream.Q[0]

        #===================================================
        #Calculate flow volumes in reaches for both times
        # This is set to false in the standard model files. It's commented out here because
        # the Evap_Rate variable is set AFTER this subroutine is run in the original VB code.
        # Thus, in the first timestep, we have an Evap_Rate equal to whatever's in the buffer.
        # It's here mainly as a record.
        # if self.IniParams.Flag_EvapLoss:
        #     EvapVol = Evap_Rate * self.Width * self.dx
        Mix = self.Q_Accretion - self.Q_Out # - EvapVol
        if len(self.Q_In) > 0:
            Mix += self.Q_In[time,-1]
        V_In_0 = ((Mix + Q_In_0) * dt) or 0
        V_In_1 = ((Mix + Q_In_1) * dt) or 0
        V_Out_0 = (Q_Out_0 * dt) or 0
        #======================================================
        # TODO: Make sure this is supposed to do the same thing here as in Initial Conditions
        self.CalcStreamGeom(Mix + Q_In_1) # Calculate conditions and set wetted depth

        if not self.Flag_SkipNode:
            if not self.Upstream: #Start - Boundary Condition Check "If"
                self.Depth[1] = self.Depth[0]
                self.Q[1] = self.Q[0]
                self.AreaX[1] = self.AreaX[0]
                self.Velocity[1] = self.Q[1] / self.AreaX[1]
            elif self.IniParams.Muskingum: #Run Muskingum-Cunge
                A = self.Q[0] / (2 * self.Width * self.Slope)
                B = (5 / 3) * self.Velocity[0] * dx
                self.X_Weight = 0.5 * (1 - A / B)
                if self.X_Weight > 0.5:
                    self.X_Weight = 0.5
                elif self.X_Weight < 0:
                    self.X_Weight = 0
                K = dx / (5 * self.Velocity[0] / 3) #Wave celerity
                V_Stored = (K * Q_Out_0) + K * self.X_Weight * (Q_In_0 - Q_Out_0)
                V_Reach = V_Stored + V_In_1
                if V_Reach < 0: #Unstable - Decrease dt or increase dx
                    Dummy3 = 2 * K * (1 - self.X_Weight)
                    if dt > Dummy3:
                        raise Exception("Hydraulics are unstable. For this finite element, the time step should be less than %0.3f minutes." % (Dummy3 / 60))
                    else:
                        Dummy3 = 2 * K * (1 - self.X_Weight)
                        raise Exception("Hydraulics are unstable. For this finite element, the time step should be greater than %0.3f minutes." % (Dummy3 / 60))
                #======================================================
                #Calc wedge flow in cell Q(1,1)
                if not self.Upstream:
                    #======================================================
                    #Calc Musk. Coeffs
                    D = 2 * K * (1 - self.X_Weight) + dt
                    C1 = (dt - 2 * K * self.X_Weight) / D
                    C2 = (dt + 2 * K * self.X_Weight) / D
                    C3 = (2 * K * (1 - self.X_Weight) - dt) / D
                    C4 = C1 + C2 + C3
                    V_Out_1 = (C1 * V_In_1 + C2 * V_In_0 + C3 * V_Out_0) or 0
                    #======================================================
                    #Calc Flow
                    self.Q[1] = V_Out_1 / dt
                    if self.Q_Control:
                        self.Q[1] = self.Q_Control
                        V_Out_1 = self.Q[1] * dt

                self.CalcStreamGeom(self.Q[1]) # Update the stream geometry

            # The following explicit method was copied over and transliterated, but it is only
            # used if one of the secret, hidden flags are set in the Excel spreadsheet, so
            # it is not used.
            # If this is to be used, we have to rethink
            elif not self.IniParams.Muskingum: #Explicit Hydraulic Method
                dR = self.Downslope.Depth[0]
                dL = self.Upslope.Depth[0]
                dM = self.Depth[0]
                Wm = self.Width
                WR = self.Downslope.Width
                WL = self.Upslope.Width
                vR = self.Downslope.Velocity[0]
                vL = self.Upslope.Velocity[0]
                vM = self.Velocity[0]
                So = self.Slope
                #Solve for the wetted depth using (3-26) from documentation
                dM = dM + (dt / (2 * dx)) * (dM * (vL - vR) + vM * (dL - dR))
                if not dM:
                    raise Exception("This is going to call a divide by zero error!")
                #Solve for friction slope using (3-28) from documentation
                self.AreaX[1] = dM * (self.Width_B + self.Z * dM)
                self.Pw = self.Width_B + 2 * dM * math.sqrt(1 + self.Z ** 2)
                self.Rh = self.AreaX[1] / self.Pw
                Sf = ((((vR + vL) ^ 2) / 2) * (self.n ** 2)) / (self.Rh ** (4 / 3))
                #Solve for velocity using (3-27) from documentation
                A = vM + (dt / (2 * dx)) * vM * (vR - vL)
                B = ((dt * 9.8 / (2 * dx)) * (dR - dL)) - (dt * 9.8 * (So - Sf))
                self.Velocity[1] = A + B
                #Calculate flow as a function of velocity and depth
                self.SetWettedDepth(Mix + Q_In_1)

        if not self.Flag_SkipNode:
            #======================================================
            #Calc hyporheic flow in cell Q(0,1)
            Dummy1 = self.Conductivity * (1 - self.Embeddedness) #Ratio Conductivity of dominant sunstrate
            Dummy2 = 0.00002 * self.Embeddedness  #Ratio Conductivity of sand - low range
            Horizontal_Conductivity = (Dummy1 + Dummy2) #True horzontal cond. (m/s)
            Dummy1 = self.ParticleSize * (1 - self.Embeddedness) #Ratio Size of dominant substrate
            Dummy2 = 0.062 * self.Embeddedness  #Ratio Conductivity of sand - low range
            thePorosity = 0.3683 * (Dummy1 + Dummy2) ** (-1*0.0641) #Estimated Porosity
            #Calculate head at top (ho) and bottom (hL) of reach
            if not self.Upstream:
                ho = self.Slope * dx
                hL = 0
            else:
                ho = self.Upstream.Depth[1] + self.Slope * dx
                hL = self.Depth[1]
            #Calculate Hyporheic Flows
            self.Hyporheic_Exchange = abs(thePorosity * self.Pw * Horizontal_Conductivity * (ho ** 2 - hL ** 2) / (2 * dx))
            if self.Hyporheic_Exchange > self.Q[1]:
                    self.Hyporheic_Exchange = self.Q[1]
            #===================================================
            #Calculate tendency to stratify
            try:
                self.Froude_Densiometric = math.sqrt(1 / (9.8 * 0.000001)) * dx * self.Q[1] / (self.Depth[1] * self.AreaX[1] * dx)
            except:
                print self.Depth, self.AreaX, dx
                raise
            #===================================================
        else: #Skip Node - No Flow in Channel
            self.Hyporheic_Exchange = 0
            self.T[0] = 0
            self.Froude_Densiometric = 0

        #===================================================
        #Check to see if wetted widths exceed bankfull widths
        #TODO: This has to be reimplemented somehow, because Excel is involved
        # connected to the backend. Meaning this class has NO understanding of what the Excel
        # spreadsheet is. Thus, something must be propigated backward to the parent class
        # to fiddle with the spreadsheet. Perhaps we can write a report to a text file or
        # something. I'm very hesitant to connect this too tightly with the interface.
        Flag_StoptheModel = False
        if self.Width > self.Width_BF and not self.IniParams.Flag_ChannelWidth:

            I = self.RiverKM - dx / 1000
            II = self.RiverKM
            msg = "The wetted width is exceeding the BFW at river KM %0.3f to %0.3f.  To accomodate flows, the BF X-area should be or greater. Select 'Yes' to continue the model run (and use calc. wetted widths) or select 'No' to stop this model run (suggested X-Area values will be recorded in Column Z in the Morphology Data worksheet)  Do you want to continue this model run?" %(round(I, 3), round(II, 3), round(self.AreaX[1], 2))
            dlg = wx.MessageDialog(self, msg, 'HeatSource question', wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_OK:
                # Put this in a public place so we don't ask again.
                self.IniParams.Flag_ChannelWidth = True
                Flag_StoptheModel = False
            else:    #Stop Model Run and Change Input Data
                Flag_StoptheModel = True
                self.IniParams.Flag_ChannelWidth = True
            dlg.Destroy()
#        if Flag_StoptheModel:
#            I = 0
#            while self[(17 + I, 5),"Morphology Data"] < self.RiverKM
#                I += 1
#            Dummy = self[17, 5) - Sheet1.Cells(18, 5)
#            For II = I - CInt(dx / (Dummy * 1000)) To I
#                If II >= 0 Then Sheet1.Cells(17 + II, 26) = Round(AreaX(Node, 1) + 0.1, 2)
#            Next II
