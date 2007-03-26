from __future__ import division
from itertools import imap
import math, time, operator
from datetime import datetime, timedelta
from DataSheet import DataSheet
from StreamNode import StreamNode

from Utils.TimeUtil import TimeUtil
from Utils.ProgressBar import ProgressBar
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from Utils.IniParams import IniParams
from Utils.BoundCond import BoundCond
from Utils.AttrList import PlaceList, TimeList
from Utils.DataPoint import DataPoint
from Utils.TimeStepper import TimeStepper

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
        self.__initialize(Flag_HS) # Put all constructor stuff in a method for Psyco optimation

    def __del__(self):
        self.Close() # Close the file and quit Excel process

    def __initialize(self, Flag_HS):
        self.Reach = PlaceList(attr='km', orderdn=True)
        self.IniParams = IP = IniParams.getInstance()
        self.BC = BC = BoundCond.getInstance()
        # Build a quick progress bar
        self.PB = ProgressBar(1000)
        self.PB("Initializing Excel interface")

        #######################################################
        # Grab the initialization parameters from the Excel file.
        # TODO: Ensure that this data doesn't have to come directly from the MainMenu to work
        self.SetSheet("TTools Data")
        IP.Name = self.GetValue("I2")
        IP.Date = self.GetValue("I3")
        IP.dt = self.GetValue("I4")
        IP.Dx = self.GetValue("I5")
        IP.Length = self.GetValue("I6")
        IP.LongSample = self.GetValue("I7")
        IP.TransSample = self.GetValue("I8")
        IP.InflowSites = int(self.GetValue("I9"))
        IP.ContSites = int(self.GetValue("I10"))
        IP.FlushDays = self.GetValue("I11")
        IP.TimeZone = self.GetValue("I12")
        IP.SimPeriod = self.GetValue("I13")
        ######################################################

        #######################################################
        ## Time class objects
        # Create a time manipulator for making time objects
        self.TimeUtil = TimeUtil()

        # Create a TimeStepper iterator
        dt = timedelta(minutes=IP.dt)
        start = self.TimeUtil.MakeDatetime(IP.Date)
        stop = start + timedelta(days=IP.SimPeriod)
        self.Timer = TimeStepper(start, dt, stop)
        ##########################################################

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
        if Flag_HS != 2: Days = self.IniParams.SimPeriod
        else: Days = 1
        self.Hours = int(self.IniParams.SimPeriod * 24) if Flag_HS != 2 else 24

        # Calculate the number of stream node inputs
        # The former subroutine in VB did this by getting each row's value
        # and incrementing a counter if the value was not blank. With the
        # new DataSheet's __getitem__ functionality, we can merely access
        # the sheet once, and return the length of that tuple
        row = self[:,5][16:] # no row definition, 5th column- strip off the first 16 lines
        self.Num_Q_Var = len(row)

        # Now we start through the steps that were in the first subroutines in the VB code's theModel subroutine
        # We might need to clean up this syntax and logical progression
        self.GetBoundaryConditions()
#        self.ScanMorphology()
        self.BuildStreamNodes2()
        self.GetInflowData()
        self.GetContinuousData()
        map(lambda x:x.ViewToSky(),self.Reach)
        map(lambda x:x.CalcStreamGeom(),self.Reach)
        # TODO: Uncomment this after debugging
        #self.SetupSheets2()

        del self.PB

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
            time = self.TimeUtil.MakeDatetime(time_col[16+I][0])
            # Get the flow boundary condition
            val = flow_col[row + I][0] # We get the 0th index because each column is actually a 1-length row
            if val == 0 or not val: raise Exception("Missing flow boundary condition for day %i " % int(I / 24))
            self.BC.Q.append(DataPoint(val,time))
            # Temperature boundary condition
            t_val = temp_col[row + I][0]
            if t_val == 0 or not t_val: raise Exception("Missing temperature boundary condition for day %i" % int(I / 24) )
            self.BC.T.append(DataPoint(t_val,time))
            # Cloudiness boundary condition
            self.BC.C.append(DataPoint(cloud_col[row + I][0],time))
            self.PB("Reading boundary conditions",I,self.Hours)

    def GetInflowData(self):
        """Get accumulation data from the "Flow Data" page"""
        #====================================================
        # Account for inflow volumes
        for I in xrange(self.IniParams.InflowSites):
            # Get the stream node corresponding to the kilometer of this inflow site.
            # TODO: Check whether this is correct (i.e. whether we need to look upstream or downstream)
            # GetByKm() currently looks downstream
            node = self.Reach[self.GetValue((I + 17, 11),"Flow Data"),1]
            # Get entire flow and temp columns in one call each
            flow_col = self[:, 13 + I * 2,"Flow Data"]
            temp_col = self[:, 14 + I * 2,"Flow Data"]
            time_col = self[:, 12, "Flow Data"]
            tribs = TimeList()
            for II in xrange(Hours):
                time = self.TimeUtil.MakeDatetime(time_col[II+16][0])
                flow = flow_col[II + 16][0]
                temp = temp_col[II + 16][0]
                tribs.append(DataPoint(flow, time=time))
                val = temp * flow if self.Flag_HS else temp
                node.T_In.append(DataPoint(val, time=time))
            # Set the node's tributary list to the inflow list
            node.Q_tribs = tribs
            self.PB("Getting inflow data", I, self.IniParams.InflowSites)

    def GetContinuousData(self):
        """Get data from the "Continuous Data" page"""
        for I in xrange(self.IniParams.ContSites):
            node = self.Reach[self.GetValue((I + 17, 4),"Continuous Data"),1] # Index by kilometer
            wind_col = self[:,11 + (I * 4),"Continuous Data"]
            humidity_col = self[:,12 + (I * 4),"Continuous Data"]
            air_col = self[:,13 + (I * 4),"Continuous Data"]
            time_col = self[:,6,"Continuous Data"]
            wind_lst = TimeList()
            air_lst = TimeList()
            hum_lst = TimeList()
            for II in xrange(self.Hours):
                time = self.TimeUtil.MakeDatetime(time_col[II + 16][0])
                node.Wind.append(DataPoint(wind_col[II + 16][0],time=time))
                node.Humidity.append(DataPoint(humidity_col[II + 16][0],time=time))
                node.T_air.append(DataPoint(air_col[II + 16][0], time=time))
            node.Wind = wind_lst
            node.T_air = air_lst
            node.Humidity = hum_lst
            self.PB("Reading continuous data", I, self.IniParams.ContSites)

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

    def BuildStreamNodes2(self):
        """Create list of StreamNodes from the spreadsheet

        In the original VB code, this was quite different. I will not explain what that
        code does, but will rather explain the motivation behind this version. We have two
        controlling variables: longitudinal sample rate and the distance step (dx). The
        dx is always a multiple of the longitudinal sample rate. The values within the
        node are the average values of the longitudinal samples that fall within that dx.
        For instance, if longrate=50 and dx=200, then the Slope for the node will be
        the average of 4 longitudinal slopes."""

        ####################
        # Some convenience variables
        # the distance step must be an exact, greater or equal to one, multiple of the sample rate.
        if (self.IniParams.Dx%self.IniParams.LongSample
            or self.IniParams.Dx<self.IniParams.LongSample):
            raise Exception("Distance step must be a multiple of the Longitudinal transfer rate")
        long = self.IniParams.LongSample
        dx = self.IniParams.Dx
        length = self.IniParams.Length
        multiple = int(dx/long) #We have this many samples per distance step
        nodes = int(self.Num_Q_Var/multiple)
        row = 17 # Current row
        ####################
        # And convenience dictionaries
        morph = {'S': 6,
                'n': 7,
                'WD': 9,
                'W_bf': 10,
                'W_b': 11,
                'd_bf': 12,
                'z': 15,
                #'X_Weight': 16,
                'Conductivity': 17, # This value needs to be divided by 1000
                'ParticleSize': 18,
                'Embeddedness': 19,
                'FLIR_Time': 20,
                'FLIR_Temp': 21,
                'Q_cont': 22,
                'd_cont': 23,
                'T_cont': 24}
        flow = {'Q_in': 4,
                'T_in': 5,
                'Q_out': 6,}
        ttools = {'Longitude': 5,
                  'Latitude': 6,
                  'Elevation': 7,
                  'Aspect': 9,
                  'Topo_W': 10,
                  'Topo_S': 11,
                  'Topo_E': 12,
                  'VHeight': 159,
                  'VDensity': 160}
        pages = {'Morphology Data': morph, 'TTools Data': ttools, 'Flow Data': flow}

        # Using this method, we can cycle through all of the nodes in self.Reach, which should coorespond
        # to the number of rows of data. If it doesn't, then the way we set Num_Q_Var should be changed.
        for h in xrange(nodes):
            # This is the node
            node = StreamNode()
            endrow = row+multiple-1 # Ending row for a get call
            for page in pages:
                # Get data as a tuple of tuples of len(multiple)
                data = self[row:endrow,:,page]
                if page == 'Morphology Data':
                    node.km = data[multiple-1][4] # Get kilometer, last row, 4th cell
                data = [i for i in self.smartaverage(data)] # Average all the values smartly
                # Now we iterate through the list of averages, and assign the values to the appropriate
                # attributes in the stream node
                for attr,col in pages[page].iteritems():
                    try:
                        setattr(node, attr, data[col])
                    except IndexError, inst:
                        if inst.message == "list index out of range":
                            # If it's an attribute that we know about, then we can just keep the zero value
                            # that's the default, or at least ignore this run because we have zero + zero.
                            if attr in ['T_cont','d_cont','Q_cont']: pass
                            else:
                                print attr, col, len(data)
                                raise
                # We are going to build the VegZone and Zonator instances We have to do this for each cardinal
                # direction and for 5 zones/direction. They are built in the StreamNode constructor and all
                # values are set to zero by default, so we can just add values here and feel confident the
                # addition will not fail.
                if page == 'TTools Data':
                    for j,k,zone in node: # j is the cardinal direction, k is the zone number
                        if k == 0: # If we're in the 0th zone
                            zone.Elevation = data[7]
                            zone.Overhang = data[j + 151] or 0
                        else:
                            ecol = data[(j * 4) + 42 + (k-1)]
                            hcol = data[(j * 8) + 71 + ((k-1) * 2)]
                            dcol = data[(j * 8) + 70 + ((k-1) * 2)]
                            zone.Elevation = ecol
                            zone.VHeight = hcol
                            zone.VDensity = dcol
                            zone.SlopeHeight = zone.Elevation - node.Zone[j][0].Elevation

            ##############################################################
            #Now that we have a stream node, we set the node's dx value, because
            # we have most nodes that are long-sample-distance times multiple,
            try:
                node.dx = long * (multiple) # Set the space-step
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
            except: # Shit, something happened, WTF?
                print node, node.S, node.W_bf, node.z, node.WD
                raise
            #############################################################
            #The original VB code has this method BFMorph, which calculates some things and
            # spits them back to the spreadsheet. We want to keep everything in the node, but
            # we'll spit these four things back to the spreadsheet for now, until we understand
            # better what the purpose is. Unfortunately, this only calculates for each node, which
            # is a multiple of the rows. So we'll have to figure out whether that's acceptable.
            self.SetValue((row, 11),node.W_b, sheet="Morphology Data")
            self.SetValue((row, 12),node.d_bf, sheet="Morphology Data")
            self.SetValue((row, 13),node.d_ave, sheet="Morphology Data")
            self.SetValue((row, 14),node.A, sheet="Morphology Data")

            self.Reach.append(node) #append and sort
            row += multiple
            if not self.PB("Building Stream Nodes", row, self.Num_Q_Var*1.5)[0]:
                raise Exception("Building streamnodes cancelled, model stopped")

    def smartaverage(self, iterable):
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
        #########
        smartlen = lambda x: len(x) or 1 # Return length of sequence or 1 for averages
        def ave(*it): # Smart average function
            l = []
            for elem in it:
                if elem is not None: l.append(elem)
            try:
                return reduce(operator.add,l)/smartlen(l) # Fast average of a list
            except TypeError, err:
                if err.message == "reduce() of empty sequence with no initial value": # Tried to average all None values
                    return None
                elif err.message == "bad operand type": # This error occurs when we have a date.
                    # lambda to return a floating point number representing a date
                    timeval = lambda x: time.mktime(time.strptime(x.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S"))
                    # Return the fast average, but map the list to the floating point number lambda above
                    return reduce(operator.add,map(timeval,l))/smartlen(l)
            else: raise
        ########

        return imap(ave, *iterable)


    def BuildStreamNodes(self):
        #TODO: My god, no method should be this long, we need a redesign here!
        # This is the worst kind of programming: Even the bastid who wrote it is clueless.
        # Unfortunately, there's not much we can do about taking all these values from an
        # Excel spreadsheet. Ugh- we need to dump Excel- that's what we need.
        del self.Reach[:] # Make sure we empty any current list

        long = self.IniParams.LongSample
        dx = self.IniParams.Dx
        length = self.IniParams.Length

        # the distance step must be an exact, greater or equal to one, multiple of the sample rate.
        if (dx%long or dx<long): raise Exception("Distance step must be a multiple of the Longitudinal transfer rate")

        multiple = dx/long #We have this many samples per distance step

        # Dictionary of sheet names, StreamNode attributes and corresponding columns within the sheet.
        # This is used in the later loop to fill the stream node with averaged data.
        morph = {'S': 6,
                'n': 7,
                'WD': 9,
                'W_bf': 10,
                'W_b': 11,
                'd_bf': 12,
                'z': 15,
                #'X_Weight': 16,
                'Conductivity': 17, # This value needs to be divided by 1000
                'ParticleSize': 18,
                'Embeddedness': 19,
                'FLIR_Time': 20,
                'FLIR_Temp': 21,
                'Q_cont': 22,
                'd_cont': 23,
                'T_cont': 24}
        flow = {'Q_in': 4,
                'T_in': 5,
                'Q_out': 6,}
        ttools = {'Longitude': 5,
                  'Latitude': 6,
                  'Elevation': 7,
                  'Aspect': 9,
                  'Topo_W': 10,
                  'Topo_S': 11,
                  'Topo_E': 12,
                  'VHeight': 159,
                  'VDensity': 160}
        pages = {'Morphology Data': morph, 'TTools Data': ttools, 'Flow Data': flow}

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

        row = 17 # Current row
        # Take a list and divide its sum by either the length of the list, or 1 if it's of zero length
        def average(lst):
            iszero = lambda x: len(x) or 1
            return sum(lst)/iszero(lst)
        # this is a boolean that allows us to use the while statement to cycle until we want to fail
        GotNodes = False
        QuickExit = False

        while not GotNodes: # Until we get to the end of the data
            node = StreamNode()
            # We want to get the data for a number of datapoints and average them for a node, so
            # we go through and get the data for each row starting at 'row' and continuing 'multiple'
            # times, then we divide by 'multiple'
            for i in xrange(int(multiple)):
                if GotNodes: break # If we set GotNodes to true in an inner loop, we don't necessarily break out of this one.
                test = i == multiple-1 #Are we in the last pass?
                # Set the river mile, we set this each time because we want the river mile
                # to equal the last mile for the combined (averaged) data. In other words, each
                # node accounts for its river mile, and all the upstream river miles until the
                # next node.
                val = self[row+i,4,'Morphology Data']
                # We don't use a simple "if not val" because the last node would probably be
                # zero, which is valid (stream mouth). Thus, we want to see if the value IS the
                # class None
                node.km = val if (val is not None) else node.km
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
                            QuickExit = True # make a quick exit out of the loop
                            break # then scram
                        # Then we send the list to the ave lambda to average it, and set the attribute
                        # to the resulting value
                        setattr(node,attr,average(getattr(node,attr)))
                        # Make sure we get the vegzones
                        for j,k,zone in node: # use StreamNode.__iter__(), we can ignore the indexes, we just want the zone.
                            for attr in ["Elevation","Overhang","VHeight","VDensity"]:
                                setattr(zone, attr, average(getattr(zone,attr)))
                        break
                    # using [get|set]attr() allows us to do all of this with a single list or dictionary,
                    # otherwise, we'd have to set each value independantly, which makes for long, inelegant methods.
                    for attr, col in pages[page].items():
                        try:
                            val = data[col] # Get current value using the attribute's name string
                            if val is None:
                                if test: # we are in the last run, or have a null value, so we average
                                    print data
                                    setattr(node,attr,average(getattr(node,attr)))
                                continue
                            # except when we have to catch some exceptions
                            #
                            # This first exception catches the case when we are given a PyTime object, which occurs whenever
                            # the interface encounters a date/time in the Excel interface. We cannot simply add the time objects
                            # so we work around that in this case.
                            if attr == "FLIR_Time":
                                # And create a floating point number which is seconds since the epoch
                                # Doing this, we can then add another time in seconds, then average them, and then
                                # get the average of the time. I'm not entirely sure if it's useful, but it's done
                                # in the original code, so I'll do it here
                                val = time.mktime(time.strptime(val.Format("%m/%d/%y %H:%M:%S"),"%m/%d/%y %H:%M:%S"))
                        # In this instance, we have an out of range tuple, so that means that we are trying
                        # to access data at the end of a row that doesn't actually exist. Since values of 'None'
                        # at the end of a returned row or column are removed, we could have a row that's too short
                        # to hold data for things like T_Control, which is at the far end of a row.
                        except IndexError, inst:
                            if inst.message == "tuple index out of range":
                                # If it's an attribute that we know about, then we can just keep the zero value
                                # that's the default, or at least ignore this run because we have zero + zero.
                                if attr in ['T_cont','d_cont','Q_cont']: pass
                                else:
                                    print attr, col, len(data)
                                    raise
                        try:
                            getattr(node,attr).append(val) # set the new value
                        except AttributeError: # Value is still None, set to a list
                            setattr(node,attr,[val])
                        if test: # we are in the last run, or have a null value, so we average
                            setattr(node,attr,average(getattr(node,attr)))

            if QuickExit: break # We're done, scram
            # Calculate the distance step, which is the longitudinal sample rate times
            # however many steps we've made. Note: this is not times 'multiple' because
            # we may be getting fewer nodes than that.

            # but the last one may be shorter.
            row += multiple
            self.Reach.append(node)

            # Here, we check if we get a cancel request from the progress bar. We set the maximum value of the progress
            # bar to 1.5 times the number of variables just because... well... what the hell?

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
