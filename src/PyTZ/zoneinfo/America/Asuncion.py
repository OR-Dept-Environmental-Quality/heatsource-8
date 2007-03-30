'''tzinfo timezone information for America/Asuncion.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Asuncion(DstTzInfo):
    '''America/Asuncion timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Asuncion'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1931,10,10,3,50,40),
d(1972,10,1,4,0,0),
d(1974,4,1,3,0,0),
d(1975,10,1,4,0,0),
d(1976,3,1,3,0,0),
d(1976,10,1,4,0,0),
d(1977,3,1,3,0,0),
d(1977,10,1,4,0,0),
d(1978,3,1,3,0,0),
d(1978,10,1,4,0,0),
d(1979,4,1,3,0,0),
d(1979,10,1,4,0,0),
d(1980,4,1,3,0,0),
d(1980,10,1,4,0,0),
d(1981,4,1,3,0,0),
d(1981,10,1,4,0,0),
d(1982,4,1,3,0,0),
d(1982,10,1,4,0,0),
d(1983,4,1,3,0,0),
d(1983,10,1,4,0,0),
d(1984,4,1,3,0,0),
d(1984,10,1,4,0,0),
d(1985,4,1,3,0,0),
d(1985,10,1,4,0,0),
d(1986,4,1,3,0,0),
d(1986,10,1,4,0,0),
d(1987,4,1,3,0,0),
d(1987,10,1,4,0,0),
d(1988,4,1,3,0,0),
d(1988,10,1,4,0,0),
d(1989,4,1,3,0,0),
d(1989,10,22,4,0,0),
d(1990,4,1,3,0,0),
d(1990,10,1,4,0,0),
d(1991,4,1,3,0,0),
d(1991,10,6,4,0,0),
d(1992,3,1,3,0,0),
d(1992,10,5,4,0,0),
d(1993,3,31,3,0,0),
d(1993,10,1,4,0,0),
d(1994,2,27,3,0,0),
d(1994,10,1,4,0,0),
d(1995,2,26,3,0,0),
d(1995,10,1,4,0,0),
d(1996,3,1,3,0,0),
d(1996,10,6,4,0,0),
d(1997,2,23,3,0,0),
d(1997,10,5,4,0,0),
d(1998,3,1,3,0,0),
d(1998,10,4,4,0,0),
d(1999,3,7,3,0,0),
d(1999,10,3,4,0,0),
d(2000,3,5,3,0,0),
d(2000,10,1,4,0,0),
d(2001,3,4,3,0,0),
d(2001,10,7,4,0,0),
d(2002,4,7,3,0,0),
d(2002,9,1,4,0,0),
d(2003,4,6,3,0,0),
d(2003,9,7,4,0,0),
d(2004,4,4,3,0,0),
d(2004,10,17,4,0,0),
d(2005,3,13,3,0,0),
d(2005,10,16,4,0,0),
d(2006,3,12,3,0,0),
d(2006,10,15,4,0,0),
d(2007,3,11,3,0,0),
d(2007,10,21,4,0,0),
d(2008,3,9,3,0,0),
d(2008,10,19,4,0,0),
d(2009,3,8,3,0,0),
d(2009,10,18,4,0,0),
d(2010,3,14,3,0,0),
d(2010,10,17,4,0,0),
d(2011,3,13,3,0,0),
d(2011,10,16,4,0,0),
d(2012,3,11,3,0,0),
d(2012,10,21,4,0,0),
d(2013,3,10,3,0,0),
d(2013,10,20,4,0,0),
d(2014,3,9,3,0,0),
d(2014,10,19,4,0,0),
d(2015,3,8,3,0,0),
d(2015,10,18,4,0,0),
d(2016,3,13,3,0,0),
d(2016,10,16,4,0,0),
d(2017,3,12,3,0,0),
d(2017,10,15,4,0,0),
d(2018,3,11,3,0,0),
d(2018,10,21,4,0,0),
d(2019,3,10,3,0,0),
d(2019,10,20,4,0,0),
d(2020,3,8,3,0,0),
d(2020,10,18,4,0,0),
d(2021,3,14,3,0,0),
d(2021,10,17,4,0,0),
d(2022,3,13,3,0,0),
d(2022,10,16,4,0,0),
d(2023,3,12,3,0,0),
d(2023,10,15,4,0,0),
d(2024,3,10,3,0,0),
d(2024,10,20,4,0,0),
d(2025,3,9,3,0,0),
d(2025,10,19,4,0,0),
d(2026,3,8,3,0,0),
d(2026,10,18,4,0,0),
d(2027,3,14,3,0,0),
d(2027,10,17,4,0,0),
d(2028,3,12,3,0,0),
d(2028,10,15,4,0,0),
d(2029,3,11,3,0,0),
d(2029,10,21,4,0,0),
d(2030,3,10,3,0,0),
d(2030,10,20,4,0,0),
d(2031,3,9,3,0,0),
d(2031,10,19,4,0,0),
d(2032,3,14,3,0,0),
d(2032,10,17,4,0,0),
d(2033,3,13,3,0,0),
d(2033,10,16,4,0,0),
d(2034,3,12,3,0,0),
d(2034,10,15,4,0,0),
d(2035,3,11,3,0,0),
d(2035,10,21,4,0,0),
d(2036,3,9,3,0,0),
d(2036,10,19,4,0,0),
d(2037,3,8,3,0,0),
d(2037,10,18,4,0,0),
        ]

    _transition_info = [
i(-13860,0,'AMT'),
i(-14400,0,'PYT'),
i(-10800,0,'PYT'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
i(-14400,0,'PYT'),
i(-10800,3600,'PYST'),
        ]

Asuncion = Asuncion()
