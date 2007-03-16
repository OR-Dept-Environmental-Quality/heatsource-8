'''tzinfo timezone information for Asia/Saigon.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Saigon(DstTzInfo):
    '''Asia/Saigon timezone definition. See datetime.tzinfo for details'''

    zone = 'Asia/Saigon'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1906,6,8,16,53,20),
d(1911,3,10,16,54,40),
d(1912,4,30,17,0,0),
d(1931,4,30,16,0,0),
        ]

    _transition_info = [
i(25620,0,'LMT'),
i(25560,0,'SMT'),
i(25200,0,'ICT'),
i(28800,0,'ICT'),
i(25200,0,'ICT'),
        ]

Saigon = Saigon()

