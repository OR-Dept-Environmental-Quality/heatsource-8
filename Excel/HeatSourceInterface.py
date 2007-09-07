from __future__ import division
from itertools import imap, dropwhile, izip, chain, repeat
import math, time, operator, bisect
from itertools import chain, ifilterfalse
from datetime import datetime, timedelta
from win32com.client import Dispatch
from os.path import exists, join, split, normpath
from sys import exit
from win32gui import PumpWaitingMessages

from ..Stream.StreamNode import StreamNode
from ..Stream.Zonator import Zonator
from ..Dieties import IniParams
from ..Dieties import Chronos
from ExcelDocument import ExcelDocument
#Flag_HS values:
#    0: Flow Router
#    1: Heat Source
#    2: Shadelator

class HeatSourceInterface(ExcelDocument):
    """Defines an interface specific to the Current (version 8.x) HeatSource Excel interface"""
    def __init__(self, filename=None, log=None, run_type=0):
        ExcelDocument.__init__(self, filename)
        self.run_type = run_type
        self.log = log
        self.Reach = {}
        # Make empty Dictionaries for the boundary conditions
        self.Q_bc = {}
        self.T_bc = {}
        self.C_bc = {}
        self.AtmosphericData = [[],[],[]]
        #######################################################
        # Grab the initialization parameters from the Excel file.
        # TODO: Ensure that this data doesn't have to come directly from the MainMenu to work
        lst = ("name", "date", "dt","dx", "length", "longsample", "transsample", "inflowsites",
               "contsites", "flushdays", "timezone", "simperiod","outputdir","evapmethod",
               "wind_a", "wind_b", "calcevap", "calcalluvium","alluviumtemp","emergent",
                "lidar", "lcdensity","daylightsavings")
        vals = [i[0] for i in self.GetValue("B3:B25","Heat Source Inputs")]
        for i in xrange(len(lst)):
            IniParams[lst[i]] = vals[i]
        IniParams["penman"] = True if IniParams["evapmethod"] == "Penman" else False
        # Make the date a datetime instance
        IniParams["date"] = Chronos.MakeDatetime(IniParams["date"])
        IniParams["dt"] = IniParams["dt"]*60 # make dt measured in seconds
        # Set up the log file in the outputdir
        self.log.SetFile(normpath(join(IniParams["outputdir"],"outfile.log")))
        ######################################################


        # from VB: Apparently, only one day is simulated for the shadelator
        # TODO: Check if we need to run for only one day during shadelator-only run.
        self.Hours = int(IniParams["simperiod"] * 24)

        timelist = [i for i in self.GetColumn(11,"Flow Data")[3:]]
        timelist.reverse()
        timelist = [i for i in dropwhile(lambda x:x=='' or x==None,timelist)]
        timelist.reverse()
        self.timelist = [Chronos.MakeDatetime(i).isoformat(" ")[:-12]+":00:00" for i in timelist]

        # Calculate the number of stream node inputs
        # The former subroutine in VB did this by getting each row's value
        # and incrementing a counter if the value was not blank. With the
        # new DataSheet's __getitem__ functionality, we can merely access
        # the sheet once, and return the length of that tuple
        self.PB("Calculating the number of datapoints")
        self.Num_Q_Var = self.LastRow("TTools Data") - 5

        # Some convenience variables
        # the distance step must be an exact, greater or equal to one, multiple of the sample rate.
        if (IniParams["dx"]%IniParams["longsample"]
            or IniParams["dx"]<IniParams["longsample"]):
            raise Exception("Distance step must be a multiple of the Longitudinal transfer rate")
        self.long = IniParams["longsample"]
        self.dx = IniParams["dx"]
        self.length = IniParams["length"]
        self.multiple = int(self.dx/self.long) #We have this many samples per distance step
        #####################

        # Now we start through the steps that were in the first subroutines in the VB code's theModel subroutine
        # We might need to clean up this syntax and logical progression
        self.GetBoundaryConditions()
#        self.ScanMorphology()
        # Land cover codes
        self.BuildNodes()
        if IniParams["lidar"]: self.BuildZonesLidar()
        else: self.BuildZonesNormal()
        self.GetInflowData()
        self.GetContinuousData()
        self.SetAtmosphericData()
        self.PB("Initializing StreamNodes")
        [x.Initialize() for x in self.Reach.itervalues()]
        # Now we manually set each nodes next and previous kilometer values
        l = self.Reach.keys()
        l.sort(reverse=True) # Sort descending, because streams are numbered from the mouth up
        for i in xrange(len(l)):
            key = l[i] # The current node's key
            # Then, set pointers to the next and previous nodes
            if i == 0: pass
            else: self.Reach[key].prev_km = self.Reach[l[i-1]] # At first node, there's no previous
            try:
                self.Reach[key].next_km = self.Reach[l[i+1]]
            except IndexError:
            ##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ## For last node (mouth) we set the downstream node equal to self, this is because
            ## we want to access the node's temp if there's no downstream, and this safes us an
            ## if statement.
                self.Reach[key].next_km = self.Reach[key]


    def CheckEarlyQuit(self):
        PumpWaitingMessages()
        if exists("c:\\quitHS"):
            self.PB("Simulation stopped by user")
            raise Exception("User forced quit")

    def SetAtmosphericData(self):
        self.CheckEarlyQuit()
        for node in self.Reach.itervalues():
            if not node.T_air:
                node.Wind, node.Humidity, node.T_air = self.AtmosphericData
            else:
                self.AtmosphericData = node.Wind, node.Humidity, node.T_air


    def GetBoundaryConditions(self):
        """Get the boundary conditions from the "Continuous Data" page"""
        self.CheckEarlyQuit()
        # Get the columns, which is faster than accessing cells
        self.PB("Reading boundary conditions")
        C = Chronos
        Rstart,Cstart = 5,5
        Rend = Rstart+self.Hours-1
        Cend = 8
        rng = ((Rstart,Cstart),(Rend,Cend))
        data = self.GetValue(rng,"Continuous Data")
        time_col = [x[0] for x in data]
        flow_col = [x[1] for x in data]
        temp_col = [x[2] for x in data]
        cloud_col = [x[3] for x in data]

        for I in xrange(self.Hours):
            time = C.MakeDatetime(time_col[I]).isoformat(" ")[:-6]
            # Get the flow boundary condition
            val = flow_col[I]
            if val == 0 or not val: raise Exception("Missing flow boundary condition for day %i " % int(I / 24))
            self.Q_bc[time] = val
            # Temperature boundary condition
            t_val = temp_col[I]
            #if t_val == 0 or not t_val: raise Exception("Missing temperature boundary condition for day %i" % int(I / 24) )
            self.T_bc[time] = t_val
            # Cloudiness boundary condition
            self.C_bc[time] = cloud_col[I]
            self.PB("Reading boundary conditions",I,self.Hours)

    def GetInflowData(self):
        """Get accumulation data from the "Flow Data" page"""
        self.CheckEarlyQuit()
        # Now we have all the data, we loop through setting our values in the
        # TimeList() instances
        self.PB("Reading Inflow Data")
        l = self.Reach.keys()
        l.sort()
        timelist = self.timelist
        Rstart,Cstart = 4,12
        Rend = Rstart+self.Hours-1
        Cend = int((IniParams["inflowsites"]-1)*2 + Cstart+3)
        rng = ((Rstart,Cstart),(Rend,Cend))
        data = self.GetValue(rng,"Flow Data")
        for site in xrange(int(IniParams["inflowsites"])):
            # Get the stream node corresponding to the kilometer of this inflow site.
            km = self.GetValue((site + 4, 9),"Flow Data")
            key = bisect.bisect(l,km)-1
            node = self.Reach[l[key]] # Index by kilometer
            flow_col = [x[site*2] for x in data]
            temp_col = [x[1+(site*2)] for x in data]
            for hour in xrange(self.Hours):
                try:  #already a tributary, need to mass balance for T
                    node.T_tribs[timelist[hour]] = (temp_col[hour]*flow_col[hour] + node.T_tribs[timelist[hour]]*node.Q_tribs[timelist[hour]]) / (node.Q_tribs[timelist[hour]] + flow_col[hour])
                    node.Q_tribs[timelist[hour]] += flow_col[hour]
                except:# KeyError:
                    node.Q_tribs[timelist[hour]] = flow_col[hour]
                    node.T_tribs[timelist[hour]] = temp_col[hour]
            self.PB("Reading inflow data",site, IniParams["inflowsites"])

    def GetContinuousData(self):
        """Get data from the "Continuous Data" page"""
        self.CheckEarlyQuit()
        self.PB("Reading Continuous Data")
        l = self.Reach.keys()
        l.sort()
        timelist = self.timelist
        Rstart,Cstart = 5,10
        Rend = Rstart+self.Hours-1
        Cend = int((IniParams["contsites"])*4 + Cstart-1)
        rng = ((Rstart,Cstart),(Rend,Cend))
        data = self.GetValue(rng,"Continuous Data")
        for site in xrange(int(IniParams["contsites"])):
            km = self.GetValue((site + 5, 3),"Continuous Data")
            key = bisect.bisect(l,km)-1
            node = self.Reach[l[key]] # Index by kilometer

            wind_col = [x[site*4] for x in data]
            humid_col = [x[1+(site*4)] for x in data]
            for hum_val in humid_col:
                print hum_val
                if hum_val >1 or hum_val < 0: raise Exception("Humidity of %s not bounded in 0<=x<=1" % `hum_val`)
            air_col =  [x[2+(site*4)] for x in data]
            for hour in xrange(self.Hours):
                node.Wind[timelist[hour]] = wind_col[hour]
                node.Humidity[timelist[hour]] = humid_col[hour]
                node.T_air[timelist[hour]] = air_col[hour]
            # The VB code essentially uses the last continuous node's
            if not site:
                self.AtmosphericData = [node.Wind, node.Humidity, node.T_air]
            self.PB("Reading continuous data", site, IniParams["contsites"])

    def ScanMorphology(self):
        """Scan morphology variables for null of nonnumeric values"""
        self.CheckEarlyQuit()
        # Start scanning at the 17th row of the spreadsheet
        #TODO: The visual basic code for this routine makes absolutely no sense
        # Included is a transcription of the original, which I've tried to interpret
        for theRow in xrange(5,self.Num_Q_Var + 5):
            row = self.GetRow(theRow,"TTools Data") # Get the entire row, rather than accessing each cell, which is slow.
            for theCol in xrange(7,38):
                val = row[theCol]
                if val == '':
                    raise Exception("Invalid data: row %i, cell %s ... Flow router terminated" %(theRow, theCol))
                if not (isinstance(val,float) or isinstance(val,int)) or \
                    val == "" or \
                    self.Num_Q_Var <= 0: # Crazy logic... should clean this up
                    raise Exception("Invalid data: row %i, cell %s: '%s' ... Flow router terminated" %(theRow, theCol,val))
            self.PB("Scanning morphology data", theRow, self.Num_Q_Var+5)

    def zipper(self,iterable,mul=2):
        """Zippify list by grouping <mul> consecutive elements together

        Zipper returns a list of lists where the internal lists are groups of <mul> consecutive
        elements from the input list. For example:
        >>> lst = [0,1,2,3,4,5,6,7,8,9]
        >>> zipper(lst)
        [[0],[1,2],[3,4][5,6],[7,8],[9]]
        The first element is a length 1 list because we assume that it is a single element node.
        Note that the last element, 9, is alone as well, this method will figure out when there are not
        enough elements to make n equal length lists, and modify itself appropriately so that the remaining list
        will contain all leftover elements. The usefulness of this method is that it will allow us to average over each <mul> consecutive elements
        """
        # From itertools recipes... We use all but the first (boundary node) element
        lst = [i for i in izip(*[chain(iterable[1:], repeat(None, mul-1))]*mul)]
        # Then we tack on the boundary node element
        lst.insert(0,(iterable[0],))
        # Then strip off the None values from the last (if any)
        lst[-1] = tuple(ifilterfalse(lambda x: x is None,lst[-1]))
        return self.numify(lst)

    def numify(self, lst):
        """Take a list of iterables and remove all values of None or empty strings"""
        # Remove None values at the end of each individual list
        for i in xrange(len(lst)):
            l = [x for x in lst[i]]
            l.reverse()
            l = [x for x in dropwhile(lambda x:x==None, l)]
            l.reverse()
            lst[i] = l
        # Remove blank strings from within the list
        for l in lst:
            n = []
            for i in xrange(len(l)):
                if l[i] == "": n.append(i)
            n.reverse()
            for i in n: del l[i]
        # Make sure there are no zero length lists because they'll fail if we average
        for i in xrange(len(lst)):
            if len(lst[i]) == 0: lst[i].append(0.0)
        return lst

    def multiplier(self, iterable, predicate=lambda x:x):
        """Return an iterable that was run through the zipper and had predicate operated on each element of"""
        stripNone = lambda y: [i for i in ifilterfalse(lambda x: x is None, y)]
        return [predicate(stripNone(x)) for x in self.zipper(iterable,self.multiple)]

    def zeroOutList(self, lst):
        """Replace blank values in a list with zeros"""
        test = lambda x: 0.0 if x=="" else x
        return [test(i) for i in lst]
    def GetColumnarData(self):
        """return a dictionary of attributes that are averaged or summed as appropriate"""
        self.CheckEarlyQuit()
        # Pages we grab columns from
        ttools = ["km","Longitude","Latitude"]
        morph = ["Elevation","S","W_bf","WD","z","n","SedThermCond","SedThermDiff","SedDepth",
                 "hyp_exch","phi","FLIR_time","FLIR_temp","Q_cont","d_cont"]
        flow = ["Q_in","T_in","Q_out"]
        # Ways that we grab the columns
        sums = ["hyp_exch","Q_in","Q_out"] # These are summed, not averaged
        mins = ["km"]
        aves = ["Longitude","Latitude","Elevation","S","W_bf","WD","z","n","SedThermCond",
                "SedThermDiff","SedDepth","phi", "Q_cont","d_cont","T_in"]
        ignore = ["FLIR_temp","FLIR_time"] # Ignore in the loop, set them manually

        data = {}
        # Get all the columnar data from the sheets
        for i in xrange(len(ttools)):
            data[ttools[i]] = self.GetColumn(1+i, "TTools Data")[5:]
        for i in xrange(len(morph)):
            data[morph[i]] = self.GetColumn(2+i, "Morphology Data")[5:]
        for i in xrange(len(flow)):
            data[flow[i]] = self.GetColumn(2+i, "Flow Data")[3:]
        # Then sum and average things as appropriate
        for attr in sums:
            data[attr] = self.multiplier(data[attr],lambda x:sum(x))
        for attr in aves:
            data[attr] = self.multiplier(data[attr],lambda x:sum(x)/len(x))
        for attr in mins:
            data[attr] = self.multiplier(data[attr],lambda x:min(x))
        return data

    def BuildNodes(self):
        self.CheckEarlyQuit()

        data = self.GetColumnarData()
        node = StreamNode(run_type=self.run_type)

        for k,v in data.iteritems():
            setattr(node,k,v[0])
        node.Q_bc = self.Q_bc
        node.T_bc = self.T_bc
        node.C_bc = self.C_bc
        self.InitializeNode(node)
        node.dx = IniParams["longsample"]
        self.Reach[node.km] = node

        #Figure out how many nodes we should have downstream. We use math.ceil() because
        # if we end up with a fraction, that means that there's a node at the end that
        # is not a perfect multiple of the sample distance.
        num_nodes = int(math.ceil((self.Num_Q_Var-1)/self.multiple))
        for i in range(0, num_nodes):
            node = StreamNode(run_type=self.run_type)
            for k,v in data.iteritems():
                setattr(node,k,v[i+1])# Add one to ignore boundary node
            self.InitializeNode(node)
            self.Reach[node.km] = node
            self.PB("Building Stream Nodes", i, self.Num_Q_Var/self.multiple)
        mouth = self.Reach[min(self.Reach.keys())]
        mouth_dx = (self.Num_Q_Var-1)%self.multiple or 1.0 # number of extra variables if we're not perfectly divisible
        mouth.dx = IniParams["longsample"] * mouth_dx

    def BuildZonesNormal(self):
        self.CheckEarlyQuit()
        LC = self.GetLandCoverCodes()
        vheight = []
        vdensity = []
        overhang = []
        elevation = []
        average = lambda x:sum(x)/len(x)

        keys = self.Reach.keys()
        keys.sort(reverse=True)
        self.PB("Building VegZones")
        for i in xrange(7, 36):
            col = self.GetColumn(i, "TTools Data")[5:]
            elev = self.GetColumn(i+28,"TTools Data")[5:]
            # Make a list from the LC codes from the column, then send that to the multiplier
            # with a lambda function that averages them appropriately
            try:
                vheight.append(self.multiplier([LC[x][0] for x in col], average))
                vdensity.append(self.multiplier([LC[x][1] for x in col], average))
                overhang.append(self.multiplier([LC[x][2] for x in col], average))
            except KeyError, (stderr):
                raise Exception("At least one land cover code from the 'TTools Data' worksheet is not in 'Land Cover Codes' worksheet (%s)." % stderr.message)
            if i>7:  #We don't want to read in column AJ
                elevation.append(self.multiplier(elev, average))
        # We have to set the emergent vegetation, so we strip those off of the iterator
        # before we record the zones.
        for i in xrange(len(keys)):
            node = self.Reach[keys[i]]
            node.VHeight = vheight[0][i]
            node.VDensity = vdensity[0][i]
            node.Overhang = overhang[0][i]

        topo_w = self.multiplier(self.GetColumn(4, "TTools Data")[5:], average)
        topo_s = self.multiplier(self.GetColumn(5, "TTools Data")[5:], average)
        topo_e = self.multiplier(self.GetColumn(6, "TTools Data")[5:], average)

        for h in xrange(len(keys)):
            node = self.Reach[keys[h]]
            VTS_Total = 0 #View to sky value
            LC_Angle_Max = 0
            # Now we set the topographic elevations in each direction
            node.TopoFactor = (topo_w[h] + topo_s[h] + topo_e[h])/(90*3) # Originally in CalcSolarFlux #3.. Above Stream Surface
            ElevationList = (topo_e[h],
                             topo_e[h],
                             0.5*(topo_e[h]+topo_s[h]),
                             topo_s[h],
                             0.5*(topo_s[h]+topo_w[h]),
                             topo_w[h],
                             topo_w[h])

            for i in xrange(7):
                T_Full = () # lowest angle necessary for full sun
                T_None = () # Highest angle necessary for full shade
                rip = ()
                for j in xrange(4):
                    Vheight = vheight[i*4+j+1][h]
                    Vdens = vdensity[i*4+j+1][h]
                    Overhang = overhang[i*4+j+1][h]
                    Elev = elevation[i*4+j][h]

                    # First, get the averages for each zone in each direction
                    if not j:
                        LC_Angle_Max = 0 # New value for each direction
                    else:
                        Overhang = 0
                    ##########################################################
                    # Calculate the relative ground elev:
                    SH = Elev - node.Elevation
                    # Then calculate the relative vegetation height:
                    VH = Vheight + SH
                    # Calculate the riparian extinction value
                    try:
                        RE = -math.log(1-Vdens)/10
                    except:
                        if Vdens == 1: RE = 1 # cannot take log of 0
                        else: raise
                    # Calculate the node distance
                    LC_Distance = IniParams["transsample"] * (j + 0.5) #This is "+ 0.5" because j starts at 0.
                    if not j: LC_Distance -= Overhang
                    if LC_Distance < 0:
                        LC_Distance = 0.00001
                    # Calculate the minimum sun angle needed for full sun
                    #T_Full.append(math.atan(math.radians(VH/LC_Distance)))  I think this should be ...
                    T_Full += math.degrees(math.atan(VH/LC_Distance)),
                    # Now get the maximum of bank shade and topographic shade for this
                    # direction
                    T_None += math.degrees(math.atan(SH/LC_Distance)),
                    ##########################################################
                    # Now we calculate the view to sky value
                    Dummy1 = Vheight + (Elev - node.Elevation)
                    Dummy2 = IniParams["transsample"] * (j + 0.5) - Overhang  #This is "+ 0.5" because j starts at 0.
                    LC_Angle = math.degrees(math.atan(VH / LC_Distance) * Vdens)  #TODO: do we really want to multiply by Vdens?
                    if not j or LC_Angle_Max < LC_Angle:
                        LC_Angle_Max = LC_Angle
                    if j == 3: VTS_Total += LC_Angle_Max # Add angle at end of each zone calculation
                    rip += RE,
                node.ShaderList += (max(T_Full), ElevationList[i], max(T_None), rip, T_Full),
            node.ViewToSky = 1 - VTS_Total / (7 * 90)
            self.PB("Building VegZones", h, len(keys))
    def BuildZonesLidar(self):
        """Build zones if we are using LiDAR data"""
        self.CheckEarlyQuit()
        raise NotImplementedError("LiDAR not yet implemented")

    def GetLandCoverCodes(self):
        """Return the codes from the Land Cover Codes worksheet as a dictionary of dictionaries"""
        self.CheckEarlyQuit()
        # GetValue() returns a tuple, but we want a list because we have to reverse it
        codes = self.GetColumn(1, "Land Cover Codes")[3:]
        height = self.GetColumn(2, "Land Cover Codes")[3:]
        dens = self.GetColumn(3, "Land Cover Codes")[3:]
        over = self.GetColumn(4, "Land Cover Codes")[3:]
        vals = [[j for j in i] for i in zip(height,dens,over)]
        data = {}
        for i in xrange(len(codes)):
            # Each code is a tuple in the form of (VHeight, VDensity, Overhang)
            data[codes[i]] = (vals[i][0],vals[i][1],vals[i][2])
        return data

    def InitializeNode(self, node):
        """Perform some initialization of the StreamNode, and write some values to spreadsheet"""
        timelist = self.timelist
        for hour in xrange(self.Hours):
            node.Q_tribs[timelist[hour]] = 0.0
            node.T_tribs[timelist[hour]] = 0.0
        ##############################################################
        #Now that we have a stream node, we set the node's dx value, because
        # we have most nodes that are long-sample-distance times multiple,
        node.dx = IniParams["dx"] # Nodes distance step.
        node.dt = IniParams["dt"] # Set the node's timestep... this may have to be adjusted to comply with stability
        # Cloudiness is not used as a boundary condition, even though it is only measured at the boundary node
        node.C_bc = self.C_bc
        # Find the earliest temperature condition
        mindate = min(self.T_bc.keys())
        if self.run_type == 2: # Running hydraulics only
            node.T, node.T_prev, node.T_sed = 0.0, 0.0, 0.0
        else:
            if self.T_bc[mindate] is None:
                raise Exception("Boundary temperature conditions cannot be blank")
            node.T = self.T_bc[mindate]
            node.T_prev = self.T_bc[mindate]
            node.T_sed = self.T_bc[mindate]
        node.Q_hyp = 0 # Assume zero hyporheic flow unless otherwise calculated
        node.E = 0 # Same for evaporation
        node.T_alluv = IniParams["alluviumtemp"] if IniParams["calcalluvium"] else 0.0

        node.SetBankfullMorphology()
