'''tzinfo timezone information for Africa/Malabo.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Malabo(DstTzInfo):
    '''Africa/Malabo timezone definition. See datetime.tzinfo for details'''

    zone = 'Africa/Malabo'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,12,31,23,24,52),
d(1963,12,15,0,0,0),
        ]

    _transition_info = [
i(2100,0,'LMT'),
i(0,0,'GMT'),
i(3600,0,'WAT'),
        ]

Malabo = Malabo()

