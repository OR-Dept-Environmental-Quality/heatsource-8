from __future__ import division
from itertools import imap, dropwhile
import math, time, operator
from datetime import datetime, timedelta
from DataSheet import DataSheet
from Stream.StreamNode import StreamNode

from Containers.VegZone import VegZone
from Containers.Zonator import Zonator
from Dieties.IniParams import IniParams
from Containers.AttrList import PlaceList, TimeList
from Containers.DataPoint import DataPoint
from Dieties.Chronos import Chronos

#Flag_HS values:
#    0: Flow Router
#    1: Heat Source
#    2: Shadelator

class HeatSourceInterface(DataSheet):
    """Defines a datasheet specific to the Current (version 7, 2006) HeatSource Excel interface"""
    def __init__(self, filename=None, gauge=None):
        if not filename:
            raise Warning("Need a model filename!")
        DataSheet.__init__(self, filename)
        self.__initialize(gauge) # Put all constructor stuff in a method for Psyco optimation

    def __del__(self):
        self.Close() # Close the file and quit Excel process

    def __initialize(self, gauge):
        self.Reach = PlaceList(attr='km', orderdn=True)
        # Build a quick progress bar
        self.PB = gauge

        # Make empty timelists for the boundary conditions
        self.Q_bc = TimeList()
        self.T_bc = TimeList()
        self.C_bc = TimeList()
        #######################################################
        # Grab the initialization parameters from the Excel file.
        # TODO: Ensure that this data doesn't have to come directly from the MainMenu to work
        self.SetSheet("TTools Data")
        IP = IniParams
        IP.Name = self.GetValue("I2")
        IP.Date = self.GetValue("I3")
        IP.dt = self.GetValue("I4")*60
        IP.dx = self.GetValue("I5")
        IP.Length = self.GetValue("I6")
        IP.LongSample = self.GetValue("I7")
        IP.TransSample = self.GetValue("I8")
        IP.InflowSites = int(self.GetValue("I9"))
        IP.ContSites = int(self.GetValue("I10"))
        IP.FlushDays = self.GetValue("I11")
        IP.TimeZone = self.GetValue("I12")
        IP.SimPeriod = self.GetValue("I13")
        ######################################################

        # Page names- maybe a useless tuple, we'll see
        self.pages = ("TTools Data", "Land Cover Codes", "Morphology Data", "Flow Data",
                      "Continuous Data", "Chart-Diel Temp","Validation Data", "Chart-TIR",
                      "Chart-Shade","Output - Hydraulics","Chart-Heat Flux","Chart-Long Temp",
                      "Chart-Solar Flux","Output - Temperature", "Output - Solar Potential",
                      "Output - Solar Surface","Output - Solar Recieved","Output - Longwave",
                      "Output - Evaporation","Output - Convection","Output - Conduction",
                      "Output - Total Heat","Output - Evaporation Rate", "Output - Daily Heat Flux")

#        self.SetupSheets1()

        # from VB: Apparently, only one day is simulated for the shadelator
        # TODO: Check if we need to run for only one day during shadelator-only run.
        Days = IniParams.SimPeriod
        self.Hours = int(IniParams.SimPeriod * 24)

        # Calculate the number of stream node inputs
        # The former subroutine in VB did this by getting each row's value
        # and incrementing a counter if the value was not blank. With the
        # new DataSheet's __getitem__ functionality, we can merely access
        # the sheet once, and return the length of that tuple
        self.PB("Calculating the number of datapoints")
        row = self[:,5][16:] # no row definition, 5th column- strip off the first 16 lines
        self.Num_Q_Var = len(row)

        # Now we start through the steps that were in the first subroutines in the VB code's theModel subroutine
        # We might need to clean up this syntax and logical progression
        self.GetBoundaryConditions()
# TODO: Uncomment after debugging
#        self.ScanMorphology()
        self.BuildStreamNodes()
#        self.GetInflowData()
        self.GetContinuousData()
        self.SetAtmosphericData()

        n = 1
        for i in self.Reach:
            self.PB("Initializing StreamNodes",n,len(self.Reach))
            i.Initialize()
            n+=1
# TODO: Uncomment this after debugging
#        self.SetupSheets2()

        del self.PB

    def SetAtmosphericData(self):
        for node in self.Reach:
            if not node.T_air:
                node.Wind, node.Humidity, node.T_air = self.AtmosphericData
            else:
                self.AtmosphericData = node.Wind, node.Humidity, node.T_air

    def GetBoundaryConditions(self):
        """Get the boundary conditions from the "Continuous Data" page"""
        # Get the columns, which is faster than accessing cells
        col = 7
        row = 16
        time_col = self[:,col-1,"Continuous Data"]
        flow_col = self[:,col,"Continuous Data"]
        temp_col = self[:,col+1,"Continuous Data"]
        cloud_col = self[:,col+2,"Continuous Data"]
        for I in xrange(self.Hours):
            time = Chronos.MakeDatetime(time_col[16+I][0])
            # Get the flow boundary condition
            val = flow_col[row + I][0] # We get the 0th index because each column is actually a 1-length row
            if val == 0 or not val: raise Exception("Missing flow boundary condition for day %i " % int(I / 24))
            self.Q_bc.append(DataPoint(val,time))
            # Temperature boundary condition
            t_val = temp_col[row + I][0]
            if t_val == 0 or not t_val: raise Exception("Missing temperature boundary condition for day %i" % int(I / 24) )
            self.T_bc.append(DataPoint(t_val,time))
            # Cloudiness boundary condition
            self.C_bc.append(DataPoint(cloud_col[row + I][0],time))
            self.PB("Reading boundary conditions",I,self.Hours)

    def GetDataBlock(self, type):
        """Get block of continuous data

        Gets a block of continuous data from a sheet, for a
        number of sites, each with mod different data columns"""
                                  #  (col, sites * datums per site, time column)
        cols = {"Flow Data":         (14, IniParams.InflowSites * 2, 13),
                "Continuous Data":   (11, IniParams.ContSites * 4, 6)
                }
        # Make a list of the times
        time_col = self[:,cols[type][2],type]
        timelist = []
        for II in xrange(self.Hours):
            timelist.append(Chronos.MakeDatetime(time_col[II + 16][0]))

        # Find the bounds of the data block
        c1 = self.excelize(cols[type][0]) # Turn the starting row into an Excel letter
        r1 = 17 # Starting row
        # The end of the data is the starting point, plus the number
        # of inflow sites times two (flow & temp)
        c2 = self.excelize((cols[type][0]-1)+cols[type][1])
        r2 = 17+self.Hours # Ending row
        addr = "%s%i:%s%i" % (c1,r1,c2,r2) # Make an excel address string for the get call
        # This gives us a grid of values
        return self.GetValue(addr, type), timelist


    def GetInflowData(self):
        """Get accumulation data from the "Flow Data" page"""
        data,timelist = self.GetDataBlock("Flow Data")

        # Now we have all the data, we loop through setting our values in the
        # TimeList() instances
        for site in xrange(IniParams.InflowSites):
            # Get the stream node corresponding to the kilometer of this inflow site.
            # TODO: Check whether this is correct (i.e. whether we need to look upstream or downstream)
            # GetByKm() currently looks downstream
            node = self.Reach[self.GetValue((site + 17, 11),"Flow Data"),1]
            for hour in xrange(self.Hours):
                # Now we make a DataPoint object with the flow and temp, where flow is in the
                # column 0+sitenum*2 and temp is in the column 1+sitenum*2 where sitenum is the
                # number of the inflow site we are on. Thus, for the 0th site, our indexes are
                # 0 and 1. We set the time in this DataPoint to the corresponding hour from the
                # timelist built above, and we append the datapoint to the Q_tribs or T_tribs
                # TimeList instance in the node.
                node.Q_tribs.append(DataPoint(data[hour][site*2], time=timelist[hour]))
                node.T_tribs.append(DataPoint(data[hour][1+site*2], time=timelist[hour]))
            self.PB("Reading Inflow data", site, IniParams.InflowSites)

    def GetContinuousData(self):
        """Get data from the "Continuous Data" page"""
        data, timelist = self.GetDataBlock("Continuous Data")

        for site in xrange(IniParams.ContSites):
            node = self.Reach[self.GetValue((site + 17, 4),"Continuous Data"),1] # Index by kilometer
            for hour in xrange(self.Hours):
                node.Wind.append(DataPoint(data[hour][site*4],time=timelist[hour]))
                node.Humidity.append(DataPoint(data[hour][1+site*4],time=timelist[hour]))
                node.T_air.append(DataPoint(data[hour][2+site*4], time=timelist[hour]))
                #TODO: Uncomment this if necessary, delete it if not. T_stream should be renamed
#                try:
#                    node.T_stream.append(DataPoint(data[hour][3+site*4], time=timelist[hour]))
#                except TypeError, inst:
#                    # Often, Stream Temp will be blank. Let's make sure that we catch that case.
#                    # We set the result to a 999 instead of zero to state that it's unknown
#                    if inst.message == "float() argument must be a string or a number":
#                        node.T_stream.append(DataPoint(999, time=timelist[hour]))
#                    else: raise
            # The VB code essentially uses the last continuous node's
            if not site:
                self.AtmosphericData = [node.Wind, node.Humidity, node.T_air]
            self.PB("Reading continuous data", site, IniParams.ContSites)

    def ScanMorphology(self):
        """Scan morphology variables for null of nonnumeric values"""
        # Start scanning at the 17th row of the spreadsheet
        #TODO: The visual basic code for this routine makes absolutely no sense
        # Included is a transcription of the original, which I've tried to interpret
        self.SetSheet('TTools Data')
        for theRow in xrange(17,self.Num_Q_Var + 16):
            row = self[theRow,:][0] # Get the entire row, rather than accessing each cell, which is slow.
                                    # We need to get the 0th index because it's the first of one row that's returned.
            for theCol in xrange(7,22):
                if theCol == 9: continue #I guess this column can be blank
                try:
                    val = row[theCol]
                except IndexError:
                    raise Exception("Invalid data: row %i, cell %s ... Flow router terminated" %(theRow, self.excelize(theCol)))
                if not (isinstance(val,float) or isinstance(val,int)) or \
                    val == "" or \
                    self.Num_Q_Var <= 0: # Crazy logic... should clean this up
                    raise Exception("Invalid data: row %i, cell %s: '%s' ... Flow router terminated" %(theRow, self.excelize(theCol),val))
            self.PB("Scanning morphology data", theRow, self.Num_Q_Var+16)

    def BuildStreamNodes(self):
        """Create list of StreamNodes from the spreadsheet

        In the original VB code, this was quite different. I will not explain what the old
        code does, but will rather explain the motivation behind this version. We have two
        controlling variables: longitudinal sample rate and the distance step (dx). The
        dx is always a multiple of the longitudinal sample rate. The values within the
        node are the average values of the longitudinal samples that fall within that dx.
        For instance, if longrate=50 and dx=200, then the Slope for the node will be
        the average of 4 longitudinal slopes. This method figures out what the details of
        this breakdown are, then calls GetNode() with those details. GetNode() then returns
        a single node developed from the averages of the dataset."""

        ####################
        # Some convenience variables
        # the distance step must be an exact, greater or equal to one, multiple of the sample rate.
        if (IniParams.dx%IniParams.LongSample
            or IniParams.dx<IniParams.LongSample):
            raise Exception("Distance step must be a multiple of the Longitudinal transfer rate")
        long = IniParams.LongSample
        dx = IniParams.dx
        length = IniParams.Length
        multiple = int(dx/long) #We have this many samples per distance step
        datapoints = self.Num_Q_Var-1 # We subtract one because the first datapoint is a boundary node.
        row = 18 # Current row (Skipping the boundary node row)

        # The first node is a boundary node. Because the discharge, etc. are not calculated, but given
        # as boundary conditions, we want this node to be simply the values of the first longitudinal
        # sample, or row 17 of the Excel spreadsheet.
        self.Reach.append(self.GetNode(17,1)) #append the boundary condition node, row 17
        # Place the boundary conditions in this first streamnode
        for cond in ["Q_bc","T_bc"]:
            setattr(self.Reach[0],cond,getattr(self,cond))
        # We also need to reset the dx of the first node, since it's of a shorter length:
        self.Reach[0].dx = IniParams.LongSample # Set it to the length of the sample rate
        # Now, the meat. Most of the nodes will be developed as some multiple of the longitudinal
        # sample rate. Here, we figure out what that multiple is and append stream nodes for all
        # of the samples.
        for i in range(0, datapoints, multiple):
            self.Reach.append(self.GetNode(row+i,multiple))
            self.PB("Building Stream Nodes", i, datapoints)
        row += i+multiple

        #The last node may not have enough datapoints to be of length multiple*long, so
        # we reset the multiple and if there's a remainder, we reset the last nodes dx
        multiple = datapoints%multiple
        if multiple: # If so, we have to calculate how many extra datapoints there are
            self.Reach[-1].dx = long*multiple


    def GetNode(self, row, multiple):
        ####################
        # And convenience dictionaries
        morph = {'S': 6,
                'n': 7,
                'WD': 9,
                'W_bf': 10,
                'W_b': 11,
                'd_bf': 12,
                'z': 15,
                'Conductivity': 17, # This value needs to be divided by 1000
                'ParticleSize': 18,
                'Embeddedness': 19,
                'Q_cont': 22,
                'd_cont': 23,
                'T_cont': 24}
        flow = {'Q_in': 4,
                'T_in': 5,
                'Q_out': 6}
        ttools = {'Longitude': 5,
                  'Latitude': 6,
                  'Elevation': 7,
                  'Aspect': 9,
                  'Topo_W': 10,
                  'Topo_S': 11,
                  'Topo_E': 12}
        pages = {'Morphology Data': morph, 'TTools Data': ttools, 'Flow Data': flow}
        # This is the node
        node = StreamNode()
        # Figuring out the ending row takes some logic. If h=0, this is the first node, which should be a
        # boundary node developed from the first (headwater) datapoint
        endrow = row+multiple-1
        for page in pages:
            # Get data as a tuple of tuples of len(multiple) and turn it into a list of lists
            data = [[i for i in j] for j in self[row:endrow,:,page]]
            if page == 'Morphology Data':
                node.km = data[-1][4] # Get kilometer, last row, 4th cell
                for i in xrange(len(data)):
                    data[i][20] = 0.0 # Remove the FLIR time so it doesn't cause an error
            # get the zone data before averaging! This is because we would average over the zone code
            # rendering it meaningless
            if page == 'TTools Data': self.GetZoneData(node, data)
            data = [i for i in self.AverageIterables(data)] # Average all the values smartly
            # Now we iterate through the list of averages, and assign the values to the appropriate
            # attributes in the stream node
            for attr,col in pages[page].iteritems():
                try:
                    setattr(node, attr, data[col])
                except IndexError, inst:
                    if inst.message == "list index out of range":
                        # If it's an attribute that we know about, then we can just keep the zero value
                        # that's the default, or at least ignore this run because we have zero + zero.
                        if attr in ['T_cont','d_cont','Q_cont', 'T_in', 'Q_in', 'Q_out']: pass
                        else:
                            print attr, col, len(data), row
                            raise
                    else: raise
        self.InitializeNode(row, node)
        return node
    def GetZoneData(self, node, data):
        """Build a Zonator instance, with VegZone values

        This method builds a Zonator instance from a tuple of data rows.
        The values placed in the VegZone instances are averaged over the
        number of rows returned. This is a bit of a grueling process because
        we have to get the height, density and overhang values for
        each zone in each direction, then we have to Average those over the
        distance step.
        """
        # Land cover codes
        LC = self.GetLandCoverCodes()
        # LC attrs
        attrs = ["VHeight","VDensity"]
        ########################################
        # We build a Zonator instance with lists for all values. This way, we can append
        # values to the list, then average over the values. The Zonator instance, has 7
        # directions, each of which holds 4 VegZone instances
        # with values for the sampled zones in each directions.
        dir = [] # List to save the seven directions
        for Direction in xrange(7):
            z = () #Tuple to store the zones 0-3
            for Zone in xrange(4):
                z += VegZone([],[],[]), #Build the VegZone with lists as values
            dir.append(z) # append to the proper direction
        node.Zone = Zonator(*dir) # Create a Zonator instance and set the node.Zone attribute
        # The values for VHeight and VDensity for emergent vegetation lie in the StreamNode
        node.VDensity = []
        node.VHeight = []
        # Overhang is also in the streamnode, as a separate variable which is a dictionary
        # indexed by direction
        ########################################

        # Now, we add values to the lists as many times as we have rows.
        for i in xrange(len(data)):
            ## Emergent vegetation
            emerg = LC[data[i][13]] # Dictionary of the emergent veg code
            node.VDensity.append(emerg["VDensity"])
            node.VHeight.append(emerg["VHeight"])

            for j,k,zone in node.GetZones():
                # Get the dictionary from the LC code from the ith row at the [14+(j*4)+k]th column
                zdict = LC[data[i][14+(j*4)+k]]
                if zdict["VDensity"] != 0:
                    pass
                if k == 0: #If we're at the first zone of a given direction, set the StreamNode's Overhang for that direction
                    try: node.Overhang[j].append(zdict["Overhang"])
                    except AttributeError:
                        node.Overhang[j] = [zdict["Overhang"]]
                zone.VHeight.append(zdict["VHeight"])
                zone.VDensity.append(zdict["VDensity"])
                zone.Elevation.append(data[i][42+(j*4)+k])

        # Theoretically, we now have lists for all of the values, so we need to average over the lists
        # We use our self.smartaverage() method, so that we take care of any values of None
        # First we average the StreamNode attributes
        node.VHeight, node.VDensity = self.SmartAverage(node.VHeight), self.SmartAverage(node.VDensity)
        for i in xrange(7): node.Overhang[i] = self.SmartAverage(node.Overhang[i])

        # Then we iterate over the zones
        for i,j,zone in node.GetZones():
            zone.VDensity = self.SmartAverage(zone.VDensity)
            zone.VHeight = self.SmartAverage(zone.VHeight)
            zone.Elevation = self.SmartAverage(zone.Elevation)

    def GetLandCoverCodes(self):
        """Return the codes from the Land Cover Codes worksheet as a dictionary of dictionaries"""
        # GetValue() returns a tuple, but we want a list because we have to reverse it
        data = [[j for j in i] for i in self.GetValue("E17:H500","Land Cover Codes")]
        # remove the null values.
        for k in xrange(len(data)):
            row = data[k]
            row.reverse()
            row = [i for i in dropwhile(lambda x:x==None,row)]
            row.reverse()
            data[k] = row
        data.reverse()
        data = [i for i in dropwhile(lambda x:len(x) == 0,data)]
        data.reverse()
        # now, make a dictionary of dictionaries to put stuff in
        d = {}
        for row in data:
            d[row[0]] = {'VHeight': row[1], 'VDensity': row[2], 'Overhang': row[3]}
        return d

    def InitializeNode(self, row, node):
        """Perform some initialization of the StreamNode, and write some values to spreadsheet"""
        ##############################################################
        #Now that we have a stream node, we set the node's dx value, because
        # we have most nodes that are long-sample-distance times multiple,

        # To make our life easier when building the node we created Topo_W,
        # Topo_S, and Topo_E, however,
        # these are better in a dictionary, so we fix that here.
        node.Topo = {"E":node.Topo_E,
                     "W":node.Topo_W,
                     "S":node.Topo_S}
        del node.Topo_E, node.Topo_W, node.Topo_S # Delete the unnecessary attributes
        node.dx = IniParams.dx # Set the space-step
        node.dt = IniParams.dt # Set the node's timestep... this may have to be adjusted to comply with stability
        # Cloudiness is not used as a boundary condition, even though it is only measured at the boundary node
        node.C_bc = self.C_bc
        node.T = self.T_bc[0]
        node.T_prev = self.T_bc[0]
        node.T_sed = self.T_bc[0]
        node.SetBankfullMorphology()
        # Taken from the VB code in SubHydraulics- this doesn't have to run at every
        # timestep, since the values don't change. Thus, we just set horizontal conductivity
        # and porosity once here, and remove the other attributes.
        # TODO: Research this mathematics further
        Dummy1 = node.Conductivity * (1 - node.Embeddedness) #Ratio Conductivity of dominant sunstrate
        Dummy2 = 0.00002 * node.Embeddedness  #Ratio Conductivity of sand - low range
        node.K_h = (Dummy1 + Dummy2) #True horzontal cond. (m/s)
        Dummy1 = node.ParticleSize * (1 - node.Embeddedness) #Ratio Size of dominant substrate
        Dummy2 = 0.062 * node.Embeddedness  #Ratio Conductivity of sand - low range
        node.phi = 0.3683 * (Dummy1 + Dummy2) ** (-1*0.0641) #Estimated Porosity

        del node.Conductivity, node.Embeddedness
        #############################################################
        #The original VB code has this method BFMorph, which calculates some things and
        # spits them back to the spreadsheet. We want to keep everything in the node, but
        # we'll spit these four things back to the spreadsheet for now, until we understand
        # better what the purpose is. Unfortunately, this only calculates for each node, which
        # is a multiple of the rows. So we'll have to figure out whether that's acceptable.
#######
# TODO: Uncomment after debugging
#            self.SetValue((row, 11),node.W_b, sheet="Morphology Data")
#            self.SetValue((row, 12),node.d_bf, sheet="Morphology Data")
#            self.SetValue((row, 13),node.d_ave, sheet="Morphology Data")
#            self.SetValue((row, 14),node.A, sheet="Morphology Data")

    def AverageIterables(self, iterable):
        """Average values in an iterable of iterables, returning a tuple of those averages.

        This method takes a tuple of tuples and averages the values in each index of the tuple,
        returning a tuple of those averages. This method has to be somewhat smart about the
        length of the iterables, and the values that the datasheet contains.
        """
        # Unfortunately, using imap won't work directly because it will only map to the length
        # of the shortest string. Thus, we sort of create our own, non-vectorized imap functionality.
        # It's not as efficient, but we only use this in BuildStreamNodes, which is only run once.
        max = 0
        # Figure out the length of the longest iterable
        for it in iterable:
            max = len(it) if len(it) > max else max
        # Make sure all iterables are of equal length
        for it in iterable:
            while len(it) < max:
                it += None, # Add a None value, kind of a stupid method, but it'll work for now.
        if len(iterable) == 1:
            return iterable[0]
        else:
            return [i for i in map(self.SmartAverage, zip(*iterable))]

    def SmartAverage(self, iterable):
        """Average values over an iterable, ignorning None or returning None if there's no length"""
        smartlen = lambda x: len(x) or 1 # Return length of sequence or 1 for averages
        l = []
        for elem in iterable:
            if elem is not None: l.append(elem)
        try:
            return reduce(operator.add,l)/smartlen(l) # Fast average of a list
        except TypeError, err:
            if err.message == "reduce() of empty sequence with no initial value": # Tried to average all None values
                return None
        else: raise

    def SetupSheets1(self):
        num = 0
        max = 20
        for page in ("Solar Potential","Solar Surface","Solar Received","Longwave",\
              "Evaporation","Convection","Total Heat","Conduction","Evaporation Rate",\
              "Temperature","Hydraulics","Daily Heat Flux"):
            name = "Output - %s" % page
            self.Clear("F16:IV16",name)
            self.Clear("17:50000",name)
            self.PB("Clearing old data", num, max)
            num+=1
        self.Clear("A13:D10000", "Chart-TIR")
        self.Clear("A13:c10000", "Chart-Shade")
        self.Clear("17:50000", "Chart-Diel Temp")
        self.Clear("13:50000", "Chart-Heat Flux")
        self.Clear("13:50000","Chart-Shade")
        self.Clear("13:50000", "Chart-Solar Flux")
        self.PB("Clearing old data", num + 6, max)

    def SetupSheets2(self):
        # This next block was originally in SetupSheets2 in the VB code.
        for i in xrange(self.Num_Q_Var):
            self.SetSheet("Morphology Data")
            cellval = {}
            cellval[1] = self[i + 17, 1] # Location Info
            cellval[2] = self[i + 17, 2] # HS Node
            cellval[3] = self[i + 17, 3] # Long Distance
            cellval[4] = round(self[i + 17, 4], 3)     # Stream km
            for page in ("Solar Potential","Solar Surface","Solar Received","Longwave",\
                  "Evaporation","Convection","Total Heat","Conduction","Evaporation Rate",\
                  "Temperature","Daily Heat Flux", "Hydraulics"):
                name = "Output - %s" % page
                for j in cellval.keys():
                    self.SetValue((i+16,j),cellval[j],sheet=name)
            self.PB("Clearing the Excel sheet and entering new\nvalues. This is an annoyingly long process",i,self.Num_Q_Var)
