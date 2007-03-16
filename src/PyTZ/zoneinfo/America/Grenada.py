'''tzinfo timezone information for America/Grenada.'''
from PyTZ.tzinfo import DstTzInfo
from PyTZ.tzinfo import memorized_datetime as d
from PyTZ.tzinfo import memorized_ttinfo as i

class Grenada(DstTzInfo):
    '''America/Grenada timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Grenada'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,7,1,4,7,0),
        ]

    _transition_info = [
i(-14820,0,'LMT'),
i(-14400,0,'AST'),
        ]

Grenada = Grenada()

