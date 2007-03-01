from __future__ import division
from DataSheet import DataSheet
from Utils.Time import TimeUtil
from Utils.ProgressBar import ProgressBar
from StreamNode import StreamNode
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.IniParams import IniParams
from numpy import arange
import math

#Flag_HS values:
#    0: Flow Router
#    1: Heat Source
#    2: Shadelator

class HeatSourceInterface(DataSheet):
    """Defines a datasheet specific to the Current (version 7, 2006) HeatSource Excel interface"""
    def __init__(self, filename=None, show=None, Flag_HS=1):
        if not filename:
            raise Warning("Need a model filename!")
        DataSheet.__init__(self, filename)
        self.StreamNodeList = ()
        self.IniParams = IP = IniParams.getInstance()

        #######################################################
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
        # I don't understand where these values are stored, so I've left it exactly as
        # it was in the original VB code, except that I place the values in the IniParams class
        IP.Flag_EvapLoss = self.GetValue("IV1","Land Cover Codes")
        IP.Flag_Muskingum = self.GetValue("IS1","Land Cover Codes")
        IP.Flag_Emergent = self.GetValue("IV5","Land Cover Codes")
        ######################################################
        # Create a time manipulator
        self.Time = TimeUtil()
        # Page names- maybe a useless tuple, we'll see
        self.pages = ("TTools Data", "Land Cover Codes", "Morphology Data", "Flow Data",
                      "Continuous Data", "Chart-Diel Temp","Validation Data", "Chart-TIR",
                      "Chart-Shade","Output - Hydraulics","Chart-Heat Flux","Chart-Long Temp",
                      "Chart-Solar Flux","Output - Temperature", "Output - Solar Potential",
                      "Output - Solar Surface","Output - Solar Recieved","Output - Longwave",
                      "Output - Evaporation","Output - Convection","Output - Conduction",
                      "Output - Total Heat","Output - Evaporation Rate", "Output - Daily Heat Flux")

        dt = self.IniParams.DT * 60 #Time step to seconds

        self.SetupSheets1()

        # TODO: These are only used in the VB routine SubEvaporativeFlux, so they should be moved there
        # What the hell are they, anyway?
        self.IniParams.the_a = self.GetValue("IV3","Land Cover Codes")
        self.IniParams.the_b = self.GetValue("IV4","Land Cover Codes")

        self.Nodes = round(1 + (self.IniParams.Length / (self.IniParams.Dx / 1000)))  #Model distance nodes

        # from VB: Apparently, only one day is simulated for the shadelator
        if Flag_HS != 2: Days = self.IniParams.SimPeriod
        else: Days = 1
        Hours = int(self.IniParams.SimPeriod * 24) if Flag_HS != 2 else 24

        #Figure out the length of the data and store it (This could be changed)
#        self.UpdateQVarCount()

        # Build a quick progress bar
#        self.PB = ProgressBar(self.IniParams.InflowSites + self.IniParams.ContSites + Hours + self.Num_Q_Var)

        # Now we start through the steps that were in the first subroutines in the VB code's theModel subroutine
        #TODO: We need to clean up this syntax and logical progression
#        self.GetBoundaryConditions(Hours)
#        if Flag_HS != 2:
#           self.GetInflowData()
#           if Flag_HS == 1: self.GetContinuousData(Hours)
#        self.ScanMorphology()
        self.BuildStreamNodes()

#        self.PB.Hide() #Hide the progressbar, but keep it live


    def GetNode(self, index):
        if isinstance(index,slice):
            return self.StreamNodeList[index.start:index.stop:index.step]
        else: return self.StreamNodeList[index]
    def Map(self, func):
        """Map a lambda function to the list of streamnodes, returning nothing"""
        # this uses list comprehension instead of map() because of the Psyco modules problems with it.
        [func(i) for i in self.StreamNodeList]

    def UpdateQVarCount(self):
        # Calculate the number of stream node inputs
        # The former subroutine in VB did this by getting each row's value
        # and incrementing a counter if the value was not blank. With the
        # new DataSheet's __getitem__ functionality, we can merely access
        # the sheet once, and return the length of that tuple
        row = self[:,5][16:] # no row definition, 5th column- strip off the first 16 lines
        self.Num_Q_Var = len(row)

    def GetBoundaryConditions(self, Hours):
        """Get the boundary conditions from the "Continuous Data" page"""
        # Boundary conditions
        self.Q_BC = []
        self.T_BC = []
        self.Cloudiness = []

        # These are storage of inflow and continuous data information
        self.IniParams.InflowSites = int(self.IniParams.InflowSites)
        self.Inflow_Rate = [[] for i in xrange(self.IniParams.InflowSites)]
        self.Inflow_Temp = [[] for i in xrange(self.IniParams.InflowSites)]
        self.Inflow_Distance = []

        self.IniParams.ContSites = int(self.IniParams.ContSites)
        self.Cont_Humidity = [[] for i in xrange(self.IniParams.ContSites)]
        self.Cont_Wind = [[] for i in xrange(self.IniParams.ContSites)]
        self.Cont_Air_Temp = [[] for i in xrange(self.IniParams.ContSites)]
        self.Cont_Distance = []

        col = 7
        for I in xrange(Hours):
            # Get the flow boundary condition
            val = self.GetValue((17 + I, col),"Continuous Data")
            if val == 0 or not val: raise Exception("Missing flow boundary condition for day %i " % int(I / 24))
            self.Q_BC.append(val)
            # Temperature boundary condition
            t_val = self.GetValue((17 + I,col+1),"Continuous Data")
            if t_val == 0 or not t_val: raise Exception("Missing temperature boundary condition for day %i" % int(I / 24) )
            self.T_BC.append(t_val)
            # Cloudiness boundary condition
            self.Cloudiness.append(self.GetValue((17 + I, col+2),"Continuous Data"))
            self.PB("Reading boundary conditions",I,Hours)

    def GetInflowData(self):
        """Get accumulation data from the "Flow Data" page"""
        for I in xrange(self.IniParams.InflowSites):
            self.Inflow_Distance.append(self.GetValue((I + 17, 11),"Flow Data"))
            for II in xrange(len(Hours)):
                self.Inflow_Rate[I].append(self.GetValue((II + 17, 14 + I * 2),"Flow Data"))
                self.Inflow_Temp[I].append(self.GetValue((17 + II, 15 + I * 2),"Flow Data"))
                self.PB("Reading inflow data", I, self.IniParams.InflowSites)
    def GetContinuousData(self, Hours):
        """Get data from the "Continuous Data" page"""
        for I in xrange(self.IniParams.ContSites):
            self.Cont_Distance.append(self.GetValue((I + 17, 4),"Continuous Data"))
            for II in xrange(Hours):
                self.Cont_Wind[I].append(self.GetValue((17 + II, 7 + (I * 4)),"Continuous Data"))
                self.Cont_Humidity[I].append(self.GetValue((17 + II, 8 + (I * 4)),"Continuous Data"))
                self.Cont_Air_Temp[I].append(self.GetValue((17 + II, 9 + (I * 4)),"Continuous Data"))
            self.PB("Reading continuous data", I, self.IniParams.ContSites)

    def ScanMorphology(self):
        """Scan morphology variables for null of nonnumeric values"""
        # Start scanning at the 17th row of the spreadsheet
        #TODO: The visual basic code for this routine makes absolutely no sense
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
            self.PB("Scanning morphology data", theRow, self.Num_Q_Var+16)

    def BuildStreamNodes(self):
        """Create list of StreamNodes from the spreadsheet

        In the original VB code, this was quite different. I will not explain what that
        code does, but will rather explain the motivation behind this version. We have two
        controlling variables: longitudinal sample rate and the distance step (dx). The
        dx is always a multiple of the longitudinal sample rate. The values within the
        node are the average values of the longitudinal samples that fall within that dx.
        For instance, if longrate=50 and dx=200, then the Slope for the node will be
        the average of 4 longitudinal slopes."""
        self.StreamNodeList = () # Make sure we empty any current list

        long = self.IniParams.LongSample
        dx = self.IniParams.Dx
        length = self.IniParams.Length

        # the distance step must be an exact, greater or equal to one, multiple of the sample rate.
        if (dx%long or dx<long): raise Exception("Distance step must be a multiple of the Longitudinal transfer rate")

        multiple = dx/long #We have this many samples per distance step

        # Dictionary of sheet names, StreamNode attributes and corresponding columns within the sheet.
        # This is used in the later loop to fill the stream node with averaged data.
        morph = {'Slope': 6,
                'N': 7,
                'WD': 9,
                'Width_BF': 10,
                'Width_B': 11,
                'Depth_BF': 12,
                'Z': 15,
                'X_Weight': 16,
                'Conductivity': 17, # This value needs to be divided by 1000
                'ParticleSize': 18,
                'Embeddedness': 19,
#                'FLIR_Time': 20,
                'FLIR_Temp': 21}
#                'Q_Control': 22,
#                'D_Control': 23,
#                'T_Control': 24}
        flow = {'Q_Accretion': 4,
                'T_Accretion': 5,
                'Q_Out': 6,}
        ttools = {'Longitude': 5,
                  'Latitude': 6,
                  'Elevation': 7,
                  'Aspect': 9,
                  'Topo_W': 10,
                  'Topo_S': 11,
                  'Topo_E': 12,
                  'VHeight': 159,
                  'VDensity': 160}
        pages = {'Morphology Data': morph}#, 'Flow Data': flow, 'TTools Data': ttools}

        # This process is quite gruelling. I think that this can probably be cleaned up by
        # getting the entire data matrix in a single call, averaging every X group of values
        # in every column, and dumping that data into the StreamNode. This would be significantly
        # easier than this method. However, since UsedRange does not seem to work, we have to find
        # a way of getting all of the data from a sheet in a non-stupid fashion. Until we do that,
        # this method will suffice.

        row = 17 # Current row
        GotNodes = False
        while not GotNodes: # Until we get to the end of the data
            node = StreamNode()
            for i in xrange(int(multiple)): # How many samples per node?
                if GotNodes: break # If we set GotNodes to true in an inner loop, we don't necessarily break out of this one.
                test = i == multiple-1 #Are we in the last pass?
                # We have to get the rivermile, but if it's blank, and since we are assuming that
                # we checked all the morphology data for blank values, then we will assume that,
                # if this is None, we hit a blank row
                val = self[row+i,4,'Morphology Data']
                node.RiverKM = val if val else node.RiverKM # Set the river mile
                row_km = node.RiverKM
                for page in pages:
                    # Row of all available data grabbed in a single 'get' call
                    # We get the 0th item because what's returned is actually a row of rows, but with only one.
                    try:
                        data = self[row+i,:,page][0]
                    except IndexError:
                         # we have a null value, which means we may be at the end of our data.
                         # e.g. if we have 3.15 km of stream with samples every 50 meters and
                         # a dx of 100 meters, we'll have an extra segment of 50 meters, so
                         # trying to grab the second part of that segment will be null.
                         # In that case, we average immediately and scram
                        val = getattr(node,attr) / (i+1)
                        setattr(node,attr,val)
                        GotNodes = True # Assume we're at the end of the data, and break completely
                        break
                    for attr, col in pages[page].items():
                        val = getattr(node,attr) + data[col] # Get current value using the attribute's name string
                        setattr(node,attr,val) # set the new value
                        if not test and attr=="Slope": crap = val
                        if test and page == 'Morphology Data': # we are in the last run, or have a null value, so we average
                            val = getattr(node,attr) / multiple
                            setattr(node,attr,val)
            row += multiple
            self.StreamNodeList += node,
            raise Exception("Not yet, we still have to finish what's commented below")

#        for i in range(count):
#
#            dir = [] # List to save the seven directions
#            for Direction in xrange(7):
#                z = () #Tuple to store the zones 0-4
#                for Zone in xrange(5):
#                    if Zone == 0:
#                        #TODO: See what this storage of elevation is used for, because it is also used above.
#                        elev = self[i + 17, 7]
#                        over = self[i + 17, Direction + 150]
#                        elev = elev if elev else 0 # In case the values are None
#                        over = over if over else 0
#                        z += VegZone(elev, Overhang=over), #Overhang and Elevation
#                        continue #No need to do any more for 0th zone
#                    Elevation = self[i + 17, Direction * 4 + 37 + Zone]
#                    VHeight = self[i + 17, Direction * 8 + 61 + Zone * 2]
#                    VDensity = self[i + 17, Direction * 8 + 60 + Zone * 2]
#                    # append to the ith zone
#                    z += VegZone(Elevation,VHeight,VDensity),
#                dir.append(z) # append to the proper direction
#            node.Zone = Zonator(*dir) # Create a Zonator instance and set the node.Zone attribute
#
#            #############################################################
#            #The original VB code has this method BFMorph, which calculates some things and
#            # spits them back to the spreadsheet. We want to keep everything in the node, but
#            # we'll spit these four things back to the spreadsheet for now, until we understand
#            # better what the purpose was
#            node.BFMorph()
#            self.SetValue((i + 17, 11),node.BottomWidth, sheet="Morphology Data")
#            self.SetValue((i + 17, 12),node.MaxDepth, sheet="Morphology Data")
#            self.SetValue((i + 17, 13),node.AveDepth, sheet="Morphology Data")
#            self.SetValue((i + 17, 14),node.BFXArea, sheet="Morphology Data")
#            ##############################################################
#
#            self.StreamNodeList += node, # Now add this node to the stream node list
#            if not self.PB("Building Stream Nodes", i, count)[0]: raise Exception("Building streamnodes cancelled, model stopped")

    def LoadModelVariables(self,Node,theDistance,Count_Q_Var,Flag_HS):
        """Load model variables (see notes)"""
        #I really don't understand what this subroutine is supposed to be doing.
        # It is just copied from the visual basic code so that it functions the same
        # way. It is probably in desperate need of optimization.
        #TODO: Figure out a better way to define these averages, perhaps in BuildStreamNodes.
        self.SetSheet('Morphology Data')
        node = self.StreamNodeList[Node]

        Flag_First = 1
        while Node > 0 and round(theDistance, 2) < round(self[Count_Q_Var + 17, 4], 2):
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
        the_attrs = ['RiverKM', 'Slope','N','Width_BF','Width_B','Depth_BF','Z','X_Weight',
                 'Embeddedness','Conductivity','ParticleSize','Aspect','Topo_W',
                 'Topo_S','Topo_E','Latitude','Longitude','FLIR_Temp','FLIR_Time',
                 'Q_Out','Q_Control','D_Control','T_Control','VHeight','VDensity',
                 'Q_Accretion','Elevation']

        calc = True
        while calc:
            """So, there's a weird loop in this subroutine (VB code) that I'm
            simulating with a nested while statement"""
            prevNode = self.StreamNodeList[Node - I]
            for attr in the_attrs:
                name = "the" + attr # Original code has 'the' in front of attribute names (i.e. theSlope for average of Slope)
                x = getattr(node,name) # get the average value (or zero if it's not yet calculated)
                y = x + prevNode.Slope # Add the current value
                setattr(node, name, y)
                if attr in control_num.keys(): control_num[attr] += 1
            # NOTE: The VB code had certain totals (e.g. T_Control_Total) which have been renamed to 'the' (e.g. theT_Control)
            # Temperature accretion is treated somewhat differently, and it should be calculated after
            # Flow accretion, so we do it outside that loop
            print prevNode
            node.theT_Accretion += prevNode.T_Accretion * prevNode.Q_Accretion


            for Direction in xrange(7):
                for Zone in xrange(5):
                    if Zone == 0:
                        node.theZone[Direction][Zone].Elevation += prevNode.Zone[Direction][Zone].Elevation
                        node.theZone[Direction][Zone].Overhang += prevNode.Zone[Direction][Zone].Overhang
                        continue # Nothing else in the 0th zone
                    node.theZone[Direction][Zone].Elevation += prevNode.Zone[Direction][Zone].Elevation
                    node.theZone[Direction][Zone].VHeight +=  prevNode.Zone[Direction][Zone].VHeight
                    node.theZone[Direction][Zone].VDensity += prevNode.Zone[Direction][Zone].VDensity
            I = I + 1
            if ((Count_Q_Var - I) < 0) or (prevNode.theRiverKM >= round((theDistance + dx / 1000), 3)): break
        #======================================================
        #Account for Inflow Volumes
        Count_Q_In = 0 #This was a global variable in the original code
        Flag_Inflow = 0
        I8 = Count_Q_In
        I7 = Count_Q_In
        if Flag_First == 1:
            Dummy = Count_Q_In

        if Count_Q_In < self.IniParams.InflowSites:
            while (theDistance <= self.Inflow_Distance[Count_Q_In]) and ((theDistance + dx / 1000) > Inflow_Distance[Count_Q_In]):
                for II in xrange(Hours):
                    # TODO: Move much of this to the StreamNode class
                    self.Q_In[II] += self.Inflow_Rate[Count_Q_In][II]
                    if Flag_HS == 1:
                        node.T_In[II] = node.T_In[II] + self.Inflow_Temp[Count_Q_In][II] * self.Inflow_Rate[Count_Q_In][II]
                Count_Q_In += 1
                Flag_Inflow = 1
                if Count_Q_In > Inflow_DistNodes: break
        #======================================================
        #Account for Inflow Temps
        if Flag_Inflow == 1 and Flag_HS == 1:
            for II in xrange(Hours):
                node.T_In[II] = node.T_In[II] / node.Q_In[II]
        Flag_Inflow = 0

        node.theSlope /= I
        node.theN /= I
        node.theWidth_BF /= I
        wet_area = node.theWidth_BF * self.IniParams.Dx
        try: node.theArea_Wetland += area
        except AttributeError: node.theArea_Wetland = wet_area
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
        for Direction in xrange(7):
            for Zone in xrange(5):
                if Zone == 0:
                    node.theZone[Direction][Zone].Elevation /= I
                    node.theZone[Direction][Zone].Overhang /= I
                    continue # done with 0th zone
                node.theZone[Direction][Zone].Elevation /= I
                node.theZone[Direction][Zone].VHeight /= I
                node.theZone[Direction][Zone].VDensity /= I
                node.theZone[Direction][Zone].SlopeHeight = node.theZone[Direction][Zone].Elevation - node.theZone[Direction][0].Elevation

    def CalculateInitialConditions(self,Node, theDistance, Flag_BC, Flag_HS):
        """Initial conditions"""
        #==================================================
        # Initial conditions for flow
        #TODO: This should be in StreamNode
        node = self.StreamNodeList[Node]
        if Flag_BC: # TODO: What the hell is Flag_BC?
            node.Q[0] = self.Q_BC[0]
        else:
            if node.theQ_Control != 0:
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
            while Cont_Distance[Counter_Atmospheric_Data] >= (theDistance + dx / 1000):
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
            Flag_SkipNode = False
            # Not sure if this should go here. The problem is it is undefined before this if/else
            # statement, and is not otherwise defined in the if portion, but it is needed AFTER
            # this statement, so if we hit this if portion, we have an undefined variable below.
            # TODO: Figure out what we are really trying to do here.
            Q_Est = node.Q[0]
        #======================================================
        #No Control Depth
        else:
            if node.theSlope <= 0:
                raise Exception("Slope cannot be less than or equal to zero unless you enter a control depth.")
            if Flag_BC == 1:
                node.theDepth[0] = 1
            else:
                node.theDepth[0] = self.StreamNodeList[Node-1].theDepth[0]
            Q_Est = node.Q[0]
            if Q_Est < 0.0071: #Channel is going dry
                Flag_SkipNode = True
                if Flag_HS == 1: T_Last = node.T[0]
                if Flag_DryChannel == 0: pass
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
            else:    #Channel has sufficient flow
                Flag_SkipNode = False

        if not Flag_SkipNode:
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
                node.Pw = node.theWidth_B + 2 * thed * math.sqrt(1 + node.theZ ** 2)
                if node.Pw <= 0: node.Pw = 0.00001
                node.Rh = A_Est / node.Pw
                Fyy = A_Est * (node.Rh ** (2 / 3)) - (node.theN) * Q_Est / math.sqrt(node.theSlope)
                dFy = (Fyy - Fy) / dy
                if dFy == 0: dFy = 0.99
                thed = D_Est - Fy / dFy
                D_Est = thed
                if D_Est < 0 or D_Est > 1000000000000 or Count_Iterations > 1000:
                    D_Est = 10 * Rnd #Randomly reseed initial value and step
                    #dy = 1 / ((200 - 100 + 1) * Rnd + 100) # Leftover comment from original code
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
            if self.IniParams.Flag_Muskingum == 0 and Flag_HS < 2 and Flag_SkipNode == 0:
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
