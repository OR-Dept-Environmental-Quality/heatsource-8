from unittest import TestCase
from Utils.VegZone import VegZone
from Utils.Zonator import Zonator
from random import randint, choice
from Utils.Exceptions import HSClassError

class TestZonator(TestCase):
    def setUp(self):
        self.t = t =( (68, 22, 42),
                      (31, 61, 72, 59),
                      (56, 90, 75),
                      (83, 94, 5, 43),
                      (44, 35, 44),
                      (8, 80, 79),
                      (26, 43, 44, 94),
                      (11, 28, 39) )
        self.v = [VegZone(*tup) for tup in t]
            
    def testMethods(self):
        self.assertRaises(HSClassError,Zonator,*self.v)
        self.assertRaises(HSClassError,Zonator,self.v)
        z = Zonator(*self.v[:-1])
        self.assertEqual(len(z),len(self.v[:-1]))
        self.assertEqual(len(z),7)
        
        d = ("NE","E","SE","S","SW","W","NW")
        for i in xrange(1):
            t = self.t[i]
            self.assertEqual(z[d[i]],t)
            
        self.assertEqual(z["NE"],[68, 22, 42])
        self.assertEqual(z.E,(31, 61, 72, 59))
        v = VegZone(26, 43, 44, 94)
        self.assertEqual(z.NW,v)

        self.assertEqual(z["NE"].Elevation, 68)
        self.assertEqual(z.NE["Elevation"],68)
        self.assertEqual(z[0][0],68)