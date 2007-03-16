'''tzinfo timezone information for America/Indianapolis.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Indianapolis(DstTzInfo):
    '''America/Indianapolis timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Indianapolis'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1918,3,31,8,0,0),
d(1918,10,27,7,0,0),
d(1919,3,30,8,0,0),
d(1919,10,26,7,0,0),
d(1941,6,22,8,0,0),
d(1941,9,28,7,0,0),
d(1942,2,9,8,0,0),
d(1945,8,14,23,0,0),
d(1945,9,30,7,0,0),
d(1946,4,28,8,0,0),
d(1946,9,29,7,0,0),
d(1947,4,27,8,0,0),
d(1947,9,28,7,0,0),
d(1948,4,25,8,0,0),
d(1948,9,26,7,0,0),
d(1949,4,24,8,0,0),
d(1949,9,25,7,0,0),
d(1950,4,30,8,0,0),
d(1950,9,24,7,0,0),
d(1951,4,29,8,0,0),
d(1951,9,30,7,0,0),
d(1952,4,27,8,0,0),
d(1952,9,28,7,0,0),
d(1953,4,26,8,0,0),
d(1953,9,27,7,0,0),
d(1954,4,25,8,0,0),
d(1954,9,26,7,0,0),
d(1955,4,24,8,0,0),
d(1957,9,29,7,0,0),
d(1958,4,27,8,0,0),
d(1969,4,27,7,0,0),
d(1969,10,26,6,0,0),
d(1970,4,26,7,0,0),
d(1970,10,25,6,0,0),
d(2006,4,2,7,0,0),
d(2006,10,29,6,0,0),
d(2007,3,11,7,0,0),
d(2007,11,4,6,0,0),
d(2008,3,9,7,0,0),
d(2008,11,2,6,0,0),
d(2009,3,8,7,0,0),
d(2009,11,1,6,0,0),
d(2010,3,14,7,0,0),
d(2010,11,7,6,0,0),
d(2011,3,13,7,0,0),
d(2011,11,6,6,0,0),
d(2012,3,11,7,0,0),
d(2012,11,4,6,0,0),
d(2013,3,10,7,0,0),
d(2013,11,3,6,0,0),
d(2014,3,9,7,0,0),
d(2014,11,2,6,0,0),
d(2015,3,8,7,0,0),
d(2015,11,1,6,0,0),
d(2016,3,13,7,0,0),
d(2016,11,6,6,0,0),
d(2017,3,12,7,0,0),
d(2017,11,5,6,0,0),
d(2018,3,11,7,0,0),
d(2018,11,4,6,0,0),
d(2019,3,10,7,0,0),
d(2019,11,3,6,0,0),
d(2020,3,8,7,0,0),
d(2020,11,1,6,0,0),
d(2021,3,14,7,0,0),
d(2021,11,7,6,0,0),
d(2022,3,13,7,0,0),
d(2022,11,6,6,0,0),
d(2023,3,12,7,0,0),
d(2023,11,5,6,0,0),
d(2024,3,10,7,0,0),
d(2024,11,3,6,0,0),
d(2025,3,9,7,0,0),
d(2025,11,2,6,0,0),
d(2026,3,8,7,0,0),
d(2026,11,1,6,0,0),
d(2027,3,14,7,0,0),
d(2027,11,7,6,0,0),
d(2028,3,12,7,0,0),
d(2028,11,5,6,0,0),
d(2029,3,11,7,0,0),
d(2029,11,4,6,0,0),
d(2030,3,10,7,0,0),
d(2030,11,3,6,0,0),
d(2031,3,9,7,0,0),
d(2031,11,2,6,0,0),
d(2032,3,14,7,0,0),
d(2032,11,7,6,0,0),
d(2033,3,13,7,0,0),
d(2033,11,6,6,0,0),
d(2034,3,12,7,0,0),
d(2034,11,5,6,0,0),
d(2035,3,11,7,0,0),
d(2035,11,4,6,0,0),
d(2036,3,9,7,0,0),
d(2036,11,2,6,0,0),
d(2037,3,8,7,0,0),
d(2037,11,1,6,0,0),
        ]

    _transition_info = [
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CWT'),
i(-18000,3600,'CPT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,0,'EST'),
i(-21600,0,'CST'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
        ]

Indianapolis = Indianapolis()

