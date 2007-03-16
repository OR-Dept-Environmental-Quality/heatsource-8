'''tzinfo timezone information for Europe/Istanbul.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Istanbul(DstTzInfo):
    '''Europe/Istanbul timezone definition. See datetime.tzinfo for details'''

    zone = 'Europe/Istanbul'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1910,9,30,22,3,4),
d(1916,4,30,22,0,0),
d(1916,9,30,21,0,0),
d(1920,3,27,22,0,0),
d(1920,10,24,21,0,0),
d(1921,4,2,22,0,0),
d(1921,10,2,21,0,0),
d(1922,3,25,22,0,0),
d(1922,10,7,21,0,0),
d(1924,5,12,22,0,0),
d(1924,9,30,21,0,0),
d(1925,4,30,22,0,0),
d(1925,9,30,21,0,0),
d(1940,6,29,22,0,0),
d(1940,10,4,21,0,0),
d(1940,11,30,22,0,0),
d(1941,9,20,21,0,0),
d(1942,3,31,22,0,0),
d(1942,10,31,21,0,0),
d(1945,4,1,22,0,0),
d(1945,10,7,21,0,0),
d(1946,5,31,22,0,0),
d(1946,9,30,21,0,0),
d(1947,4,19,22,0,0),
d(1947,10,4,21,0,0),
d(1948,4,17,22,0,0),
d(1948,10,2,21,0,0),
d(1949,4,9,22,0,0),
d(1949,10,1,21,0,0),
d(1950,4,18,22,0,0),
d(1950,10,7,21,0,0),
d(1951,4,21,22,0,0),
d(1951,10,7,21,0,0),
d(1962,7,14,22,0,0),
d(1962,10,7,21,0,0),
d(1964,5,14,22,0,0),
d(1964,9,30,21,0,0),
d(1970,5,2,22,0,0),
d(1970,10,3,21,0,0),
d(1971,5,1,22,0,0),
d(1971,10,2,21,0,0),
d(1972,5,6,22,0,0),
d(1972,10,7,21,0,0),
d(1973,6,2,23,0,0),
d(1973,11,4,0,0,0),
d(1974,3,31,0,0,0),
d(1974,11,3,2,0,0),
d(1975,3,29,22,0,0),
d(1975,10,25,21,0,0),
d(1976,5,31,22,0,0),
d(1976,10,30,21,0,0),
d(1977,4,2,22,0,0),
d(1977,10,15,21,0,0),
d(1978,4,1,22,0,0),
d(1978,10,14,21,0,0),
d(1979,10,14,20,0,0),
d(1980,4,6,0,0,0),
d(1980,10,12,20,0,0),
d(1981,3,29,0,0,0),
d(1981,10,11,20,0,0),
d(1982,3,28,0,0,0),
d(1982,10,10,20,0,0),
d(1983,7,30,21,0,0),
d(1983,10,1,20,0,0),
d(1985,4,19,21,0,0),
d(1985,9,27,21,0,0),
d(1986,3,30,0,0,0),
d(1986,9,28,0,0,0),
d(1987,3,29,0,0,0),
d(1987,9,27,0,0,0),
d(1988,3,27,0,0,0),
d(1988,9,25,0,0,0),
d(1989,3,26,0,0,0),
d(1989,9,24,0,0,0),
d(1990,3,25,0,0,0),
d(1990,9,30,0,0,0),
d(1990,12,31,22,0,0),
d(1991,3,31,1,0,0),
d(1991,9,29,1,0,0),
d(1992,3,29,1,0,0),
d(1992,9,27,1,0,0),
d(1993,3,28,1,0,0),
d(1993,9,26,1,0,0),
d(1994,3,27,1,0,0),
d(1994,9,25,1,0,0),
d(1995,3,26,1,0,0),
d(1995,9,24,1,0,0),
d(1996,3,31,1,0,0),
d(1996,10,27,1,0,0),
d(1997,3,30,1,0,0),
d(1997,10,26,1,0,0),
d(1998,3,29,1,0,0),
d(1998,10,25,1,0,0),
d(1999,3,28,1,0,0),
d(1999,10,31,1,0,0),
d(2000,3,26,1,0,0),
d(2000,10,29,1,0,0),
d(2001,3,25,1,0,0),
d(2001,10,28,1,0,0),
d(2002,3,31,1,0,0),
d(2002,10,27,1,0,0),
d(2003,3,30,1,0,0),
d(2003,10,26,1,0,0),
d(2004,3,28,1,0,0),
d(2004,10,31,1,0,0),
d(2005,3,27,1,0,0),
d(2005,10,30,1,0,0),
d(2006,3,26,1,0,0),
d(2006,10,29,1,0,0),
d(2007,3,25,1,0,0),
d(2007,10,28,1,0,0),
d(2008,3,30,1,0,0),
d(2008,10,26,1,0,0),
d(2009,3,29,1,0,0),
d(2009,10,25,1,0,0),
d(2010,3,28,1,0,0),
d(2010,10,31,1,0,0),
d(2011,3,27,1,0,0),
d(2011,10,30,1,0,0),
d(2012,3,25,1,0,0),
d(2012,10,28,1,0,0),
d(2013,3,31,1,0,0),
d(2013,10,27,1,0,0),
d(2014,3,30,1,0,0),
d(2014,10,26,1,0,0),
d(2015,3,29,1,0,0),
d(2015,10,25,1,0,0),
d(2016,3,27,1,0,0),
d(2016,10,30,1,0,0),
d(2017,3,26,1,0,0),
d(2017,10,29,1,0,0),
d(2018,3,25,1,0,0),
d(2018,10,28,1,0,0),
d(2019,3,31,1,0,0),
d(2019,10,27,1,0,0),
d(2020,3,29,1,0,0),
d(2020,10,25,1,0,0),
d(2021,3,28,1,0,0),
d(2021,10,31,1,0,0),
d(2022,3,27,1,0,0),
d(2022,10,30,1,0,0),
d(2023,3,26,1,0,0),
d(2023,10,29,1,0,0),
d(2024,3,31,1,0,0),
d(2024,10,27,1,0,0),
d(2025,3,30,1,0,0),
d(2025,10,26,1,0,0),
d(2026,3,29,1,0,0),
d(2026,10,25,1,0,0),
d(2027,3,28,1,0,0),
d(2027,10,31,1,0,0),
d(2028,3,26,1,0,0),
d(2028,10,29,1,0,0),
d(2029,3,25,1,0,0),
d(2029,10,28,1,0,0),
d(2030,3,31,1,0,0),
d(2030,10,27,1,0,0),
d(2031,3,30,1,0,0),
d(2031,10,26,1,0,0),
d(2032,3,28,1,0,0),
d(2032,10,31,1,0,0),
d(2033,3,27,1,0,0),
d(2033,10,30,1,0,0),
d(2034,3,26,1,0,0),
d(2034,10,29,1,0,0),
d(2035,3,25,1,0,0),
d(2035,10,28,1,0,0),
d(2036,3,30,1,0,0),
d(2036,10,26,1,0,0),
d(2037,3,29,1,0,0),
d(2037,10,25,1,0,0),
        ]

    _transition_info = [
i(7020,0,'IMT'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(14400,7200,'TRST'),
i(10800,0,'TRT'),
i(14400,3600,'TRST'),
i(10800,0,'TRT'),
i(14400,3600,'TRST'),
i(10800,0,'TRT'),
i(14400,3600,'TRST'),
i(10800,0,'TRT'),
i(14400,3600,'TRST'),
i(10800,0,'TRT'),
i(10800,0,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
i(10800,3600,'EEST'),
i(7200,0,'EET'),
        ]

Istanbul = Istanbul()

