'''tzinfo timezone information for Antarctica/Casey.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Casey(DstTzInfo):
    '''Antarctica/Casey timezone definition. See datetime.tzinfo for details'''

    zone = 'Antarctica/Casey'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1969,1,1,0,0,0),
        ]

    _transition_info = [
i(0,0,'zzz'),
i(28800,0,'WST'),
        ]

Casey = Casey()

