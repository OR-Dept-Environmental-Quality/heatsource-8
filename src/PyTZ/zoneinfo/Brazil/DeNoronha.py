'''tzinfo timezone information for Brazil/DeNoronha.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class DeNoronha(DstTzInfo):
    '''Brazil/DeNoronha timezone definition. See datetime.tzinfo for details'''

    zone = 'Brazil/DeNoronha'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1914,1,1,2,9,40),
d(1931,10,3,13,0,0),
d(1932,4,1,1,0,0),
d(1932,10,3,2,0,0),
d(1933,4,1,1,0,0),
d(1949,12,1,2,0,0),
d(1950,4,16,2,0,0),
d(1950,12,1,2,0,0),
d(1951,4,1,1,0,0),
d(1951,12,1,2,0,0),
d(1952,4,1,1,0,0),
d(1952,12,1,2,0,0),
d(1953,3,1,1,0,0),
d(1963,12,9,2,0,0),
d(1964,3,1,1,0,0),
d(1965,1,31,2,0,0),
d(1965,3,31,1,0,0),
d(1965,12,1,2,0,0),
d(1966,3,1,1,0,0),
d(1966,11,1,2,0,0),
d(1967,3,1,1,0,0),
d(1967,11,1,2,0,0),
d(1968,3,1,1,0,0),
d(1985,11,2,2,0,0),
d(1986,3,15,1,0,0),
d(1986,10,25,2,0,0),
d(1987,2,14,1,0,0),
d(1987,10,25,2,0,0),
d(1988,2,7,1,0,0),
d(1988,10,16,2,0,0),
d(1989,1,29,1,0,0),
d(1989,10,15,2,0,0),
d(1990,2,11,1,0,0),
d(1999,10,3,2,0,0),
d(2000,2,27,1,0,0),
d(2000,10,8,2,0,0),
d(2000,10,15,1,0,0),
d(2001,10,14,2,0,0),
d(2002,2,17,1,0,0),
        ]

    _transition_info = [
i(-7800,0,'LMT'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
i(-3600,3600,'FNST'),
i(-7200,0,'FNT'),
        ]

DeNoronha = DeNoronha()
