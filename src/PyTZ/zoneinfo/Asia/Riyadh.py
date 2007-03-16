'''tzinfo timezone information for Asia/Riyadh.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Riyadh(DstTzInfo):
    '''Asia/Riyadh timezone definition. See datetime.tzinfo for details'''

    zone = 'Asia/Riyadh'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1949,12,31,20,53,8),
        ]

    _transition_info = [
i(11220,0,'LMT'),
i(10800,0,'AST'),
        ]

Riyadh = Riyadh()

