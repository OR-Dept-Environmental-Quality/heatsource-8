'''tzinfo timezone information for America/Montserrat.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Montserrat(DstTzInfo):
    '''America/Montserrat timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Montserrat'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,7,1,4,9,52),
        ]

    _transition_info = [
i(-14940,0,'LMT'),
i(-14400,0,'AST'),
        ]

Montserrat = Montserrat()

