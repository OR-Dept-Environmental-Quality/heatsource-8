from __future__ import division
from DataSheet import DataSheet
from Utils.Time import TimeUtil
from Utils.ProgressBar import ProgressBar
from StreamNode import StreamNode
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.IniParams import IniParams
from numpy import arange
import math, time, datetime

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
        self.UpdateQVarCount()

        # Build a quick progress bar
        self.PB = ProgressBar(self.IniParams.InflowSites + self.IniParams.ContSites + Hours + self.Num_Q_Var)

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
                'FLIR_Time': 20,
                'FLIR_Temp': 21,
                'Q_Control': 22,
                'D_Control': 23,
                'T_Control': 24}
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
        pages = {'Morphology Data': morph, 'TTools Data': ttools}#, 'Flow Data': flow}

        # This process is quite gruelling. I think that this can probably be cleaned up by
        # getting the entire data matrix in a single call, averaging every X group of values
        # in every column, and dumping that data into the StreamNode. This would be significantly
        # easier than this method. However, since UsedRange does not seem to work, we have to find
        # a way of getting all of the data from a sheet in a non-stupid fashion. However, significant
        # time will have to be spent figuring out how to turn the nature of the spreadsheet into
        # a proper OOP framework.
        # One idea for this is to subclass sheets from DataSheet and have a MorphologySheet,
        # a FlowSheet, etc. Then, we could tie the StreamNode class directly to the DataSheet
        # subclass and have this done internally.
        # TODO: Optimize, or otherwise try to clean up this syntax.

        row = 17 # Current row
        # this is a boolean that allows us to use the while statement to cycle until we want to fail
        GotNodes = False
        while not GotNodes: # Until we get to the end of the data
            node = StreamNode()
            # We want to get the data for a number of datapoints and average them for a node, so
            # we go through and get the data for each row starting at 'row' and continuing 'multiple'
            # times, then we divide by 'multiple'
            for i in xrange(int(multiple)):
                if GotNodes: break # If we set GotNodes to true in an inner loop, we don't necessarily break out of this one.
                test = i == multiple-1 #Are we in the last pass?
                # Set the river mile, we set this each time because we want the river mile
                # to equal the last mile for the combined (averaged) data.
                val = self[row+i,4,'Morphology Data']
                node.RiverKM = val if val else node.RiverKM
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
                         # In that case, we average immediately and scram. However, if we are at
                         # the first pass in 'multiple' then we actually grabbed the last bit of
                         # data during the last pass, meaning we have just built a node with
                         # zero kilometers and no internal data. Thus, we have to figure out if
                         # this is true, and if so, set a condition that allows us to delet the node.
                        GotNodes = True # We're done, either way
                        if not i: # we're at the first pass, i==0
                            del node # Get rid of the node
                            break # then scram
                        val = getattr(node,attr) / (i+1)
                        setattr(node,attr,val)
                        # Make sure we get the vegzones
                        for j,k,zone in node: # use StreamNode.__iter__(), we can ignore the indexes, we just want the zone.
                            for attr in ["Elevation","Overhang","VHeight","VDensity"]:
                                val = getattr(zone,attr) # Get the value
                                val = val / (i+1) if val else val # Divide if not zero, or keep zero if it is
                                setattr(zone, attr, val)
                        break
                    # using [get|set]attr() allows us to do all of this with a single list or dictionary,
                    # otherwise, we'd have to set each value independantly, which makes for long, inelegant methods.
                    for attr, col in pages[page].items():
                        try:
                            val = getattr(node,attr) + data[col] # Get current value using the attribute's name string
                        # except when we have to catch some exceptions
                        #
                        # This first exception catches the case when we are given a PyTime object, which occurs whenever
                        # the interface encounters a date/time in the Excel interface. We cannot simply add the time objects
                        # so we work around that in this case.
                        except TypeError, inst:
                            if inst.message == "unsupported operand type(s) for +: 'int' and 'time'":
                                t = data[col] # get the data
                                # And create a floating point number which is seconds since the epoch
                                # Doing this, we can then add another time in seconds, then average them, and then
                                # get the average of the time. I'm not entirely sure if it's useful, but it's done
                                # in the original code, so I'll do it here
                                #TODO: Explore adding a + operator to the TimeUtil function.
                                d = time.mktime(time.strptime(t.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S"))
                                val = getattr(node,attr) + d # Then add that to the current number
                        # In this instance, we have an out of range tuple, so that means that we are trying
                        # to access data at the end of a row that doesn't actually exist. Since values of 'None'
                        # at the end of a returned row or column are removed, we could have a row that's too short
                        # to hold data for things like T_Control, which is at the far end of a row.
                        except IndexError, inst:
                            if inst.message == "tuple index out of range":
                                # If it's an attribute that we know about, then we can just keep the zero value
                                # that's the default, or at least ignore this run because we have zero + zero.
                                if attr in ['T_Control','D_Control','Q_Control']: pass
                                else:
                                    print attr, col, len(data)
                                    raise

                        setattr(node,attr,val) # set the new value
                        if test: # we are in the last run, or have a null value, so we average
                            val = getattr(node,attr) / multiple
                            setattr(node,attr,val)
                    # We are going to build the VegZone and Zonator instances We have to do this for each cardinal
                    # direction and for 5 zones/direction. They are built in the StreamNode constructor and all
                    # values are set to zero by default, so we can just add values here and feel confident the
                    # addition will not fail.
                    if page == 'TTools Data':
                        #TODO: Create a method in the StreamNode that will automagically cycle this
                        # Somehow, we should automagically cycle through all of the zones in all of
                        # the directions in a single call... that would be sweet!
                        for j,k,zone in node: # j is the cardinal direction, k is the zone number
                            if k == 0: # If we're in the 0th zone
                                zone.Elevation += data[7]
                                try:
                                    zone.Overhang += data[j + 150]
                                except TypeError: # Overhang column is blank, meaning there's no overhang
                                    pass
                            else:
                                zone.Elevation += data[j * 4 + 37 + k]
                                zone.VHeight += data[j * 8 + 61 + k * 2]
                                zone.VDensity += data[j * 8 + 60 + k * 2]
                            if test:
                                for attr in ["Elevation","Overhang","VHeight","VDensity"]:
                                    val = getattr(zone,attr) # Get the value
                                    val = val / multiple if val else val # Divide if not zero, or keep zero if it is
                                    setattr(zone, attr, val)
            if GotNodes: break # We're done, scram
            #############################################################
            #The original VB code has this method BFMorph, which calculates some things and
            # spits them back to the spreadsheet. We want to keep everything in the node, but
            # we'll spit these four things back to the spreadsheet for now, until we understand
            # better what the purpose is. Unfortunately, this only calculates for each node, which
            # is a multiple of the rows. So we'll have to figure out whether that's acceptable.
            # TODO: Figure out whether we should calculate this for each row, or if each node is enough.
            try:
                node.BFMorph()
            except:
                print node, node.Slope, node.Width_BF, node.Z, node.WD
            self.SetValue((i + 17, 11),node.BottomWidth, sheet="Morphology Data")
            self.SetValue((i + 17, 12),node.MaxDepth, sheet="Morphology Data")
            self.SetValue((i + 17, 13),node.AveDepth, sheet="Morphology Data")
            self.SetValue((i + 17, 14),node.BFXArea, sheet="Morphology Data")
            ##############################################################
            #Now that we have a stream node, we set the node's dx value, because
            # we have most nodes that are long-sample-distance times multiple,
            # but the last one may be shorter.
            node.dx = long * (i+1)
            row += multiple
            self.StreamNodeList += node,

            # Here, we check if we get a cancel request from the progress bar. We set the maximum value of the progress
            # bar to 1.5 times the number of variables just because... well... what the hell?
            if not self.PB("Building Stream Nodes", row, self.Num_Q_Var*1.5)[0]:
                raise Exception("Building streamnodes cancelled, model stopped")
        self.PB.Hide()
        raise Exception("Make sure that the node.dx stuff works, then make sure that breaking before the end always works")

    def LoadModelVariables(self,Node,theDistance,Count_Q_Var,Flag_HS):
        """Load model variables (see notes)"""
        # The original VB code contained loops here to average the data in various arrays
        # and then create new arrays with those averaged values. Rather, here we just
        # create StreamNode instances with those averaged values in the BuildStreamNode
        # method, then we do some other stuff here. We separate here and there mainly
        # because there is one "holy-mother-of-god"-big class.
        for node in StreamNodeList:
            wet_area = node.theWidth_BF * self.IniParams.Dx
            node.Area_Wetland += area
            
        
        #======================================================
        #Account for Inflow Volumes
        Count_Q_In = 0 #This was a global variable in the original code
        Flag_Inflow = 0
        I8 = Count_Q_In
        I7 = Count_Q_In

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


        node.theT_Control = (node.theT_Control / control_num['T_Control']) if node.theT_Control else 0

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
