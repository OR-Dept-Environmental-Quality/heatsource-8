from __future__ import division
from DataSheet import DataSheet
from Utils.Time import TimeUtil
from StreamNode import StreamNode
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.IniParams import IniParams
from numpy import arange
import math

class HeatSourceInterface(DataSheet):
    """Defines a datasheet specific to the Current (version 7, 2006) HeatSource Excel interface"""
    def __init__(self, filename=None, show=None):
        if not filename:
            raise Warning("Need a model filename!")
        DataSheet.__init__(self, filename)
        self.StreamNodeList = ()
        self.IniParams = IP = IniParams.getInstance()

        # Grab the initialization parameters from the Excel file.
        # TODO: Ensure that this data doesn't have to come directly from the MainMenu to work
        self.SetSheet("TTools Data")
        IP.Name = self.GetValue("I2")
        IP.Date = self.GetValue("I3")
        IP.DT = self.GetValue("I4")
        IP.Dx = self.GetValue("I5")
        IP.Length = self.GetValue("I6")
        IP.LongSample = self.GetValue("I7")
        IP.TransSample = self.GetValue("I8")
        IP.InflowSites = self.GetValue("I9")
        IP.ContSites = self.GetValue("I10")
        IP.FlushDays = self.GetValue("I11")
        IP.TimeZone = self.GetValue("I12")
        IP.SimPeriod = self.GetValue("I13")

        self.Time = TimeUtil()
        self.pages = ("TTools Data", "Land Cover Codes", "Morphology Data", "Flow Data",
                      "Continuous Data", "Chart-Diel Temp","Validation Data", "Chart-TIR",
                      "Chart-Shade","Output - Hydraulics","Chart-Heat Flux","Chart-Long Temp",
                      "Chart-Solar Flux","Output - Temperature", "Output - Solar Potential",
                      "Output - Solar Surface","Output - Solar Recieved","Output - Longwave",
                      "Output - Evaporation","Output - Convection","Output - Conduction",
                      "Output - Total Heat","Output - Evaporation Rate", "Output - Daily Heat Flux")

    def BasicInputs(self,Flag_HS=0):
        if len(self.StreamNodeList) = 0:
            raise Exception("StreamNodes must be built before this method is functional")
        # TODO: This is the original subroutine to get the input data. We should make it OOP!
        #=======================================================
        StartDate = self.Time.MakeDatetime(self.GetFromMenu("Date"))
        # I don't understand where these values are stored, so I've left it exactly as
        # it was in the original VB code.
        Flag_EvapLoss = self.GetValue("IV1","Land Cover Codes")
        Flag_Muskingum = self.GetValue("IS1","Land Cover Codes")
        Flag_Emergent = self.GetValue("IV5","Land Cover Codes")
        dt = self.IniParams.DT * 60 #Time step to seconds
        dx = self.IniParams.Dx
        #TODO: Need to deal with these flags
        if Flag_HS == 1 or Flag_HS == 2: Dx_lc = self.IniParams.TranSample
        LongSampleRate = self.IniParams.LongSample
        if Flag_HS != 2: Days = self.IniParams.SimPeriod
        else: Days = 1
        Hours = int(Days * 24) #Sim Period (Hours)
        self.Q_BC = []
        self.T_BC = []
        self.Cloudiness = []
        for I in range(Hours - 1):
            if Flag_HS != 2:
                val = self.GetValue((17 + I, 8),"Continuous Data")
                if val == 0: raise Exception("Missing flow boundary condition for day %i " % int(I / 24))
                self.Q_BC.append(val)
                the_a = self.GetValue("IV3","Land Cover Codes")
                the_b = self.GetValue("IV4","Land Cover Codes")
            if Flag_HS == 1:
                t_val = self.GetValue((17 + I,9),"Continuous Data")
                if t_val == 0: raise Exception("Missing temperature boundary condition for day %i" % int(I / 24) )
                self.T_BC.append(t_val)
                self.Cloudiness.append(self.GetValue((17 + I, 10),"Continuous Data"))
        #I = 0 # TODO: necessary?
        StreamLength = self.IniParams.Length
        self.Nodes = round(1 + (StreamLength / (dx / 1000)))  #Model distance nodes
        #=======================================================
        #Get Inflow and continuous data inputs
        if Flag_HS == 0:
            #TODO: Why do we grab values from different sheets if they are all available from the menu or some main sheet?
            Inflow_DistNodes = int(self.GetValue("I9","Output - Hydraulics"))
            # TODO: Some of this should likely be moved to the StreamNode class
            Inflow_Distance = []
            Inflow_Rate = [[] for i in xrange(Inflow_DistNodes)]
            for I in xrange(Inflow_DistNodes):
                Inflow_Distance.append(self.GetValue((I + 17, 12),"Flow Data"))
                for II in xrange(len(Hours)):
                    Inflow_Rate[I].append(self.GetValue((II + 17, 15 + I * 2),"Flow Data"))
        elif Flag_HS == 1: #Heat Source
            Cont_DistNodes = self.GetValue("I10","TTools Data")
            Cont_Humidity = [[] for i in Cont_DistNodes]
            Cont_Wind = [[] for i in Cont_DistNodes]
            Cont_Air_Temp = [[] for i in Cont_DistNodes]
            Cont_Distance = []
            for I in xrange(len(Cont_DistNodes)):
                Cont_Distance.append(self.GetValue((I + 17, 5),"Continuous Data"))
                for II in xrange(len(Hours)):
                    Cont_Wind[I].append(self.GetValue((17 + II, 8 + (I * 4)),"Continuous Data"))
                    Cont_Humidity[I].append(self.GetValue((17 + II, 9 + (I * 4)),"Continuous Data"))
                    Cont_Air_Temp[I].append(self.GetValue((17 + II, 10 + (I * 4)),"Continuous Data"))
            Inflow_DistNodes = self.GetValue("I9","TTools Data")
            Inflow_Distance = []
            Inflow_Rate = [[] for i in Inflow_DistNodes]
            Inflow_Temp = [[] for i in Inflow_DistNodes]
            for I in xrange(len(Inflow_DistNodes)):
                Inflow_Distance.append(self.GetValue((I + 17, 12),"Flow Data"))
                for II in xrange(len(Hours)):
                    Inflow_Rate[I].append(self.GetValue((II + 17, 15 + I * 2),"Flow Data"))
                    Inflow_Temp[I].append(self.GetValue((17 + II, 16 + I * 2),"Flow Data"))
        elif Flag_HS == 2: #Shadealator
            pass
        else: raise Exception("Stupid Flag_HS is broken")

    def UpdateQVarCounter(self):
        ## This is kind of a stupid method. We should know from somewhere else how
        # many datapoints there are.
        #TODO: Fix this
        #=======================================================
        #Calc Number of Flow, Morphology and Land Cover Inputs
        Num_Q_Var = -1
        self.SetSheet("TTools Data")
        val = self[Num_Q_Var + 18,5]
        while val:
            Num_Q_Var += 1 # Iterate
            val = self[Num_Q_Var + 18,5]
            if val == "": val = None
        self.Num_Q_Var = Num_Q_Var

    def CheckMorphologySheet(self):
        #=======================================================
        #Scan morphology variables for null of nonnumeric values
        # Start scanning at the 17th row of the spreadsheet
        #TODO: The visual basic code for this routine makes absolutely no sense!
        # Included is a transcription of the original, which I've tried to interpret
        self.SetSheet('TTools Data')
        for theRow in xrange(17,self.Num_Q_Var + 16):
                for theCol in xrange(7,22):
                    if theCol == 9: continue
                    val = self[theRow,theCol]
                    if not (isinstance(val,float) or isinstance(val,int)) or \
                        val == "" or \
                        self.Num_Q_Var <= 0:
                        raise Exception("Invalid data: row %i, cell %s: '%s' ... Flow router terminated" %(theRow, self.excelize(theCol),val))

    def BuildStreamNodes(self):
        """Create list of StreamNodes from the spreadsheet"""
        # This function is copied from the VB code, but it is somewhat pointless if the
        # program is built in a proper OOP framework, because most of these variables would
        # in objects
        # TODO: Building a stream node might need to be cleaned up a bit.
        for i in range(self.Num_Q_Var):
            node = StreamNode()
            self.sheet = 'Morphology Data'
            node.RiverKM = self[i + 17, 4]
            node.Slope = self[i + 17, 6]
            node.N = self[i + 17, 7]
            node.WD = self[i + 17, 9]
            node.Width_BF = self[i + 17, 10]
            node.Width_B = self[i + 17, 11]
            node.Depth_BF = self[i + 17, 12]
            node.Z = self[i + 17, 15]
            node.X_Weight = self[i + 17, 16]
            node.Conductivity = self[i + 17, 17] / 1000
            node.Particle_Size = self[i + 17, 18]
            node.Embeddedness = self[i + 17, 19]
            node.Q_Control = self[i + 17, 22]
            node.D_Control = self[i + 17, 23]
            node.FLIR_Time = self[i + 17, 20]
            node.FLIR_Temp = self[i + 17, 21]
            node.T_Control = self[i + 17, 24]

            self.sheet = 'Flow Data'
            node.Q_Out = self[i + 17, 6]
            node.Q_Accretion = self[i + 17, 4]
            node.T_Accretion = self[i + 17, 5]

            self.sheet = 'TTools Data'
            node.Longitude = self[i + 17, 5]
            node.Latitude = self[i + 17, 6]
            node.Aspect = self[i + 17, 9]
            node.Topo_W = self[i + 17, 10]
            node.Topo_S = self[i + 17, 11]
            node.Topo_E = self[i + 17, 12]
            node.VHeight = self[i + 17, 159]
            node.VDensity = self[i + 17, 160]
            node.Elevation = self[i + 17, 7]

            #The original VB code has this method BFMorph, which calculates some things and
            # spits them back to the spreadsheet. We want to keep everything in the node, but
            # we'll spit these four things back to the spreadsheet for now, until we understand
            # better what the purpose was
            self.sheet = "Morphology Data"
            node.BFMorph()
            self.SetValue((i + 17, 11),node.BottomWidth)
            self.SetValue((i + 17, 12),node.MaxDepth)
            self.SetValue((i + 17, 13),node.AveDepth)
            self.SetValue((i + 17, 14),node.BFXArea)
            ##############################################################

            dir = [] # List to save the seven directions
            for Direction in xrange(1,8):
                z = () #Tuple to store the zones 0-4
                for Zone in xrange(5):
                    if Zone == 0:
                        #TODO: See what this storage of elevation is used for, because it is also used above.
                        z += VegZone(self[i + 17, 7], Overhang=self[i + 17, Direction + 150]), #Overhang and Elevation
                        continue #No need to do any more for 0th zone
                    Elevation = self[i + 17, Direction * 4 + 37 + Zone]
                    VHeight = self[i + 17, Direction * 8 + 61 + Zone * 2]
                    VDensity = self[i + 17, Direction * 8 + 60 + Zone * 2]
                    # append to the ith zone
                    z += VegZone(Elevation,VHeight,VDensity),
                dir.append(z) # append to the proper direction
            node.Zone = Zonator(*dir) # Create a Zonator instance and set the node.Zone attribute

        self.StreamNodeList += node, # Now add this node to the stream node list

    def LoadModelVariables(self,Node,theDistance,Count_Q_Var,Flag_HS):
        """Load model variables (see notes)"""
        #I really don't understand what this subroutine is supposed to be doing.
        # It is just copied from the visual basic code so that it functions the same
        # way. It is probably in desperate need of optimization.
        #TODO: Figure out a better way to define these averages, perhaps in BuildStreamNodes.
        self.SetSheet('Morphology Data')
        node = self.StreamNodeList[Node]
        while Node > 0 and Round(theDistance, 2) < round(self[Count_Q_Var + 17, 5], 2):
            Count_Q_Var = Count_Q_Var + 1
        #======================================================
        #Average Parameters Over Modeled Segments
        #======================================================
        I = 0
        # This is a dictionary to hold totals for the averages.
        # In the original code, it was {I2,I3,...,I8}
        control_num = {'T_Control':0,'Q_Control':0,'D_Control':0,'Q_Accretion':0}
        node.Q_Out_Total = 0
        # Here's a list of attributes that we are calculating in the original
        # VB code. This allows us to just loop over them, instead of individually
        # calculating each one.
        the_attrs = ['RiverKM', 'Slope','N','Width_BF','Width_B','Width_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','Elevation']

        thisNode = self.StreamNodeList[Count_Q_Var - I]
        calc = True
        while calc:
            """So, there's a weird loop in this subroutine (VB code) that I'm
            simulating with a nested while statement"""
            for attr in the_attrs:
                name = "the" + attr # Original code has 'the' in front of attribute names (i.e. theSlope for average of Slope)
                x = getattr(node,name) # get the average value (or zero if it's not yet calculated)
                y = x + thisNode.Slope # Add the current value
                setattr(node, name, y)
                if attr in control_num.keys(): control_num[attr] += 1
            # NOTE: The VB code had certain totals (e.g. T_Control_Total) which have been renamed to 'the' (e.g. theT_Control)
            # Temperature accretion is treated somewhat differently, and it should be calculated after
            # Flow accretion, so we do it outside that loop
            node.theT_Accretion = (node.theT_Accretion + thisNode.T_Accretion * thisNode.Q_Accretion)

            for Direction in xrange(1,8):
                for Zone in xrange(5):
                    if Zone == 0:
                        node.theZone[Direction][Zone].Elevation += thisNode.Zone[Direction][Zone].Elevation
                        node.theZone[Direction][Zone].Overhang += thisNode.Zone[Direction][Zone].Overhang
                        continue # Nothing else in the 0th zone
                    node.theZone[Direction][Zone].Elevation = node.Zone[Direction][Zone].theElevation + thisNode.Zone[Direction][Zone].Elevation
                    node.theZone[Direction][Zone].VHeight +=  node.Zone[Direction][Zone].VHeight
                    node.theZone[Direction][Zone].VDensity += node.Zone[Direction][Zone].VDensity
            I = I + 1
            if ((Count_Q_Var - I) < 0) or (thisNode.theRiverKM >= round((theDistance + dx / 1000), 3)): break
        #======================================================
        #Account for Inflow Volumes
        Flag_Inflow = 0
        I8 = Count_Q_In
        I7 = Count_Q_In
        if Flag_First == 1:
            Dummy = Count_Q_In
        if Count_Q_In < Inflow_DistNodes:
            while (theDistance <= Inflow_Distance(Count_Q_In)) and ((theDistance + dx / 1000) > Inflow_Distance(Count_Q_In)):
                for II in xrange(Hours):
                    # TODO: Move much of this to the StreamNode class
                    Q_In[II] += Inflow_Rate[Count_Q_In][II]
                    if Flag_HS == 1:
                        T_In[Node][II] = T_In[Node][II] + Inflow_Temp[Count_Q_In][II] * Inflow_Rate[Count_Q_In][II]
                Count_Q_In = Count_Q_In + 1
                Flag_Inflow = 1
                if Count_Q_In > Inflow_DistNodes: break
        #======================================================
        #Account for Inflow Temps
        if Flag_Inflow == 1 and Flag_HS == 1:
            for II in xrange(Hours):
                T_In[Node][II] = T_In[Node][II] / Q_In[Node][II]
        Flag_Inflow = 0

        node.theSlope /= I
        node.theN /= I
        node.theWidth_BF /= I
        node.theArea_Wetland = theArea_Wetland + node.theWidth_BF * dx
        node.theWidth_B /= I
        node.theDepth_BF /= I
        node.theZ /= I
        node.theX_Weight /= I
        node.theEmbeddedness /= I
        node.theConductivity /= I
        node.theParticleSize /= I
        node.theQ_Control = (node.theQ_Control / control_num['Q_Control']) if node.theQ_Control else 0
        node.theQ_Accretion = node.theQ_Accretion if node.theQ_Accretion else 0
        node.theT_Accretion = (node.theT_Accretion / node.theQ_Accretion) if node.theQ_Accretion else 0
        node.theD_Control = (node.theD_Control / control_num['D_Control']) if node.theD_Control else 0

        #======================================================
        #Calculate Average elevations and land cover height and density
        #theElevation(Node, Zone, Direction)
        #theVHeight(Node, Zone, Direction)
        #theVDensity(Node, Zone, Direction)
        #Direction: 0 = Stream
        #           1 = Northeast
        #           2 = East
        #           3 = Southeast
        #           4 = South
        #           5 = Southwest
        #           6 = West
        #           7 = Northwest
        node.theT_Control = (node.theT_Control / control_num['T_Control']) if node.theT_Control else 0

        node.theAspect /= I
        node.theTopo_W /= I
        node.theTopo_S /= I
        node.theTopo_E /= I
        node.theLatitude /= I
        node.theLongitude /= I
        node.Gotit = 0
        node.theFLIR_Time /= I
        node.theFLIR_Temp /= I
        node.theVHeight /= I
        node.theVDensity /= I
        for Direction in xrange(1,8):
            for Zone in xrange(5):
                if Zone == 0:
                    node.theZone[Direction][Zone].Elevation /= I
                    node.theZone[Direction][Zone].Overhang /= I
                    continue # done with 0th zone
                node.theZone[Direction][Zone].Elevation /= I
                node.theZone[Direction][Zone].VHeight /= I
                node.theZone[Direction][Zone].VDensity /= I
                node.theZone[Direction][Zone].SlopeHeight = node.theZone[Direction][Zone].Elevation - node.theZone[Direction][0].Elevation

    def CalculateInitialConditions(self,Node, theDistance, Flag_BC):
        """Initial conditions"""
        #==================================================
        # Initial conditions for flow
        #TODO: This should be in StreamNode
        node = self.StreamNodeList[Node]
        if Flag_BC: # TODO: What the hell is Flag_BC?
            node.Q[0] = self.Q_BC[0]
        else
            if node.theQ_Control(Node) != 0:
                node.Q[0] = node.theQ_Control
            else:
                node.Q[0] = self.StreamNodeList[Node-1].Q[0] + node.Q_In[theHour] - node.theQ_Out + node.theQ_Accretion
        node.Q[1] = node.Q[0]
        #=======================================================
        #Set Temperature Initial Conditions
        # TODO: This should be in StreamNode
        if Flag_HS == 1:
            node.T[0] = node.T[1] = node.Temp_Sed = self.T_BC[theHour]
        #======================================================
        #Set Atmospheric Counter
        #TODO: To StreamNode??
        if Flag_HS == 1:
            while Cont_Distance[Counter_Atmospheric_Data] >= (theDistance + dx / 1000)
                Counter_Atmospheric_Data = Counter_Atmospheric_Data + 1
            node.Atmospheric_Data = Counter_Atmospheric_Data
        #======================================================
        #Calculate Initial Condition Hydraulics
        if node.theQ_Control: node.Q[0] = node.theQ_Control
        if node.theD_Control: node.theDepth[0] = node.theD_Control
        #======================================================
        #Control Depth
        if node.theD_Control:
            node.AreaX[0] = node.theDepth[0] * (node.theWidth_B + node.theZ * node.theDepth[0])
            node.Pw = node.theWidth_B + 2 * node.theDepth[0] * math.sqrt(1 + node.theZ ** 2)
            if node.Pw <= 0: node.Pw = 0.00001
            node.Rh = node.AreaX[0] / node.Pw
        #======================================================
        #No Control Depth
        else
            if node.theSlope <= 0:
                raise Exception("Slope cannot be less than or equal to zero unless you enter a control depth.")
            if Flag_BC == 1:
                node.theDepth[0] = 1
            else:
                node.theDepth[0] = self.StreamNodeList[Node-1].theDepth[0]
            Q_Est = node.Q[0]
            if Q_Est < 0.0071: 'Channel is going dry
                Flag_SkipNode[Node] = True
                if Flag_HS == 1: T_Last = node.T[0]
                if Flag_DryChannel == 0:
                    # TODO: Implement dry channel controls
#                    If Sheet2.Range("IV22").Value = 1 Then
#                        Style = vbYesNo + vbCritical                   ' Define buttons.
#                        Title = "Heat Source - Channel Is Going Dry"  ' Define title
#                        Msg = "The channel is going dry at " & Round(theDistance, 2) & " river KM.  The model will either skip these 'dry stream segments' or you can stop this model run and change input data.  Do you want to continue this model run?"
#                        response = MsgBox(Msg, Style, Title, Help, Ctxt)
#                        If response = vbYes Then ' Continue Model run
#                            Flag_DryChannel = 1
#                        Else    'Stop Model Run and Change Input Data
#                            End
#                        End If
#                    Else
#                        Flag_DryChannel = 1
#                    End If
            else    'Channel has sufficient flow
                Flag_SkipNode[Node] = False

        if not Flag_SkipNode[Node]:
            Converge = 100000
            dy = 0.01
            D_Est = node.theDepth[0]
            A_Est = node.AreaX[0]
            Count_Iterations = 0
            while True:
                if D_Est == 0: D_Est = 10
                A_Est = D_Est * (node.theWidth_B + node.theZ * D_Est)
                node.Pw = node.theWidth_B + 2 * D_Est * math.sqrt(1 + node.theZ ** 2)
                if node.Pw <= 0: node.Pw = 0.00001
                node.Rh = A_Est / node.Pw
                Fy = A_Est * (node.Rh ** (2 / 3)) - (node.theN) * Q_Est / math.sqrt(node.theSlope)
                thed = D_Est + dy
                A_Est = thed * (node.theWidth_B + node.theZ * thed)
                node.Pw = node.theWidth_B + 2 * thed * node.sqrt(1 + node.theZ ** 2)
                if node.Pw <= 0: node.Pw = 0.00001
                node.Rh = A_Est / node.Pw
                Fyy = A_Est * (node.Rh ** (2 / 3)) - (node.theN) * Q_Est / math.sqrt(node.theSlope)
                dFy = (Fyy - Fy) / dy
                if dFy == 0: dFy = 0.99
                thed = D_Est - Fy / dFy
                D_Est = thed
                if D_Est < 0 or D_Est > 1000000000000 or Count_Iterations > 1000:
                    D_Est = 10 * Rnd 'Randomly reseed initial value and step
    '                dy = 1 / ((200 - 100 + 1) * Rnd + 100)
                    Converge = 10
                    Count_Iterations = 0
                dy = 0.01
                Converge = abs(Fy / dFy)
                if Converge < 0.001: break
                Count_Iterations = Count_Iterations + 1
            node.theDepth[0] = D_Est
            node.AreaX[0] = A_Est
            node.theVelocity[0] = node.Q[0] / node.AreaX[0]
            node.theWidth = node.theWidth_B + 2 * node.theZ * node.theDepth[0]
            node.Celerity = node.theVelocity[0] + math.sqrt(9.8 * node.theDepth[0]) #TODO: Check this with respect to gravity rounding error
            if Flag_Muskingum == 0 and Flag_HS < 2 and Flag_SkipNode[Node] == 0:
                if dt > dx / node.Celerity: dt = dx / node.Celerity
        else:
            Q_Est = 0
            node.theDepth[0] = 0
            node.AreaX[0] = 0
            node.Pw = 0
            node.Rh = 0
            node.theWidth = 0
            node.theDepthAve = 0
            node.theVelocity[0] = 0
            node.Q[0] = 0
            node.Celerity = 0

    def SetupSheets1(self):
        for page in ("Solar Potential","Solar Surface","Solar Received","Longwave",\
              "Evaporation","Convection","Total Heat","Conduction","Evaporation Rate",\
              "Temperature","Hydraulics","Daily Heat Flux"):
            name = "Output - %s" % page
            self.Clear("F16:IV16",name)
            self.Clear("17:50000",name)
        self.Clear("A13:D10000", "Chart-TIR")
        self.Clear("A13:c10000", "Chart-Shade")
        self.Clear("17:50000", "Chart-Diel Temp")
        self.Clear("13:50000", "Chart-Heat Flux")
        self.Clear("13:50000","Chart-Shade")
        self.Clear("13:50000", "Chart-Solar Flux")

    def SetupSheets2(self,Node, Count_Q_Var, theDistance):
        """Set the values for a particular node and distance.

        "There must be a better way... right?" He asked God."""
        self.SetSheet("Morphology Data")
        val = {}
        val[2] = self[Count_Q_Var + 17, 2] # Location Info
        val[3] = self[Count_Q_Var + 17, 3] # HS Node
        val[4] = self[Count_Q_Var + 17, 4] # Long Distance
        val[5] = round(theDistance, 3)     # Stream km

        for page in ("Solar Potential","Solar Surface","Solar Received","Longwave",\
              "Evaporation","Convection","Total Heat","Conduction","Evaporation Rate",\
              "Temperature","Daily Heat Flux", "Hydraulics"):
            name = "Output - %s" % page
            for i in val.keys():
                self.SetValue((Node+17,i),val[i],sheet=name)
