'''tzinfo timezone information for Africa/Ouagadougou.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Ouagadougou(DstTzInfo):
    '''Africa/Ouagadougou timezone definition. See datetime.tzinfo for details'''

    zone = 'Africa/Ouagadougou'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1912,1,1,0,6,4),
        ]

    _transition_info = [
i(-360,0,'LMT'),
i(0,0,'GMT'),
        ]

Ouagadougou = Ouagadougou()

