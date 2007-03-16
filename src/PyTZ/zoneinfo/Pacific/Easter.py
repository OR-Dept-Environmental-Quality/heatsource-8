'''tzinfo timezone information for Pacific/Easter.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Easter(DstTzInfo):
    '''Pacific/Easter timezone definition. See datetime.tzinfo for details'''

    zone = 'Pacific/Easter'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1932,9,1,7,17,28),
d(1942,6,1,4,0,0),
d(1942,8,1,5,0,0),
d(1946,9,1,3,0,0),
d(1968,11,3,4,0,0),
d(1969,3,30,3,0,0),
d(1969,11,23,4,0,0),
d(1970,3,29,3,0,0),
d(1970,10,11,4,0,0),
d(1971,3,14,3,0,0),
d(1971,10,10,4,0,0),
d(1972,3,12,3,0,0),
d(1972,10,15,4,0,0),
d(1973,3,11,3,0,0),
d(1973,9,30,4,0,0),
d(1974,3,10,3,0,0),
d(1974,10,13,4,0,0),
d(1975,3,9,3,0,0),
d(1975,10,12,4,0,0),
d(1976,3,14,3,0,0),
d(1976,10,10,4,0,0),
d(1977,3,13,3,0,0),
d(1977,10,9,4,0,0),
d(1978,3,12,3,0,0),
d(1978,10,15,4,0,0),
d(1979,3,11,3,0,0),
d(1979,10,14,4,0,0),
d(1980,3,9,3,0,0),
d(1980,10,12,4,0,0),
d(1981,3,15,3,0,0),
d(1981,10,11,4,0,0),
d(1982,1,19,3,0,0),
d(1982,3,14,3,0,0),
d(1982,10,10,4,0,0),
d(1983,3,13,3,0,0),
d(1983,10,9,4,0,0),
d(1984,3,11,3,0,0),
d(1984,10,14,4,0,0),
d(1985,3,10,3,0,0),
d(1985,10,13,4,0,0),
d(1986,3,9,3,0,0),
d(1986,10,12,4,0,0),
d(1987,4,12,3,0,0),
d(1987,10,11,4,0,0),
d(1988,3,13,3,0,0),
d(1988,10,2,4,0,0),
d(1989,3,12,3,0,0),
d(1989,10,15,4,0,0),
d(1990,3,18,3,0,0),
d(1990,9,16,4,0,0),
d(1991,3,10,3,0,0),
d(1991,10,13,4,0,0),
d(1992,3,15,3,0,0),
d(1992,10,11,4,0,0),
d(1993,3,14,3,0,0),
d(1993,10,10,4,0,0),
d(1994,3,13,3,0,0),
d(1994,10,9,4,0,0),
d(1995,3,12,3,0,0),
d(1995,10,15,4,0,0),
d(1996,3,10,3,0,0),
d(1996,10,13,4,0,0),
d(1997,3,30,3,0,0),
d(1997,10,12,4,0,0),
d(1998,3,15,3,0,0),
d(1998,9,27,4,0,0),
d(1999,4,4,3,0,0),
d(1999,10,10,4,0,0),
d(2000,3,12,3,0,0),
d(2000,10,15,4,0,0),
d(2001,3,11,3,0,0),
d(2001,10,14,4,0,0),
d(2002,3,10,3,0,0),
d(2002,10,13,4,0,0),
d(2003,3,9,3,0,0),
d(2003,10,12,4,0,0),
d(2004,3,14,3,0,0),
d(2004,10,10,4,0,0),
d(2005,3,13,3,0,0),
d(2005,10,9,4,0,0),
d(2006,3,12,3,0,0),
d(2006,10,15,4,0,0),
d(2007,3,11,3,0,0),
d(2007,10,14,4,0,0),
d(2008,3,9,3,0,0),
d(2008,10,12,4,0,0),
d(2009,3,15,3,0,0),
d(2009,10,11,4,0,0),
d(2010,3,14,3,0,0),
d(2010,10,10,4,0,0),
d(2011,3,13,3,0,0),
d(2011,10,9,4,0,0),
d(2012,3,11,3,0,0),
d(2012,10,14,4,0,0),
d(2013,3,10,3,0,0),
d(2013,10,13,4,0,0),
d(2014,3,9,3,0,0),
d(2014,10,12,4,0,0),
d(2015,3,15,3,0,0),
d(2015,10,11,4,0,0),
d(2016,3,13,3,0,0),
d(2016,10,9,4,0,0),
d(2017,3,12,3,0,0),
d(2017,10,15,4,0,0),
d(2018,3,11,3,0,0),
d(2018,10,14,4,0,0),
d(2019,3,10,3,0,0),
d(2019,10,13,4,0,0),
d(2020,3,15,3,0,0),
d(2020,10,11,4,0,0),
d(2021,3,14,3,0,0),
d(2021,10,10,4,0,0),
d(2022,3,13,3,0,0),
d(2022,10,9,4,0,0),
d(2023,3,12,3,0,0),
d(2023,10,15,4,0,0),
d(2024,3,10,3,0,0),
d(2024,10,13,4,0,0),
d(2025,3,9,3,0,0),
d(2025,10,12,4,0,0),
d(2026,3,15,3,0,0),
d(2026,10,11,4,0,0),
d(2027,3,14,3,0,0),
d(2027,10,10,4,0,0),
d(2028,3,12,3,0,0),
d(2028,10,15,4,0,0),
d(2029,3,11,3,0,0),
d(2029,10,14,4,0,0),
d(2030,3,10,3,0,0),
d(2030,10,13,4,0,0),
d(2031,3,9,3,0,0),
d(2031,10,12,4,0,0),
d(2032,3,14,3,0,0),
d(2032,10,10,4,0,0),
d(2033,3,13,3,0,0),
d(2033,10,9,4,0,0),
d(2034,3,12,3,0,0),
d(2034,10,15,4,0,0),
d(2035,3,11,3,0,0),
d(2035,10,14,4,0,0),
d(2036,3,9,3,0,0),
d(2036,10,12,4,0,0),
d(2037,3,15,3,0,0),
d(2037,10,11,4,0,0),
        ]

    _transition_info = [
i(-26220,0,'MMT'),
i(-21600,4620,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-25200,0,'EAST'),
i(-21600,3600,'EASST'),
i(-18000,7200,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
i(-21600,0,'EAST'),
i(-18000,3600,'EASST'),
        ]

Easter = Easter()

