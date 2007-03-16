'''tzinfo timezone information for Antarctica/Syowa.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Syowa(DstTzInfo):
    '''Antarctica/Syowa timezone definition. See datetime.tzinfo for details'''

    zone = 'Antarctica/Syowa'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1957,1,29,0,0,0),
        ]

    _transition_info = [
i(0,0,'zzz'),
i(10800,0,'SYOT'),
        ]

Syowa = Syowa()

