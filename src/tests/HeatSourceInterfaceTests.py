from __future__ import division
from unittest import TestCase
from Excel.HeatSourceInterface import HeatSourceInterface
from Utils.Time import TimeUtil

class TestDataSheet(TestCase):
    def setUp(self):
        self.doc = HeatSourceInterface("c:\\eclipse\\HeatSource\\Toketee_CCC.xls")
    def tearDown(self):
        del self.doc

#    def test_UpdateQVarCounter(self):
#        """Test ability to count variables"""
#        self.doc.UpdateQVarCounter()
#        self.assertEqual(self.doc.Num_Q_Var,63)
#
#    def test_CheckMorphology(self):
#        """Test ability to check morphology"""
#        # Sort of a dumb method, we should have better checking.
#        self.doc.UpdateQVarCounter()
#        self.doc.CheckMorphologySheet()

#    def test_BasicInputs(self):
#        self.doc.BasicInputs()

    def test_RedimVars(self):
        """Test building of stream nodes"""
        self.doc.UpdateQVarCounter()
        self.doc.RedimVariables()
        self.doc.BasicInputs()
        print len(self.doc.StreamNodeList), self.doc.Nodes
#        node = self.doc.StreamNodeList[0]
#        print "\n"
#        l = (('RiverKM',3.15),
#             ('Slope',0.0012),
#             ('n',0.25),
#             ('Width_BF',8.5),
#             ('Width_B',7.9),
#             ('Depth_BF',0.6),
#             ('Z',0.5),
#             ('X_Weight',0.0),
#             ('Conductivity',30/1000),
#             ('Particle_Size',250),
#             ('Embeddedness',0.2),
#             ('Q_Control',0.3),
#             ('D_Control',0.4),
#             ('Q_Out',0.6),
#             ('Q_Accretion',0.4),
#             ('T_Accretion',0.5),
#             ('FLIR_Temp',11.1),
#             ('T_Control',0.5),
#             ('Longitude',-122.42055784),
#             ('Latitude',43.2632496),
#             ('Aspect',283.8),
#             ('Topo_W',4.2),
#             ('Topo_S',19.5),
#             ('Topo_E',15.1),
#             ('VHeight',0.8),
#             ('VDensity',0.9),
#             ('Elevation',737))
#
#        for attr,val in l:
#            self.assertAlmostEqual(getattr(node,attr),val,5)
#
#        #FLIR_Time
#        l = (('year',2001),('month',07),('day',10),
#             ('hour',14), ('minute',14),('second',0))
#        t = TimeUtil()
#        date = t.MakeDatetime(getattr(node,'FLIR_Time'))
#        for attr,val in l:
#            self.assertAlmostEqual(getattr(date,attr),val,5)
#        # Zones:      0 1 2 3 4
#        elev,dens = 1.5199999809265137, 0.64999997615814209
#        d = {'NE': ((737,None,None,0.1),(741,0,0,None),(741,0,0,None),(740.1,0,0,None),(740.1,0,0,None)),
#             'E':  ((737,None,None,0.2),(741,0,0,None),(743.1,0,0,None),(743.1,elev,dens,None),(743.1,elev,dens,None)),
#             'SE': ((737,None,None,0.3),(743.1,elev,dens,None),(744,elev,dens,None),(744.9,elev,dens,None),(747.1,elev,dens,None)),
#             'S':  ((737,None,None,0.4),(743.1,elev,dens,None),(744,elev,dens,None),(747.1,0,0,None),(748,10,dens,None)),
#             'SW': ((737,None,None,0.5),(741,elev,dens,None),(742.2,elev,dens,None),(743.1,0,0,None),(743.1,0,0,None)),
#             'W':  ((737,None,None,0.6),(739.1,0,0,None),(739.1,0,0,None),(737,elev,dens,None),(737,elev,dens,None)),
#             'NW': ((737,None,None,0.7),(739.1,elev,dens,None),(737,elev,dens,None),(737,elev,dens,None),(737,elev,dens,None))}
#
#        for dir, tup in node.Zone.iteritems():
#            for i in range(5):
#                print dir, i
#                self.assertEqual(node.Zone[dir][i],d[dir][i])
#