'''tzinfo timezone information for Indian/Kerguelen.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Kerguelen(DstTzInfo):
    '''Indian/Kerguelen timezone definition. See datetime.tzinfo for details'''

    zone = 'Indian/Kerguelen'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1950,1,1,0,0,0),
        ]

    _transition_info = [
i(0,0,'zzz'),
i(18000,0,'TFT'),
        ]

Kerguelen = Kerguelen()

