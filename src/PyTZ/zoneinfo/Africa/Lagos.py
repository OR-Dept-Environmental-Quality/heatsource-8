'''tzinfo timezone information for Africa/Lagos.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Lagos(DstTzInfo):
    '''Africa/Lagos timezone definition. See datetime.tzinfo for details'''

    zone = 'Africa/Lagos'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1919,8,31,23,46,24),
        ]

    _transition_info = [
i(840,0,'LMT'),
i(3600,0,'WAT'),
        ]

Lagos = Lagos()

