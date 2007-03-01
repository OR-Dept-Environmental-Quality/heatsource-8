from __future__ import division
from unittest import TestCase
from Excel.HeatSourceInterface import HeatSourceInterface
from Utils.Time import TimeUtil

class TestDataSheet(TestCase):
    def setUp(self):
        self.doc = HeatSourceInterface("c:\\eclipse\\HeatSource\\Toketee_CCC.xls")
    def tearDown(self):
        pass

    def test_UpdateQVarCounter(self):
        """Test ability to count variables"""
        self.doc.UpdateQVarCounter()
        self.assertEqual(self.doc.Num_Q_Var,64)

    def test_CheckMorphology(self):
        """Test ability to check morphology"""
        # Sort of a dumb method, we should have better checking.
        self.doc.UpdateQVarCounter()
        self.doc.CheckMorphologySheet()

#    def test_BuildStreamNodes(self):
#        """Test building of stream nodes"""
#        self.doc.UpdateQVarCounter()
#        self.doc.BuildStreamNodes()
#        self.doc.BasicInputs()
#        # Accessing this way tests the __getitem__ method
#        nodelist = self.doc.GetNode(slice(0,3))
#        self.assertEqual(len(nodelist),3)
#        node = nodelist[0]
#        l = (('RiverKM', 3.15),
#             ('Slope', 0.0012),
#             ('N', 0.25),
#             ('Width_BF', 8.5),
#             ('Width_B', 7.9),
#             ('Depth_BF', 0.6),
#             ('Z', 0.5),
#             ('X_Weight', 0.0),
#             ('Conductivity', 30/1000),
#             ('Particle_Size', 250),
#             ('Embeddedness', 0.2),
#             ('Q_Control', 0.3),
#             ('D_Control', 0.4),
#             ('Q_Out', 0.6),
#             ('Q_Accretion', 0.4),
#             ('T_Accretion', 0.5),
#             ('FLIR_Temp', 11.1),
#             ('T_Control', 0.5),
#             ('Longitude', -122.42055784),
#             ('Latitude', 43.2632496),
#             ('Aspect', 283.8),
#             ('Topo_W', 4.2),
#             ('Topo_S', 19.5),
#             ('Topo_E', 15.1),
#             ('VHeight', 0.8),
#             ('VDensity', 0.9),
#             ('Elevation', 737))
#
#        for attr, val in l:
#            self.assertAlmostEqual(getattr(node, attr), val, 5)
#
#        #FLIR_Time
#        l = (('year', 2001), ('month', 07), ('day', 10),
#             ('hour', 14), ('minute', 14), ('second', 0))
#        t = TimeUtil()
#        date = t.MakeDatetime(getattr(node, 'FLIR_Time'))
#        for attr, val in l:
#            self.assertAlmostEqual(getattr(date, attr), val, 5)
#        elev, dens = 1.5199999809265137, 0.64999997615814209
#        # Zones:      Zone 0                Zone 1                   Zone 2                  Zone 3                   Zone 4
#        d = {'NE': ((737, 0, 0, 0.1), (741,   0,    0,    0), (741,   0,    0,    0), (740.1, 0,    0,    0), (740.1, 0,    0,    0)),
#             'E':  ((737, 0, 0, 0.2), (741,   0,    0,    0), (743.1, 0,    0,    0), (743.1, elev, dens, 0), (743.1, elev, dens, 0)),
#             'SE': ((737, 0, 0, 0.3), (743.1, elev, dens, 0), (744,   elev, dens, 0), (744.9, elev, dens, 0), (747.1, elev, dens, 0)),
#             'S':  ((737, 0, 0, 0.4), (743.1, elev, dens, 0), (744,   elev, dens, 0), (747.1, 0,    0,    0), (748,   10,   dens, 0)),
#             'SW': ((737, 0, 0, 0.5), (741,   elev, dens, 0), (742.2, elev, dens, 0), (743.1, 0,    0,    0), (743.1, 0,    0,    0)),
#             'W':  ((737, 0, 0, 0.6), (739.1, 0,    0,    0), (739.1, 0,    0,    0), (737,   elev, dens, 0), (737,   elev, dens, 0)),
#             'NW': ((737, 0, 0, 0.7), (739.1, elev, dens, 0), (737,   elev, dens, 0), (737,   elev, dens, 0), (737,   elev, dens, 0))}
#
#        for dir, tup in node.Zone.iteritems():
#            for i in range(5):
#                self.assertEqual(node.Zone[dir][i], d[dir][i])
#        self.doc.Close()
