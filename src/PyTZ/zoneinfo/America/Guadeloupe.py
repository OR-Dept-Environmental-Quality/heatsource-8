'''tzinfo timezone information for America/Guadeloupe.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Guadeloupe(DstTzInfo):
    '''America/Guadeloupe timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Guadeloupe'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,6,8,4,6,8),
        ]

    _transition_info = [
i(-14760,0,'LMT'),
i(-14400,0,'AST'),
        ]

Guadeloupe = Guadeloupe()

