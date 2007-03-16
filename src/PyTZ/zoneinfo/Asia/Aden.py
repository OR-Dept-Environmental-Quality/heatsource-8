'''tzinfo timezone information for Asia/Aden.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Aden(DstTzInfo):
    '''Asia/Aden timezone definition. See datetime.tzinfo for details'''

    zone = 'Asia/Aden'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1949,12,31,20,59,12),
        ]

    _transition_info = [
i(10860,0,'LMT'),
i(10800,0,'AST'),
        ]

Aden = Aden()

