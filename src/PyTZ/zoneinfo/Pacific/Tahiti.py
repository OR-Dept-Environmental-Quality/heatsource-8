'''tzinfo timezone information for Pacific/Tahiti.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Tahiti(DstTzInfo):
    '''Pacific/Tahiti timezone definition. See datetime.tzinfo for details'''

    zone = 'Pacific/Tahiti'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1912,10,1,9,58,16),
        ]

    _transition_info = [
i(-35880,0,'LMT'),
i(-36000,0,'TAHT'),
        ]

Tahiti = Tahiti()

