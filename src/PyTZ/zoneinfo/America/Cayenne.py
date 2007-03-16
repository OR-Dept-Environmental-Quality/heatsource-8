'''tzinfo timezone information for America/Cayenne.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Cayenne(DstTzInfo):
    '''America/Cayenne timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Cayenne'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,7,1,3,29,20),
d(1967,10,1,4,0,0),
        ]

    _transition_info = [
i(-12540,0,'LMT'),
i(-14400,0,'GFT'),
i(-10800,0,'GFT'),
        ]

Cayenne = Cayenne()

