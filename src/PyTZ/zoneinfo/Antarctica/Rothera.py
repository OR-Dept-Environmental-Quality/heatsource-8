'''tzinfo timezone information for Antarctica/Rothera.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Rothera(DstTzInfo):
    '''Antarctica/Rothera timezone definition. See datetime.tzinfo for details'''

    zone = 'Antarctica/Rothera'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1976,12,1,0,0,0),
        ]

    _transition_info = [
i(0,0,'zzz'),
i(-10800,0,'ROTT'),
        ]

Rothera = Rothera()

