'''tzinfo timezone information for Eire.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Eire(DstTzInfo):
    '''Eire timezone definition. See datetime.tzinfo for details'''

    zone = 'Eire'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1916,5,21,2,25,21),
d(1916,10,1,2,25,21),
d(1917,4,8,2,0,0),
d(1917,9,17,2,0,0),
d(1918,3,24,2,0,0),
d(1918,9,30,2,0,0),
d(1919,3,30,2,0,0),
d(1919,9,29,2,0,0),
d(1920,3,28,2,0,0),
d(1920,10,25,2,0,0),
d(1921,4,3,2,0,0),
d(1921,10,3,2,0,0),
d(1921,12,6,0,0,0),
d(1922,3,26,2,0,0),
d(1922,10,8,2,0,0),
d(1923,4,22,2,0,0),
d(1923,9,16,2,0,0),
d(1924,4,13,2,0,0),
d(1924,9,21,2,0,0),
d(1925,4,19,2,0,0),
d(1925,10,4,2,0,0),
d(1926,4,18,2,0,0),
d(1926,10,3,2,0,0),
d(1927,4,10,2,0,0),
d(1927,10,2,2,0,0),
d(1928,4,22,2,0,0),
d(1928,10,7,2,0,0),
d(1929,4,21,2,0,0),
d(1929,10,6,2,0,0),
d(1930,4,13,2,0,0),
d(1930,10,5,2,0,0),
d(1931,4,19,2,0,0),
d(1931,10,4,2,0,0),
d(1932,4,17,2,0,0),
d(1932,10,2,2,0,0),
d(1933,4,9,2,0,0),
d(1933,10,8,2,0,0),
d(1934,4,22,2,0,0),
d(1934,10,7,2,0,0),
d(1935,4,14,2,0,0),
d(1935,10,6,2,0,0),
d(1936,4,19,2,0,0),
d(1936,10,4,2,0,0),
d(1937,4,18,2,0,0),
d(1937,10,3,2,0,0),
d(1938,4,10,2,0,0),
d(1938,10,2,2,0,0),
d(1939,4,16,2,0,0),
d(1939,11,19,2,0,0),
d(1940,2,25,2,0,0),
d(1946,10,6,1,0,0),
d(1947,3,16,2,0,0),
d(1947,11,2,1,0,0),
d(1948,4,18,2,0,0),
d(1948,10,31,2,0,0),
d(1949,4,3,2,0,0),
d(1949,10,30,2,0,0),
d(1950,4,16,2,0,0),
d(1950,10,22,2,0,0),
d(1951,4,15,2,0,0),
d(1951,10,21,2,0,0),
d(1952,4,20,2,0,0),
d(1952,10,26,2,0,0),
d(1953,4,19,2,0,0),
d(1953,10,4,2,0,0),
d(1954,4,11,2,0,0),
d(1954,10,3,2,0,0),
d(1955,4,17,2,0,0),
d(1955,10,2,2,0,0),
d(1956,4,22,2,0,0),
d(1956,10,7,2,0,0),
d(1957,4,14,2,0,0),
d(1957,10,6,2,0,0),
d(1958,4,20,2,0,0),
d(1958,10,5,2,0,0),
d(1959,4,19,2,0,0),
d(1959,10,4,2,0,0),
d(1960,4,10,2,0,0),
d(1960,10,2,2,0,0),
d(1961,3,26,2,0,0),
d(1961,10,29,2,0,0),
d(1962,3,25,2,0,0),
d(1962,10,28,2,0,0),
d(1963,3,31,2,0,0),
d(1963,10,27,2,0,0),
d(1964,3,22,2,0,0),
d(1964,10,25,2,0,0),
d(1965,3,21,2,0,0),
d(1965,10,24,2,0,0),
d(1966,3,20,2,0,0),
d(1966,10,23,2,0,0),
d(1967,3,19,2,0,0),
d(1967,10,29,2,0,0),
d(1968,2,18,2,0,0),
d(1968,10,26,23,0,0),
d(1971,10,31,2,0,0),
d(1972,3,19,2,0,0),
d(1972,10,29,2,0,0),
d(1973,3,18,2,0,0),
d(1973,10,28,2,0,0),
d(1974,3,17,2,0,0),
d(1974,10,27,2,0,0),
d(1975,3,16,2,0,0),
d(1975,10,26,2,0,0),
d(1976,3,21,2,0,0),
d(1976,10,24,2,0,0),
d(1977,3,20,2,0,0),
d(1977,10,23,2,0,0),
d(1978,3,19,2,0,0),
d(1978,10,29,2,0,0),
d(1979,3,18,2,0,0),
d(1979,10,28,2,0,0),
d(1980,3,16,2,0,0),
d(1980,10,26,2,0,0),
d(1981,3,29,1,0,0),
d(1981,10,25,1,0,0),
d(1982,3,28,1,0,0),
d(1982,10,24,1,0,0),
d(1983,3,27,1,0,0),
d(1983,10,23,1,0,0),
d(1984,3,25,1,0,0),
d(1984,10,28,1,0,0),
d(1985,3,31,1,0,0),
d(1985,10,27,1,0,0),
d(1986,3,30,1,0,0),
d(1986,10,26,1,0,0),
d(1987,3,29,1,0,0),
d(1987,10,25,1,0,0),
d(1988,3,27,1,0,0),
d(1988,10,23,1,0,0),
d(1989,3,26,1,0,0),
d(1989,10,29,1,0,0),
d(1990,3,25,1,0,0),
d(1990,10,28,1,0,0),
d(1991,3,31,1,0,0),
d(1991,10,27,1,0,0),
d(1992,3,29,1,0,0),
d(1992,10,25,1,0,0),
d(1993,3,28,1,0,0),
d(1993,10,24,1,0,0),
d(1994,3,27,1,0,0),
d(1994,10,23,1,0,0),
d(1995,3,26,1,0,0),
d(1995,10,22,1,0,0),
d(1996,1,1,0,0,0),
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
i(-1500,0,'DMT'),
i(2100,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'BST'),
i(0,0,'GMT'),
i(3600,3600,'BST'),
i(0,0,'GMT'),
i(3600,3600,'BST'),
i(0,0,'GMT'),
i(3600,3600,'BST'),
i(0,0,'GMT'),
i(3600,3600,'BST'),
i(0,0,'GMT'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(3600,0,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
i(3600,3600,'IST'),
i(0,0,'GMT'),
        ]

Eire = Eire()

