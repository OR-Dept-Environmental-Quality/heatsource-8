from __future__ import division
from itertools import imap, dropwhile, izip, chain, repeat
import math, time, operator, bisect, weakref, copy
from itertools import chain, ifilterfalse, count
from datetime import datetime, timedelta
from win32com.client import Dispatch
from os.path import exists, join, split, normpath
from sys import exit
from win32gui import PumpWaitingMessages

from ..Stream.StreamNode import StreamNode
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
        self.ContDataSites = [] # List of kilometers with continuous data nodes assigned.
        #######################################################
        # Grab the initialization parameters from the Excel file.
        lst = {"name": "B4",
               "length": "B5",
               "outputdir": "B6",
               "date": "B8",
               "modelstart": "B9",
               "modelend": "B10",
               "end": "B11",
               "flushdays": "B12",
               "timezone": "B13",
               "daylightsavings": "B14",
               "dt": "E4",
               "dx": "E5",
               "longsample": "E6",
               "transsample": "E7",
               "inflowsites": "E8",
               "contsites": "E9",
               "calcevap": "E11",
               "evapmethod": "E12",
               "wind_a": "E13",
               "wind_b": "E14",
               "calcalluvium": "E15",
               "alluviumtemp": "E16",
               "emergent": "E17",
               "lidar": "E18",
               "lcdensity": "E19" }
        for k,v in lst.iteritems():
            IniParams[k] = self.GetValue(v, "Heat Source Inputs")
        IniParams["penman"] = False
        if IniParams["calcevap"]:
            IniParams["penman"] = True if IniParams["evapmethod"] == "Penman" else False
        # Make the date a datetime instance
        IniParams["date"] = Chronos.MakeDatetime(IniParams["date"])
        IniParams["end"] = Chronos.MakeDatetime(IniParams["end"])
        if IniParams["modelstart"] is None:
            IniParams["modelstart"] = IniParams["date"]
        else:
            IniParams["modelstart"] = Chronos.MakeDatetime(IniParams["modelstart"])
        if IniParams["modelend"] is None:
            IniParams["modelend"] = IniParams["end"]
        else:
            IniParams["modelend"] = Chronos.MakeDatetime(IniParams["modelend"])
        IniParams["dt"] = IniParams["dt"]*60 # make dt measured in seconds
        # Set up the log file in the outputdir
        self.log.SetFile(normpath(join(IniParams["outputdir"],"outfile.log")))
        ######################################################
        # Calculate the length of the simulation period in days and the number of hours
        IniParams["simperiod"] = (IniParams["modelend"]-IniParams["modelstart"]).days + 1
        self.Hours = int(IniParams["simperiod"] * 24)

        # Get a single list of all of the boundary condition times by pulling a whole column from the sheet
        # and stripping off the blank values. This will store ALL times, not only those that we're running.
        # In other words, if we have data for 6 days, but are only running one day, this will get all six days
        # worth of boundary condition times. It's alright for now, not too much data storage or iteration
        timelist = [i for i in self.GetColumn(5,"Continuous Data")[4:]]
        timelist.reverse()
        timelist = [i for i in dropwhile(lambda x:x=='' or x==None,timelist)]
        timelist.reverse()
        # Make sure that they are only value at the top of the hour
        self.timelist = [Chronos.MakeDatetime(i).isoformat(" ")[:-12]+":00:00" for i in timelist]

        # Calculate the number of stream node inputs
        # The former subroutine in VB did this by getting each row's value
        # and incrementing a counter if the value was not blank. With the
        # new DataSheet's __getitem__ functionality, we can merely access
        # the sheet once, and return the length of that tuple
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

        # Now we start through the steps of building a stream reach full of nodes
        self.GetBoundaryConditions()
        self.BuildNodes()
        if IniParams["lidar"]: self.BuildZonesLidar()
        else: self.BuildZonesNormal()
        self.GetInflowData()
        self.GetContinuousData()
        self.SetAtmosphericData()
        self.PB("Initializing StreamNodes")

        # Now we manually set each nodes next and previous kilometer values by stepping through the reach
        l = self.Reach.keys()
        l.sort(reverse=True) # Sort descending, because streams are numbered from the mouth up
        head = self.Reach[max(l)] # The headwater node
        # Set the previous and next kilometer of each node.
        slope_problems = []
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
            # Set a headwater node
            self.Reach[key].head = head
            self.Reach[key].Initialize()
            if self.Reach[key].S <= 0.0: slope_problems.append(key)
        if len(slope_problems):
            raise Exception ("The following reaches have zero slope. Kilometers: %s" %",".join(['%0.3f'%i for i in slope_problems]))

    def close(self):
        del self.T_bc, self.Reach

    def CheckEarlyQuit(self):
        """Checks a value to see whether the user wants to stop the model before we completely set everything up"""
        PumpWaitingMessages()

    def SetAtmosphericData(self):
        """For each node without continuous data, use closest (up or downstream) node's data"""
        self.CheckEarlyQuit()
        self.PB("Setting Atmospheric Data")
        from bisect import bisect
        sites = self.ContDataSites # Localize the variable for speed
        sites.sort() #Sort is necessary for the bisect module
        c = count()
        l = self.Reach.keys()
        # This routine bisects the reach and searches the difference between us and the upp
        for km, node in self.Reach.iteritems():
            if km not in sites:
                # Kilometer's downstream and upstream
                lower = bisect(sites,km)-1 if bisect(sites,km)-1 > 0 else 0 # zero is the lowest (protect against value of -1)
                # bisect returns the length of a list when the bisecting number is greater than the greatest value.
                # Here we protect by max-ing out at the length of the list.
                upper = min([bisect(sites,km),len(sites)-1])
                # Use the indexes to get the kilometers from the sites list
                down = sites[lower]
                up = sites[upper]
                datasite = self.Reach[up] # Initialize to upstream's continuous data
                if km-down < up-km: # Only if the distance to the downstream node is closer do we use that
                    datasite = self.Reach[down]
                self.Reach[km].ContData = datasite.ContData
                self.PB("Setting Atmospheric Data", c.next(), len(l))

    def GetBoundaryConditions(self):
        """Get the boundary conditions from the "Continuous Data" page"""
        self.CheckEarlyQuit()
        # Get the columns, which is faster than accessing cells
        self.PB("Reading boundary conditions")
        C = Chronos
        # Starting and ending rows and columns for this worksheet
        Rstart,Cstart = 5,5
        Rend = Rstart+self.Hours-1
        Cend = 8
        rng = ((Rstart,Cstart),(Rend,Cend))
        # Grab the data block and strip out time, flow and temp columns.
        data = self.GetValue(rng,"Continuous Data")
        time_col = [x[0] for x in data]
        flow_col = [x[1] for x in data]
        temp_col = [x[2] for x in data]

        # Now set the discharge and temperature boundary condition dictionaries.
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
            self.PB("Reading boundary conditions",I,self.Hours)

    def GetInflowData(self):
        """Get accumulation data from the "Flow Data" page"""
        self.CheckEarlyQuit()
        self.PB("Reading Inflow Data")
        # Local variables for reach and timelist
        l = self.Reach.keys()
        l.sort()
        timelist = self.timelist
        # Get the data block from the worksheet
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
            # Strip off the flow and temp columns
            flow_col = [x[site*2] for x in data]
            temp_col = [x[1+(site*2)] for x in data]
            # then set the nodes Q_tribs and T_tribs dictionaries with the values, first checking
            # whether there are improper blank fields.
            for i in xrange(len(flow_col)):
                # Here we test to make sure that the flow and temp columns are not blank
                # Temp can be blank with negative flows because we don't need to mass balance with the temperature
                if flow_col[i] is None or (flow_col[i] > 0 and temp_col[i] is None):
                    if i > Rend: continue # Don't worry about blanks in later date/times if we're not modeling during that time
                    raise Exception("Cannot have a tributary with blank flow or temperature conditions")
            # Here, we actually set the tribs library, appending to a tuple. Q_ and T_tribs are
            # tuples of values because we may have more than one input for a given node
            for hour in xrange(self.Hours):
                node.Q_tribs[timelist[hour]] += flow_col[hour], #Append to tuple
                node.T_tribs[timelist[hour]] += temp_col[hour],
            self.PB("Reading inflow data",site, IniParams["inflowsites"])

    def GetContinuousData(self):
        """Get data from the "Continuous Data" page"""
        # This is remarkably similar to GetInflowData. We get a block of data, then set the dictionary of the node
        self.CheckEarlyQuit()
        self.PB("Reading Continuous Data")
        l = self.Reach.keys()
        l.sort()
        timelist = self.timelist
        Rstart,Cstart = 5,9
        Rend = Rstart+self.Hours-1
        Cend = int((IniParams["contsites"])*5 + Cstart-1)
        rng = ((Rstart,Cstart),(Rend,Cend))
        data = self.GetValue(rng,"Continuous Data")
        for site in xrange(int(IniParams["contsites"])):
            km = self.GetValue((site + 5, 3),"Continuous Data")
            if km is None or not isinstance(km, float):
                # This is a bad dataset if there's no kilometer
                raise Exception("Must have a stream kilometer (e.g. 15.3) for each continuous data node!")
            key = bisect.bisect(l,km)-1
            node = self.Reach[l[key]] # Index by kilometer
            # Append this node to a list of all nodes which have continuous data
            self.ContDataSites.append(node.km)

            # We have a data block, so each row of data contains 4 elements. Here, we grab each
            # element from each row in a list, then do some testing
            cloud_col = [x[site*5] for x in data]    # Grab all of the values in a list
            wind_col = [x[1+(site*5)] for x in data]
            humid_col = [x[2+(site*5)] for x in data]
            air_col =  [x[3+(site*5)] for x in data]
            # Test cloudiness and default to zero if blank
            for i in xrange(len(cloud_col)):
                if cloud_col[i] is None: cloud_col[i] = 0.0
            # Test wind and default to zero if blank
            for i in xrange(len(wind_col)):
                if wind_col[i] is None: wind_col[i] = 0.0
            # test humidity and make sure it's greater than 0
            for hum_val in humid_col:
                if hum_val < 0: raise Exception("Humidity (value of %s in Continuous Data) must be greater than zero" % `hum_val`)
            # Air temp cannot be blank
            for air_val in air_col:
                if air_val is None: raise Exception("Must have values for Air Temp in Continuous Data sheet")
            # Now set the ContData dictionary to a tuple holding the data
            for hour in xrange(self.Hours):
                node.ContData[timelist[hour]] = cloud_col[hour], wind_col[hour], humid_col[hour], air_col[hour]
            self.PB("Reading continuous data", site, IniParams["contsites"])

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
        """Return an iterable that was run through the zipper

        Take an iterable and strip the values of None, then send to the zipper
        and apply predicate to each value returned (zipper returns a list"""
        # This is a way to safely apply a generic lambda function to an iterable
        # First we strip off the None values.
        stripNone = lambda y: [i for i in ifilterfalse(lambda x: x is None, y)]
        return [predicate(stripNone(x)) for x in self.zipper(iterable,self.multiple)]

    def zeroOutList(self, lst):
        """Replace blank values in a list with zeros"""
        test = lambda x: 0.0 if x=="" else x
        return [test(i) for i in lst]

    def GetColumnarData(self):
        """return a dictionary of attributes that are averaged or summed as appropriate"""
        self.CheckEarlyQuit()
        # Pages we grab columns from, and the columns that we grab
        ttools = ["km","Longitude","Latitude"]
        morph = ["Elevation","S","W_b","z","n","SedThermCond","SedThermDiff","SedDepth",
                 "hyp_exch","phi","FLIR_time","FLIR_temp","Q_cont","d_cont"]
        flow = ["Q_in","T_in","Q_out"]
        # Ways that we grab the columns
        sums = ["hyp_exch","Q_in","Q_out"] # These are summed, not averaged
        mins = ["km"]
        aves = ["Longitude","Latitude","Elevation","S","W_b","z","n","SedThermCond",
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
        # Then sum and average things as appropriate. multiplier() takes a tuple
        # and applies the given lambda function to that tuple.
        for attr in sums:
            data[attr] = self.multiplier(data[attr],lambda x:sum(x))
        for attr in aves:
            data[attr] = self.multiplier(data[attr],lambda x:sum(x)/len(x))
        for attr in mins:
            data[attr] = self.multiplier(data[attr],lambda x:min(x))
        return data

    def BuildNodes(self):
        # This is the worst of the methods. At some point, dealing with the collection of data
        # from an excel spreadsheet is going to cause trouble. I tried to keep the trouble to a
        # minimum, but this is one of the bad methods of our interface with Excel.
        self.CheckEarlyQuit()
        self.PB("Building Stream Nodes")
        Q_mb = 0.0
        # Grab all of the data in a dictionary
        data = self.GetColumnarData()
        #################################
        # Build a boundary node
        node = StreamNode(run_type=self.run_type,Q_mb=Q_mb)
        # Then set the attributes for everything in the dictionary
        for k,v in data.iteritems():
            setattr(node,k,v[0])
        # set the flow and temp boundary conditions for the boundary node
        node.Q_bc = self.Q_bc
        node.T_bc = self.T_bc
        self.InitializeNode(node)
        node.dx = IniParams["longsample"]
        self.Reach[node.km] = node
        ############################################

        #Figure out how many nodes we should have downstream. We use math.ceil() because
        # if we end up with a fraction, that means that there's a node at the end that
        # is not a perfect multiple of the sample distance. We might end up ending at
        # stream kilometer 0.5, for instance, in that case
        num_nodes = int(math.ceil((self.Num_Q_Var-1)/self.multiple))
        for i in range(0, num_nodes):
            node = StreamNode(run_type=self.run_type,Q_mb=Q_mb)
            for k,v in data.iteritems():
                setattr(node,k,v[i+1])# Add one to ignore boundary node
            self.InitializeNode(node)
            self.Reach[node.km] = node
            self.PB("Building Stream Nodes", i, self.Num_Q_Var/self.multiple)
        # Find the mouth node and calculate the actual distance
        mouth = self.Reach[min(self.Reach.keys())]
        mouth_dx = (self.Num_Q_Var-1)%self.multiple or 1.0 # number of extra variables if we're not perfectly divisible
        mouth.dx = IniParams["longsample"] * mouth_dx

    def BuildZonesNormal(self):
        """This method builds the sampled vegzones in the case of non-lidar datasets"""
        # Hide your straight razors. This implementation will make you want to use them on your wrists.
        self.CheckEarlyQuit()
        LC = self.GetLandCoverCodes() # Pull the LULC data from the appropriate sheet
        vheight = []
        vdensity = []
        overhang = []
        elevation = []
        average = lambda x:sum(x)/len(x)

        keys = self.Reach.keys()
        keys.sort(reverse=True) # Downstream sorted list of stream kilometers
        self.PB("Building VegZones")
        for i in xrange(7, 36): # For each column of LULC data
            col = self.GetColumn(i, "TTools Data")[5:] # LULC column
            elev = self.GetColumn(i+28,"TTools Data")[5:] # Shift by 28 to get elevation column
            # Make a list from the LC codes from the column, then send that to the multiplier
            # with a lambda function that averages them appropriately. Note, we're averaging over
            # the values (e.g. density) not the actual code, which would be meaningless.
            try:
                vheight.append(self.multiplier([LC[x][0] for x in col], average))
                vdensity.append(self.multiplier([LC[x][1] for x in col], average))
                overhang.append(self.multiplier([LC[x][2] for x in col], average))
            except KeyError, (stderr):
                raise Exception("At least one land cover code from the 'TTools Data' worksheet is blank or not in 'Land Cover Codes' worksheet (Code: %s)." % stderr.message)
            if i>7:  #We don't want to read in column AJ -Dan
                elevation.append(self.multiplier(elev, average))
        # We have to set the emergent vegetation, so we strip those off of the iterator
        # before we record the zones.
        for i in xrange(len(keys)):
            node = self.Reach[keys[i]]
            node.VHeight = vheight[0][i]
            node.VDensity = vdensity[0][i]
            node.Overhang = overhang[0][i]

        # Average over the topo values
        topo_w = self.multiplier(self.GetColumn(4, "TTools Data")[5:], average)
        topo_s = self.multiplier(self.GetColumn(5, "TTools Data")[5:], average)
        topo_e = self.multiplier(self.GetColumn(6, "TTools Data")[5:], average)

        # ... and you thought things were crazy earlier! Here is where we build up the
        # values for each node. This is culled from earlier version's VB code and discussions
        # to try to simplify it... yeah, you read that right, simplify it... you should've seen in earlier!
        for h in xrange(len(keys)):
            node = self.Reach[keys[h]]
            VTS_Total = 0 #View to sky value
            LC_Angle_Max = 0
            # Now we set the topographic elevations in each direction
            node.TopoFactor = (topo_w[h] + topo_s[h] + topo_e[h])/(90*3) # Topography factor Above Stream Surface
            # This is basically a list of directions, each with a sort of average topography
            ElevationList = (topo_e[h],
                             topo_e[h],
                             0.5*(topo_e[h]+topo_s[h]),
                             topo_s[h],
                             0.5*(topo_s[h]+topo_w[h]),
                             topo_w[h],
                             topo_w[h])
            # Sun comes down and can be full-on, blocked by veg, or blocked by topography. Earlier implementations
            # calculated each case on the fly. Here we chose a somewhat more elegant solution and calculate necessary
            # angles. Basically, there is a minimum angle for which full sun is calculated (top of trees), and the
            # maximum angle at which full shade is calculated (top of topography). Anything in between these is an
            # angle for which sunlight is passing through trees. So, for each direction, we want to calculate these
            # two angles so that late we can test whether we are between them, and only do the shading calculations
            # if that is true.

            for i in xrange(7): # Iterate through each direction
                T_Full = () # lowest angle necessary for full sun
                T_None = () # Highest angle necessary for full shade
                rip = () # Riparian extinction, basically the amount of loss due to vegetation shading
                for j in xrange(4): # Iterate through each of the 4 zones
                    # TODO: This was in a try block but with no note and no specific exception listed. Why?
                    try:
                        Vheight = vheight[i*4+j+1][h]
                    except:
                        self.log.write("Problem in BuildZonesNormal() setting Vheight")
                        raise
                    Vdens = vdensity[i*4+j+1][h]
                    Overhang = overhang[i*4+j+1][h]
                    Elev = elevation[i*4+j][h]

                    if not j: # We are at the stream edge, so start over
                        LC_Angle_Max = 0 # New value for each direction
                    else:
                        Overhang = 0 # No overhang away from the stream
                    ##########################################################
                    # Calculate the relative ground elevation. This is the
                    # vertical distance from the stream surface to the land surface
                    SH = Elev - node.Elevation
                    # Then calculate the relative vegetation height
                    VH = Vheight + SH
                    # Calculate the riparian extinction value
                    try:
                        RE = -math.log(1-Vdens)/10
                    except:
                        if Vdens == 1: RE = 1 # cannot take log of 0, RE is full if it's zero
                        else: raise
                    # Calculate the node distance
                    LC_Distance = IniParams["transsample"] * (j + 0.5) #This is "+ 0.5" because j starts at 0.
                    # We shift closer to the stream by the amount of overhang
                    # This is a rather ugly cludge.
                    if not j: LC_Distance -= Overhang
                    if LC_Distance < 0:
                        LC_Distance = 0.00001
                    # Calculate the minimum sun angle needed for full sun
                    T_Full += math.degrees(math.atan(VH/LC_Distance)), # It gets added to a tuple of full sun values
                    # Now get the maximum of bank shade and topographic shade for this
                    # direction
                    T_None += math.degrees(math.atan(SH/LC_Distance)), # likewise, a tuple of values
                    ##########################################################
                    # Now we calculate the view to sky value
                    # LC_Angle is the vertical angle from the surface to the land-cover top. It's
                    # multiplied by the density as a kludge
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
        codes = self.GetColumn(1, "Land Cover Codes")[3:]
        height = self.GetColumn(2, "Land Cover Codes")[3:]
        dens = self.GetColumn(3, "Land Cover Codes")[3:]
        over = self.GetColumn(4, "Land Cover Codes")[3:]
        # make a list of lists with values: [(height[0], dens[0], over[0]), (height[1],...),...]
        vals = [tuple([j for j in i]) for i in zip(height,dens,over)]
        data = {}
        for i in xrange(len(codes)):
            # Each code is a tuple in the form of (VHeight, VDensity, Overhang)
            data[codes[i]] = vals[i]
        return data

    def InitializeNode(self, node):
        """Perform some initialization of the StreamNode, and write some values to spreadsheet"""
        timelist = self.timelist
        # Initialize each nodes tribs dictionary to a tuple
        for hour in xrange(self.Hours):
            node.Q_tribs[timelist[hour]] = ()
            node.T_tribs[timelist[hour]] = ()
        ##############################################################
        #Now that we have a stream node, we set the node's dx value, because
        # we have most nodes that are long-sample-distance times multiple,
        node.dx = IniParams["dx"] # Nodes distance step.
        node.dt = IniParams["dt"] # Set the node's timestep... this may have to be adjusted to comply with stability
        # Find the earliest temperature boundary condition
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
