'''tzinfo timezone information for Asia/Urumqi.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Urumqi(DstTzInfo):
    '''Asia/Urumqi timezone definition. See datetime.tzinfo for details'''

    zone = 'Asia/Urumqi'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1927,12,31,18,9,40),
d(1980,4,30,18,0,0),
d(1986,5,3,16,0,0),
d(1986,9,13,15,0,0),
d(1987,4,11,16,0,0),
d(1987,9,12,15,0,0),
d(1988,4,9,16,0,0),
d(1988,9,10,15,0,0),
d(1989,4,15,16,0,0),
d(1989,9,16,15,0,0),
d(1990,4,14,16,0,0),
d(1990,9,15,15,0,0),
d(1991,4,13,16,0,0),
d(1991,9,14,15,0,0),
        ]

    _transition_info = [
i(21000,0,'LMT'),
i(21600,0,'URUT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
i(32400,3600,'CDT'),
i(28800,0,'CST'),
        ]

Urumqi = Urumqi()

