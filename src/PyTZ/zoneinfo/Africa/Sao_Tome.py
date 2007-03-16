'''tzinfo timezone information for Africa/Sao_Tome.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Sao_Tome(DstTzInfo):
    '''Africa/Sao_Tome timezone definition. See datetime.tzinfo for details'''

    zone = 'Africa/Sao_Tome'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1912,1,1,0,36,32),
        ]

    _transition_info = [
i(-2220,0,'LMT'),
i(0,0,'GMT'),
        ]

Sao_Tome = Sao_Tome()

