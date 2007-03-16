'''tzinfo timezone information for America/Araguaina.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Araguaina(DstTzInfo):
    '''America/Araguaina timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Araguaina'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1914,1,1,3,12,48),
d(1931,10,3,14,0,0),
d(1932,4,1,2,0,0),
d(1932,10,3,3,0,0),
d(1933,4,1,2,0,0),
d(1949,12,1,3,0,0),
d(1950,4,16,3,0,0),
d(1950,12,1,3,0,0),
d(1951,4,1,2,0,0),
d(1951,12,1,3,0,0),
d(1952,4,1,2,0,0),
d(1952,12,1,3,0,0),
d(1953,3,1,2,0,0),
d(1963,12,9,3,0,0),
d(1964,3,1,2,0,0),
d(1965,1,31,3,0,0),
d(1965,3,31,2,0,0),
d(1965,12,1,3,0,0),
d(1966,3,1,2,0,0),
d(1966,11,1,3,0,0),
d(1967,3,1,2,0,0),
d(1967,11,1,3,0,0),
d(1968,3,1,2,0,0),
d(1985,11,2,3,0,0),
d(1986,3,15,2,0,0),
d(1986,10,25,3,0,0),
d(1987,2,14,2,0,0),
d(1987,10,25,3,0,0),
d(1988,2,7,2,0,0),
d(1988,10,16,3,0,0),
d(1989,1,29,2,0,0),
d(1989,10,15,3,0,0),
d(1990,2,11,2,0,0),
d(1995,10,15,3,0,0),
d(1996,2,11,2,0,0),
d(1996,10,6,3,0,0),
d(1997,2,16,2,0,0),
d(1997,10,6,3,0,0),
d(1998,3,1,2,0,0),
d(1998,10,11,3,0,0),
d(1999,2,21,2,0,0),
d(1999,10,3,3,0,0),
d(2000,2,27,2,0,0),
d(2000,10,8,3,0,0),
d(2001,2,18,2,0,0),
d(2001,10,14,3,0,0),
d(2002,2,17,2,0,0),
d(2002,11,3,3,0,0),
d(2003,2,16,2,0,0),
        ]

    _transition_info = [
i(-11580,0,'LMT'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
i(-7200,3600,'BRST'),
i(-10800,0,'BRT'),
        ]

Araguaina = Araguaina()

