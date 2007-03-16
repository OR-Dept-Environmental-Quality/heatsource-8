'''tzinfo timezone information for Africa/Bissau.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Bissau(DstTzInfo):
    '''Africa/Bissau timezone definition. See datetime.tzinfo for details'''

    zone = 'Africa/Bissau'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,5,26,1,2,20),
d(1975,1,1,1,0,0),
        ]

    _transition_info = [
i(-3720,0,'LMT'),
i(-3600,0,'WAT'),
i(0,0,'GMT'),
        ]

Bissau = Bissau()

